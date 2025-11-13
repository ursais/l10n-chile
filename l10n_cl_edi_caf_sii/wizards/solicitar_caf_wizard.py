# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SolicitarCafWizard(models.TransientModel):
    _name = "solicitar.caf.wizard"
    _description = "Request CAF from SII Wizard"

    # Fields
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    document_type_id = fields.Many2one(
        "l10n_latam.document.type",
        string="Document Type",
        required=True,
        domain="[('country_id.code', '=', 'CL')]",
    )
    from_folio = fields.Integer(
        string="From Folio",
        required=True,
        default=1,
    )
    to_folio = fields.Integer(
        string="To Folio",
        required=True,
        default=100,
    )

    # Constraint methods
    @api.constrains("from_folio", "to_folio")
    def _check_folios(self):
        for wizard in self:
            if wizard.from_folio > wizard.to_folio:
                raise UserError(_("From Folio must be less than To Folio"))
            if wizard.from_folio < 1:
                raise UserError(_("From Folio must be greater than 0"))

    # Action methods
    def action_query_caf(self):
        """Query CAF availability from SII"""
        self.ensure_one()

        # Create CAF query record
        caf_query = self.env["l10n_cl.caf.sii"].create(
            {
                "company_id": self.company_id.id,
                "document_type_id": self.document_type_id.id,
                "date_from": self.from_folio,
                "date_to": self.to_folio,
            }
        )

        # Execute query
        try:
            caf_query.consultar_caf_desde_sii()

            return {
                "type": "ir.actions.act_window",
                "name": _("CAF Query Result"),
                "res_model": "l10n_cl.caf.sii",
                "res_id": caf_query.id,
                "view_mode": "form",
                "target": "current",
            }
        except Exception as error:
            raise UserError(_("Error querying CAF from SII: %s") % error) from None
