# Standard library imports
from datetime import date, timedelta

# Imports of odoo
from odoo.tests.common import TransactionCase


class TestAccountSalesBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "customer_rank": 1,
            }
        )
        cls.journal = cls.env["account.journal"].search(
            [
                ("company_id", "=", cls.company.id),
                ("type", "=", "sale"),
            ],
            limit=1,
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Sales Journal",
                    "code": "SALE",
                    "type": "sale",
                }
            )

    def test_create_sales_book(self):
        """Test creation of sales book"""
        book = self.env["account.sales.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        self.assertTrue(book)
        self.assertEqual(book.state, "draft")
        self.assertTrue(book.name)

    def test_generate_sales_book(self):
        """Test generation of sales book"""
        # Create test invoice
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "invoice_date": date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "quantity": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        invoice.action_post()

        # Generate book
        book = self.env["account.sales.book"].create(
            {
                "date_from": date.today(),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        self.assertEqual(book.state, "generated")
        self.assertGreater(len(book.line_ids), 0)

    def test_export_xml(self):
        """Test XML export"""
        book = self.env["account.sales.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        # Test export (should return action)
        result = book.action_export_xml()
        self.assertTrue(result)
        self.assertEqual(result.get("type"), "ir.actions.act_url")
