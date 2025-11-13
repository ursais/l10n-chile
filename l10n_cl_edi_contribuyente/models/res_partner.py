# Standard library imports
import logging
import re

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Fields
    l10n_cl_sii_taxpayer_verified = fields.Boolean(
        string="SII Verified",
        readonly=True,
        help="Indicates if this taxpayer has been verified with SII",
    )
    l10n_cl_sii_verification_date = fields.Datetime(
        string="SII Verification Date",
        readonly=True,
    )
    l10n_cl_sii_taxpayer_activities = fields.Text(
        string="Economic Activities (SII)",
        readonly=True,
        help="Economic activities registered in SII",
    )
    l10n_cl_sii_taxpayer_status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
        ],
        string="SII Status",
        readonly=True,
    )

    # Business methods
    def action_validate_rut_with_sii(self):
        """Validate RUT with SII and update partner data.

        This method connects to SII services to validate the Chilean RUT
        and retrieve taxpayer information.

        :return: Action to show result
        :raises UserError: If validation fails
        """
        self.ensure_one()

        if not self.vat:
            raise UserError(_("Partner must have a VAT/RUT number"))

        if self.country_id.code != "CL":
            raise UserError(_("RUT validation is only for Chilean partners"))

        # Call validation service
        contribuyente_model = self.env["l10n_cl.contribuyente"]
        result = contribuyente_model.validar_rut_en_sii(self.vat)

        if result.get("valid"):
            self.write(
                {
                    "l10n_cl_sii_taxpayer_verified": True,
                    "l10n_cl_sii_verification_date": fields.Datetime.now(),
                    "l10n_cl_sii_taxpayer_status": result.get("status", "active"),
                    "l10n_cl_sii_taxpayer_activities": result.get("activities", ""),
                }
            )

            # Auto-complete partner data if available
            if result.get("name") and not self.name:
                self.name = result.get("name")

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("RUT Validated"),
                    "message": _("RUT %s has been validated with SII") % self.vat,
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            raise UserError(
                _("Could not validate RUT %s with SII: %s")
                % (self.vat, result.get("error", "Unknown error"))
            )

    @api.constrains("vat", "country_id")
    def _check_vat_cl(self):
        """Enhanced VAT validation for Chilean RUT"""
        for partner in self:
            if partner.country_id.code == "CL" and partner.vat:
                if not self._validate_rut_format(partner.vat):
                    raise ValidationError(
                        _("Invalid Chilean RUT format. Expected format: 12345678-9")
                    )

    def _validate_rut_format(self, vat):
        """Validate Chilean RUT format.

        :param vat: VAT/RUT string
        :return: True if valid format
        """
        if not vat:
            return False

        # Remove 'CL' prefix if present
        rut = vat.replace("CL", "").replace("cl", "")

        # Check format: 12345678-9 or 12.345.678-9
        pattern = r"^\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]$"
        if not re.match(pattern, rut):
            return False

        # Validate check digit
        return self._validate_rut_check_digit(rut)

    def _validate_rut_check_digit(self, rut):
        """Validate Chilean RUT check digit.

        :param rut: RUT string (with or without dots)
        :return: True if check digit is valid
        """
        # Remove dots and split
        rut_clean = rut.replace(".", "")
        parts = rut_clean.split("-")
        if len(parts) != 2:
            return False

        number = parts[0]
        check_digit = parts[1].upper()

        # Calculate check digit
        reversed_digits = map(int, reversed(number))
        factors = [2, 3, 4, 5, 6, 7]
        s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
        calculated_digit = 11 - (s % 11)

        if calculated_digit == 11:
            calculated_digit = "0"
        elif calculated_digit == 10:
            calculated_digit = "K"
        else:
            calculated_digit = str(calculated_digit)

        return check_digit == calculated_digit
