# Standard library imports
from datetime import date, timedelta

# Imports of odoo
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountPurchaseBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "supplier_rank": 1,
            }
        )
        cls.journal = cls.env["account.journal"].search(
            [
                ("company_id", "=", cls.company.id),
                ("type", "=", "purchase"),
            ],
            limit=1,
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Purchase Journal",
                    "code": "PURCH",
                    "type": "purchase",
                }
            )

    def test_create_purchase_book(self):
        """Test creation of purchase book"""
        book = self.env["account.purchase.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        self.assertTrue(book)
        self.assertEqual(book.state, "draft")
        self.assertTrue(book.name)

    def test_validate_dates(self):
        """Test date validation"""
        with self.assertRaises(ValidationError):
            book = self.env["account.purchase.book"].create(
                {
                    "date_from": date.today(),
                    "date_to": date.today() - timedelta(days=1),
                }
            )
            book._check_dates()

    def test_generate_purchase_book(self):
        """Test generation of purchase book"""
        # Create test invoice
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
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
        book = self.env["account.purchase.book"].create(
            {
                "date_from": date.today(),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        self.assertEqual(book.state, "generated")
        self.assertGreater(len(book.line_ids), 0)

    def test_reset_to_draft(self):
        """Test reset to draft"""
        book = self.env["account.purchase.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()
        book.action_reset_to_draft()
        self.assertEqual(book.state, "draft")
        self.assertEqual(len(book.line_ids), 0)
