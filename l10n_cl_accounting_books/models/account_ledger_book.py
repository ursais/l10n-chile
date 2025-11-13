# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountLedgerBook(models.Model):
    _name = "account.ledger.book"
    _description = "Chilean Ledger Book (Libro Mayor)"
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
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_from = fields.Date(
        string="From Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_to = fields.Date(
        string="To Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    account_ids = fields.Many2many(
        "account.account",
        string="Accounts",
        help="Leave empty to include all accounts",
        readonly=True,
        states={"draft": [("readonly", False)]},
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
        "account.ledger.book.line",
        "book_id",
        string="Lines",
        readonly=True,
    )

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    account_count = fields.Integer(
        string="Account Count",
        compute="_compute_account_count",
    )

    @api.depends("date_from", "date_to", "company_id")
    def _compute_name(self):
        for record in self:
            if record.date_from and record.date_to:
                record.name = _("Ledger Book %s - %s") % (
                    record.date_from.strftime("%Y-%m-%d"),
                    record.date_to.strftime("%Y-%m-%d"),
                )
            else:
                record.name = _("New Ledger Book")

    @api.depends("line_ids.account_id")
    def _compute_account_count(self):
        for record in self:
            record.account_count = len(record.line_ids.mapped("account_id"))

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_("From date must be before To date"))

    def action_generate(self):
        """Generate ledger book lines grouped by account"""
        self.ensure_one()

        if self.state != "draft":
            raise UserError(_("You can only generate from draft state"))

        if not self.date_from or not self.date_to:
            raise UserError(_("Please set From Date and To Date"))

        if self.date_from > self.date_to:
            raise UserError(_("From date must be before To date"))

        # Prepare domain
        domain = [
            ("company_id", "=", self.company_id.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("move_id.state", "=", "posted"),
        ]

        if self.account_ids:
            domain.append(("account_id", "in", self.account_ids.ids))

        # Get account move lines
        aml = self.env["account.move.line"].search(domain, order="account_id, date, id")

        if not aml:
            raise UserError(_("No accounting entries found for the selected period"))

        # Clear existing lines
        self.line_ids.unlink()

        # Group by account and generate lines
        lines_to_create = []
        account_data = {}

        for line in aml:
            account_id = line.account_id.id
            if account_id not in account_data:
                account_data[account_id] = {
                    "account_id": account_id,
                    "account_code": line.account_id.code,
                    "account_name": line.account_id.name,
                    "debit": 0.0,
                    "credit": 0.0,
                    "balance": 0.0,
                }

            account_data[account_id]["debit"] += line.debit
            account_data[account_id]["credit"] += line.credit
            account_data[account_id]["balance"] += line.debit - line.credit

        # Create lines
        for account_id, data in account_data.items():
            lines_to_create.append(
                {
                    "book_id": self.id,
                    "account_id": account_id,
                    "account_code": data["account_code"],
                    "account_name": data["account_name"],
                    "debit": data["debit"],
                    "credit": data["credit"],
                    "balance": data["balance"],
                }
            )

        if lines_to_create:
            self.env["account.ledger.book.line"].create(lines_to_create)

        self.state = "generated"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Ledger book generated successfully with %s accounts")
                % len(lines_to_create),
                "type": "success",
                "sticky": False,
            },
        }

    def action_export_xml(self):
        """Export ledger book to XML format for SII"""
        self.ensure_one()
        if self.state != "generated":
            raise UserError(_("Please generate the book first"))

        wizard = self.env["account.book.export.wizard"].create(
            {
                "book_type": "ledger",
                "ledger_book_id": self.id,
            }
        )
        return {
            "name": _("Export Ledger Book"),
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
