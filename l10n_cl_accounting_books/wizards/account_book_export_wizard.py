# Standard library imports
import base64

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountBookExportWizard(models.TransientModel):
    _name = "account.book.export.wizard"
    _description = "Accounting Book Export Wizard"

    book_type = fields.Selection(
        [
            ("journal", "Journal Book"),
            ("ledger", "Ledger Book"),
            ("inventory", "Inventory Book"),
        ],
        string="Book Type",
        required=True,
    )

    journal_book_id = fields.Many2one(
        "account.journal.book",
        string="Journal Book",
    )
    ledger_book_id = fields.Many2one(
        "account.ledger.book",
        string="Ledger Book",
    )
    inventory_book_id = fields.Many2one(
        "account.inventory.book",
        string="Inventory Book",
    )

    file_name = fields.Char(
        string="File Name",
        compute="_compute_file_name",
    )
    file_data = fields.Binary(
        string="XML File",
        readonly=True,
    )

    @api.depends("book_type", "journal_book_id", "ledger_book_id", "inventory_book_id")
    def _compute_file_name(self):
        for record in self:
            if record.book_type == "journal" and record.journal_book_id:
                record.file_name = (
                    "libro_diario_%s.xml"
                    % record.journal_book_id.date_from.strftime("%Y%m")
                )
            elif record.book_type == "ledger" and record.ledger_book_id:
                record.file_name = (
                    "libro_mayor_%s.xml"
                    % record.ledger_book_id.date_from.strftime("%Y%m")
                )
            elif record.book_type == "inventory" and record.inventory_book_id:
                record.file_name = (
                    "libro_inventario_%s.xml"
                    % record.inventory_book_id.date_from.strftime("%Y%m")
                )
            else:
                record.file_name = "libro_contable.xml"

    def action_export(self):
        """Export book to XML"""
        self.ensure_one()

        export_model = self.env["account.book.export"]
        xml_content = False

        if self.book_type == "journal" and self.journal_book_id:
            xml_content = export_model.generate_journal_book_xml(self.journal_book_id)
            self.journal_book_id.state = "exported"
        elif self.book_type == "ledger" and self.ledger_book_id:
            xml_content = export_model.generate_ledger_book_xml(self.ledger_book_id)
            self.ledger_book_id.state = "exported"
        elif self.book_type == "inventory" and self.inventory_book_id:
            xml_content = export_model.generate_inventory_book_xml(
                self.inventory_book_id
            )
            self.inventory_book_id.state = "exported"
        else:
            raise UserError(_("Please select a book to export"))

        if not xml_content:
            raise UserError(_("Error generating XML file"))

        # Create attachment
        self.file_data = base64.b64encode(xml_content)

        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s/file_data/%s?download=1"
            % (self.id, self.file_name),
            "target": "self",
        }
