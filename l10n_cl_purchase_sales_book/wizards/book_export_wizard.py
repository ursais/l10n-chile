# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BookExportWizard(models.TransientModel):
    _name = "book.export.wizard"
    _description = "Export Purchase/Sales Book Wizard"

    # Fields
    book_type = fields.Selection(
        [
            ("purchase", "Purchase Book"),
            ("sales", "Sales Book"),
        ],
        string="Book Type",
        required=True,
        default="purchase",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    date_from = fields.Date(
        string="From Date",
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string="To Date",
        required=True,
        default=fields.Date.context_today,
    )
    export_format = fields.Selection(
        [
            ("xml", "XML (SII Format)"),
            ("pdf", "PDF Report"),
        ],
        string="Export Format",
        required=True,
        default="xml",
    )

    # Constraint methods
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_("From Date must be before To Date"))

    # Action methods
    def action_export(self):
        """Export book in selected format"""
        self.ensure_one()

        # Create or get existing book
        if self.book_type == "purchase":
            book_model = self.env["account.purchase.book"]
        else:
            book_model = self.env["account.sales.book"]

        book = book_model.create(
            {
                "company_id": self.company_id.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )

        # Generate book
        book.action_generate()

        # Export in requested format
        if self.export_format == "xml":
            return book.action_export_xml()
        else:
            # Return PDF report action
            return self.env.ref(
                f"l10n_cl_purchase_sales_book.{self.book_type}_book_report"
            ).report_action(book)
