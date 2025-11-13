# Standard library imports
import logging

# Imports of odoo
from odoo import fields, models

_logger = logging.getLogger(__name__)


class L10nClDteCaf(models.Model):
    _inherit = "l10n_cl.dte.caf"

    # Add field to track CAF usage
    used_folios_count = fields.Integer(
        string="Used Folios",
        compute="_compute_used_folios_count",
        store=False,
    )
    available_folios_count = fields.Integer(
        string="Available Folios",
        compute="_compute_available_folios_count",
        store=False,
    )

    def _compute_used_folios_count(self):
        """Compute number of folios already used"""
        for caf in self:
            if caf.status != "in_use":
                caf.used_folios_count = caf.final_nb - caf.start_nb + 1
                continue

            # Count used folios from invoices
            move_model = self.env["account.move"]
            used_count = move_model.search_count(
                [
                    ("company_id", "=", caf.company_id.id),
                    (
                        "l10n_latam_document_type_id",
                        "=",
                        caf.l10n_latam_document_type_id.id,
                    ),
                    ("l10n_latam_document_number", ">=", str(caf.start_nb)),
                    ("l10n_latam_document_number", "<=", str(caf.final_nb)),
                    ("state", "=", "posted"),
                ]
            )
            caf.used_folios_count = used_count

    def _compute_available_folios_count(self):
        """Compute number of folios still available"""
        for caf in self:
            total_folios = caf.final_nb - caf.start_nb + 1
            caf.available_folios_count = total_folios - caf.used_folios_count
