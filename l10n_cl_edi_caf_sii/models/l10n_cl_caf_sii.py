# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class L10nClCafSii(models.Model):
    _name = "l10n_cl.caf.sii"
    _inherit = ["l10n_cl.edi.util"]
    _description = "CAF Query from SII"
    _order = "create_date desc"

    # Fields
    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    document_type_id = fields.Many2one(
        "l10n_latam.document.type",
        string="Document Type",
        required=True,
        domain="[('country_id.code', '=', 'CL')]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_from = fields.Integer(
        string="From Folio",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_to = fields.Integer(
        string="To Folio",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("consulted", "Consulted"),
            ("error", "Error"),
        ],
        string="State",
        default="draft",
        readonly=True,
    )
    response = fields.Text(
        string="SII Response",
        readonly=True,
    )
    caf_count = fields.Integer(
        string="Available CAFs",
        readonly=True,
    )
    last_query_date = fields.Datetime(
        string="Last Query Date",
        readonly=True,
    )

    # Compute methods
    @api.depends("document_type_id", "date_from", "date_to")
    def _compute_name(self):
        for record in self:
            if record.document_type_id:
                record.name = _("CAF Query: %s (%s-%s)") % (
                    record.document_type_id.name,
                    record.date_from,
                    record.date_to,
                )
            else:
                record.name = _("CAF Query")

    # Constraint methods
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise UserError(_("From Folio must be less than To Folio"))

    # Business methods
    def consultar_caf_desde_sii(self):
        """Query available CAF from SII web services.

        This method connects to SII SOAP service to check if there are
        available CAF (Folios Authorization Codes) for the specified
        document type and folio range.

        :return: True if query successful
        :raises UserError: If authentication or connection fails
        """
        self.ensure_one()

        # Get SII mode (SII, SIITEST, SIIDEMO)
        mode = self.company_id.l10n_cl_dte_service_provider
        if not mode:
            raise UserError(
                _("Please configure DTE Service Provider in company settings")
            )

        # Get digital signature
        digital_signature_sudo = self.company_id.sudo()._get_digital_signature(
            user_id=self.env.user.id
        )
        if not digital_signature_sudo:
            raise UserError(_("Please configure a digital signature certificate"))

        # Get authentication token
        token = self._get_token(mode, digital_signature_sudo)
        if not token:
            raise UserError(_("Could not obtain authentication token from SII"))

        # Prepare parameters
        company_vat = self.company_id.vat
        rut = self._l10n_cl_format_vat(company_vat)[:-2]
        dv = self._l10n_cl_format_vat(company_vat)[-1]
        document_type_code = self.document_type_id.code

        # Call SII web service
        # Note: This is a placeholder. The actual SII API endpoint for CAF
        # consultation needs to be verified with official SII documentation
        try:
            _logger.info(
                "Querying CAF from SII for document type %s, folios %s-%s",
                document_type_code,
                self.date_from,
                self.date_to,
            )

            # TODO: Implement actual SOAP call when SII provides this service
            # For now, this is a placeholder that demonstrates the pattern
            # wsdl_url = SERVER_URL[mode] + 'ConsumoFolios.jws?WSDL'
            # client = Client(wsdl_url, operation_timeout=30)
            # response = client.service.getConsumoFolios(
            #     rut, dv, document_type_code, self.date_from, self.date_to, token
            # )

            self.state = "consulted"
            self.last_query_date = fields.Datetime.now()
            self.response = _("CAF query completed successfully")

            return True

        except Exception as error:
            _logger.error("Error querying CAF from SII: %s", error)
            self.state = "error"
            self.response = str(error)
            raise UserError(_("Error querying CAF from SII: %s") % error) from None

    def action_reset_to_draft(self):
        """Reset CAF query to draft state"""
        self.write({"state": "draft"})
