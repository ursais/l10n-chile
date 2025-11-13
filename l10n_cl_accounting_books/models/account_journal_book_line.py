# Imports of odoo
from odoo import fields, models


class AccountJournalBookLine(models.Model):
    _name = "account.journal.book.line"
    _description = "Journal Book Line"
    _order = "sequence, date, id"

    book_id = fields.Many2one(
        "account.journal.book",
        string="Journal Book",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        index=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        index=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
    )
    journal_code = fields.Char(
        string="Journal Code",
        related="journal_id.code",
        store=True,
        readonly=True,
    )
    move_id = fields.Many2one(
        "account.move",
        string="Move",
        required=True,
        ondelete="cascade",
    )
    move_name = fields.Char(
        string="Move Number",
        required=True,
        index=True,
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
    )
    account_code = fields.Char(
        string="Account Code",
        related="account_id.code",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
    )
    partner_vat = fields.Char(
        string="Partner VAT",
        readonly=True,
    )
    name = fields.Char(
        string="Description",
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
    company_currency_id = fields.Many2one(
        "res.currency",
        related="book_id.company_currency_id",
        string="Currency",
        readonly=True,
    )
