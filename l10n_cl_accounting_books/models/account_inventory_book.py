# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountInventoryBook(models.Model):
    _name = "account.inventory.book"
    _description = "Chilean Inventory and Balance Book (Libro de Inventario y Balances)"
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
        help="Start date of the period (usually beginning of fiscal year)",
    )
    date_to = fields.Date(
        string="To Date",
        required=True,
        help="End date of the period (usually end of fiscal year)",
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

    # Initial Balance
    initial_balance_ids = fields.One2many(
        "account.inventory.book.line",
        "book_id",
        string="Initial Balance",
        domain=[("line_type", "=", "initial")],
        readonly=True,
    )

    # Final Balance
    final_balance_ids = fields.One2many(
        "account.inventory.book.line",
        "book_id",
        string="Final Balance",
        domain=[("line_type", "=", "final")],
        readonly=True,
    )

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        store=False,
    )

    @api.depends("date_from", "date_to", "company_id")
    def _compute_name(self):
        for record in self:
            if record.date_from and record.date_to:
                record.name = _("Inventory Book %s - %s") % (
                    record.date_from.strftime("%Y-%m-%d"),
                    record.date_to.strftime("%Y-%m-%d"),
                )
            else:
                record.name = _("New Inventory Book")

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_("From date must be before To date"))

    def action_generate(self):
        """Generate inventory book with initial and final balances"""
        self.ensure_one()

        if self.state != "draft":
            raise UserError(_("You can only generate from draft state"))

        if not self.date_from or not self.date_to:
            raise UserError(_("Please set From Date and To Date"))

        if self.date_from > self.date_to:
            raise UserError(_("From date must be before To date"))

        # Clear existing lines
        self.initial_balance_ids.unlink()
        self.final_balance_ids.unlink()

        # Get all accounts
        accounts = self.env["account.account"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("deprecated", "=", False),
            ],
            order="code",
        )

        if not accounts:
            raise UserError(_("No accounts found"))

        # Generate initial balance (balance before date_from)
        initial_lines = []
        final_lines = []

        for account in accounts:
            # Initial balance
            initial_balance = self._get_account_balance(
                account, self.date_from, "before"
            )
            initial_lines.append(
                {
                    "book_id": self.id,
                    "line_type": "initial",
                    "account_id": account.id,
                    "account_code": account.code,
                    "account_name": account.name,
                    "debit": initial_balance["debit"],
                    "credit": initial_balance["credit"],
                    "balance": initial_balance["balance"],
                }
            )

            # Final balance (balance up to date_to)
            final_balance = self._get_account_balance(account, self.date_to, "up_to")
            final_lines.append(
                {
                    "book_id": self.id,
                    "line_type": "final",
                    "account_id": account.id,
                    "account_code": account.code,
                    "account_name": account.name,
                    "debit": final_balance["debit"],
                    "credit": final_balance["credit"],
                    "balance": final_balance["balance"],
                }
            )

        # Create lines
        if initial_lines:
            self.env["account.inventory.book.line"].create(initial_lines)
        if final_lines:
            self.env["account.inventory.book.line"].create(final_lines)

        self.state = "generated"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Inventory book generated successfully"),
                "type": "success",
                "sticky": False,
            },
        }

    def _get_account_balance(self, account, date, mode="up_to"):
        """Get account balance up to or before a date"""
        domain = [
            ("account_id", "=", account.id),
            ("company_id", "=", self.company_id.id),
            ("move_id.state", "=", "posted"),
        ]

        if mode == "before":
            domain.append(("date", "<", date))
        elif mode == "up_to":
            domain.append(("date", "<=", date))

        lines = self.env["account.move.line"].search(domain)

        return {
            "debit": sum(lines.mapped("debit")),
            "credit": sum(lines.mapped("credit")),
            "balance": sum(lines.mapped("debit")) - sum(lines.mapped("credit")),
        }

    def action_export_xml(self):
        """Export inventory book to XML format for SII"""
        self.ensure_one()
        if self.state != "generated":
            raise UserError(_("Please generate the book first"))

        wizard = self.env["account.book.export.wizard"].create(
            {
                "book_type": "inventory",
                "inventory_book_id": self.id,
            }
        )
        return {
            "name": _("Export Inventory Book"),
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
        self.initial_balance_ids.unlink()
        self.final_balance_ids.unlink()
        self.state = "draft"
