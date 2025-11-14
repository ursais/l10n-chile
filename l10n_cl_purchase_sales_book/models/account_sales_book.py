# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountSalesBook(models.Model):
    _name = "account.sales.book"
    _inherit = "account.book.export"
    _description = "Chilean Sales Book (Libro de Ventas)"
    _order = "date_from desc, date_to desc"

    # Fields
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
    line_ids = fields.One2many(
        "account.sales.book.line",
        "book_id",
        string="Sales Book Lines",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
        ],
        string="State",
        default="draft",
        readonly=True,
    )
    total_net = fields.Monetary(
        string="Total Net",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_tax = fields.Monetary(
        string="Total Tax",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    # Compute methods
    @api.depends("date_from", "date_to")
    def _compute_name(self):
        for record in self:
            if record.date_from and record.date_to:
                record.name = _("Sales Book %s to %s") % (
                    record.date_from.strftime("%Y-%m-%d"),
                    record.date_to.strftime("%Y-%m-%d"),
                )
            else:
                record.name = _("Sales Book")

    @api.depends("line_ids.net_amount", "line_ids.tax_amount", "line_ids.total_amount")
    def _compute_totals(self):
        for record in self:
            record.total_net = sum(line.net_amount for line in record.line_ids)
            record.total_tax = sum(line.tax_amount for line in record.line_ids)
            record.total_amount = sum(line.total_amount for line in record.line_ids)

    # Constraint methods
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_("From Date must be before To Date"))

    # Action methods
    def action_generate(self):
        """Generate sales book lines from customer invoices"""
        self.ensure_one()

        # Delete existing lines
        self.line_ids.unlink()

        # Get customer invoices for period
        invoice_model = self.env["account.move"]
        invoices = invoice_model.search(
            [
                ("company_id", "=", self.company_id.id),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("invoice_date", ">=", self.date_from),
                ("invoice_date", "<=", self.date_to),
            ],
            order="invoice_date, name",
        )

        # Create book lines
        line_model = self.env["account.sales.book.line"]
        for invoice in invoices:
            line_model.create(self._prepare_sales_book_line(invoice))

        self.state = "generated"
        return True

    def _prepare_sales_book_line(self, invoice):
        """Prepare sales book line values from invoice.

        :param invoice: account.move record
        :return: Dictionary with line values
        """
        # Calculate amounts
        net_amount = invoice.amount_untaxed
        tax_amount = invoice.amount_tax
        total_amount = invoice.amount_total

        # Get document type and DTE status
        document_type = (
            invoice.l10n_latam_document_type_id
            if hasattr(invoice, "l10n_latam_document_type_id")
            else False
        )
        dte_status = (
            invoice.l10n_cl_dte_status
            if hasattr(invoice, "l10n_cl_dte_status")
            else False
        )

        return {
            "book_id": self.id,
            "invoice_id": invoice.id,
            "invoice_date": invoice.invoice_date,
            "partner_id": invoice.partner_id.id,
            "partner_vat": invoice.partner_id.vat or "",
            "document_type_id": document_type.id if document_type else False,
            "document_number": invoice.l10n_latam_document_number
            if hasattr(invoice, "l10n_latam_document_number")
            else invoice.name,
            "dte_status": dte_status,
            "net_amount": net_amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
        }

    def action_reset_to_draft(self):
        """Reset to draft and delete lines"""
        self.write({"state": "draft"})
        self.line_ids.unlink()


class AccountSalesBookLine(models.Model):
    _name = "account.sales.book.line"
    _description = "Sales Book Line"
    _order = "invoice_date, invoice_id"

    # Fields
    book_id = fields.Many2one(
        "account.sales.book",
        string="Sales Book",
        required=True,
        ondelete="cascade",
        index=True,
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        required=True,
        readonly=True,
    )
    invoice_date = fields.Date(
        string="Invoice Date",
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        readonly=True,
    )
    partner_vat = fields.Char(
        string="Customer RUT",
        readonly=True,
    )
    document_type_id = fields.Many2one(
        "l10n_latam.document.type",
        string="Document Type",
        readonly=True,
    )
    document_number = fields.Char(
        string="Document Number",
        readonly=True,
    )
    dte_status = fields.Selection(
        [
            ("not_sent", "Pending To Be Sent"),
            ("ask_for_status", "Ask For Status"),
            ("accepted", "Accepted"),
            ("objected", "Accepted With Objections"),
            ("rejected", "Rejected"),
        ],
        string="DTE Status",
        readonly=True,
    )
    net_amount = fields.Monetary(
        string="Net Amount",
        currency_field="currency_id",
        readonly=True,
    )
    tax_amount = fields.Monetary(
        string="Tax Amount",
        currency_field="currency_id",
        readonly=True,
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="book_id.currency_id",
        store=True,
        readonly=True,
    )
