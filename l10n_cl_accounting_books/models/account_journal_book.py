# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountJournalBook(models.Model):
    _name = "account.journal.book"
    _description = "Chilean Journal Book (Libro Diario)"
    _order = "date_from desc, date_to desc"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        required=True,
        compute="_compute_name",
        store=True,
        readonly=True,
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
    )
    date_to = fields.Date(
        string="To Date",
        required=True,
    )
    journal_ids = fields.Many2many(
        "account.journal",
        string="Journals",
        help="Leave empty to include all journals",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
            ("exported", "Exported"),
        ],
        string="State",
        default="draft",
        readonly=True,
        copy=False,
    )

    line_ids = fields.One2many(
        "account.journal.book.line",
        "book_id",
        string="Lines",
        readonly=True,
    )

    total_debit = fields.Monetary(
        string="Total Debit",
        compute="_compute_totals",
        currency_field="company_currency_id",
        store=True,
    )
    total_credit = fields.Monetary(
        string="Total Credit",
        compute="_compute_totals",
        currency_field="company_currency_id",
        store=True,
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        store=False,
    )
    line_count = fields.Integer(
        string="Line Count",
        compute="_compute_line_count",
    )

    @api.depends("date_from", "date_to", "company_id")
    def _compute_name(self):
        for record in self:
            if record.date_from and record.date_to:
                record.name = _("Journal Book %s - %s") % (
                    record.date_from.strftime("%Y-%m-%d"),
                    record.date_to.strftime("%Y-%m-%d"),
                )
            else:
                record.name = _("New Journal Book")

    @api.depends("line_ids.debit", "line_ids.credit")
    def _compute_totals(self):
        for record in self:
            record.total_debit = sum(record.line_ids.mapped("debit"))
            record.total_credit = sum(record.line_ids.mapped("credit"))

    @api.depends("line_ids")
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_("From date must be before To date"))

    def action_generate(self):
        """Generate journal book lines from accounting entries"""
        self.ensure_one()

        if self.state != "draft":
            raise UserError(_("You can only generate from draft state"))

        # Validate dates
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set From Date and To Date"))

        if self.date_from > self.date_to:
            raise UserError(_("From date must be before To date"))

        # Prepare domain
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("state", "=", "posted"),
        ]

        if self.journal_ids:
            domain.append(("journal_id", "in", self.journal_ids.ids))

        # Get moves
        moves = self.env["account.move"].search(domain, order="date, name, id")

        if not moves:
            raise UserError(_("No accounting entries found for the selected period"))

        # Clear existing lines
        self.line_ids.unlink()

        # Generate lines
        sequence = 1
        lines_to_create = []

        for move in moves:
            for line in move.line_ids:
                lines_to_create.append(
                    {
                        "book_id": self.id,
                        "sequence": sequence,
                        "date": move.date,
                        "journal_id": move.journal_id.id,
                        "journal_code": move.journal_id.code,
                        "move_id": move.id,
                        "move_name": move.name,
                        "account_id": line.account_id.id,
                        "account_code": line.account_id.code,
                        "partner_id": line.partner_id.id if line.partner_id else False,
                        "partner_vat": line.partner_id.vat
                        if line.partner_id
                        else False,
                        "name": line.name or "/",
                        "debit": line.debit,
                        "credit": line.credit,
                    }
                )
                sequence += 1

        # Create lines in batch
        # Use sudo() to bypass ACLs since this is called from action_generate()
        # which is a method on the book itself, not on the lines
        if lines_to_create:
            self.env["account.journal.book.line"].sudo().create(lines_to_create)

        self.state = "generated"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Journal book generated successfully with %s lines")
                % len(lines_to_create),
                "type": "success",
                "sticky": False,
            },
        }

    def action_export_xml(self):
        """Export journal book to XML format for SII"""
        self.ensure_one()
        if self.state != "generated":
            raise UserError(_("Please generate the book first"))

        wizard = self.env["account.book.export.wizard"].create(
            {
                "book_type": "journal",
                "journal_book_id": self.id,
            }
        )
        return {
            "name": _("Export Journal Book"),
            "type": "ir.actions.act_window",
            "res_model": "account.book.export.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_reset_to_draft(self):
        """Reset book to draft state"""
        self.ensure_one()
        if self.state == "exported":
            raise UserError(_("Cannot reset exported book"))
        self.line_ids.unlink()
        self.state = "draft"

    def action_view_lines(self):
        """Open lines view"""
        self.ensure_one()
        return {
            "name": _("Journal Book Lines"),
            "type": "ir.actions.act_window",
            "res_model": "account.journal.book.line",
            "view_mode": "list,form",
            "domain": [("book_id", "=", self.id)],
            "context": {"default_book_id": self.id},
        }
