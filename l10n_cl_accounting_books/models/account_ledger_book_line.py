# Imports of odoo
from odoo import fields, models


class AccountLedgerBookLine(models.Model):
    _name = "account.ledger.book.line"
    _description = "Ledger Book Line"
    _order = "account_code, account_id"

    book_id = fields.Many2one(
        "account.ledger.book",
        string="Ledger Book",
        required=True,
        ondelete="cascade",
        index=True,
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
        index=True,
    )
    account_code = fields.Char(
        string="Account Code",
        required=True,
        index=True,
    )
    account_name = fields.Char(
        string="Account Name",
        required=True,
    )
    debit = fields.Monetary(
        string="Debit",
        currency_field="company_currency_id",
        default=0.0,
    )
    credit = fields.Monetary(
        string="Credit",
        currency_field="company_currency_id",
        default=0.0,
    )
    balance = fields.Monetary(
        string="Balance",
        currency_field="company_currency_id",
        default=0.0,
        help="Balance = Debit - Credit",
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="book_id.company_currency_id",
        string="Currency",
        readonly=True,
        store=False,
    )
