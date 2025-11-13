# Standard library imports
import logging

# Imports of odoo
from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EnviarLibroSiiWizard(models.TransientModel):
    _name = "enviar.libro.sii.wizard"
    _description = "Send Book to SII Wizard"

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
    book_id = fields.Many2one(
        "account.purchase.book",
        string="Purchase Book",
    )
    sales_book_id = fields.Many2one(
        "account.sales.book",
        string="Sales Book",
    )

    # Action methods
    def action_send_to_sii(self):
        """Send selected book to SII"""
        self.ensure_one()

        if self.book_type == "purchase" and self.book_id:
            return self.book_id.action_send_to_sii()
        elif self.book_type == "sales" and self.sales_book_id:
            return self.sales_book_id.action_send_to_sii()
        else:
            raise UserError(_("Please select a book to send"))
