# Standard library imports
from datetime import date, timedelta

# Imports of odoo
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountJournalBook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.journal = cls.env["account.journal"].search(
            [
                ("company_id", "=", cls.company.id),
                ("type", "=", "general"),
            ],
            limit=1,
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Test Journal",
                    "code": "TEST",
                    "type": "general",
                }
            )

        # Get or create account
        cls.account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("account_type", "=", "asset_current"),
            ],
            limit=1,
        )
        if not cls.account:
            cls.account = cls.env["account.account"].create(
                {
                    "name": "Test Account",
                    "code": "TEST001",
                    "account_type": "asset_current",
                }
            )

    def test_create_journal_book(self):
        """Test creation of journal book"""
        book = self.env["account.journal.book"].create(
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
        book = self.env["account.journal.book"].create(
            {
                "date_from": date.today(),
                "date_to": date.today() - timedelta(days=1),
            }
        )
        with self.assertRaises(ValidationError):
            book._check_dates()

    def test_generate_journal_book(self):
        """Test generation of journal book lines"""
        # Create a posted move
        move = self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "date": date.today(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.account.id,
                            "debit": 100.0,
                            "name": "Test Debit",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.account.id,
                            "credit": 100.0,
                            "name": "Test Credit",
                        },
                    ),
                ],
            }
        )
        move.action_post()

        # Create and generate book
        book = self.env["account.journal.book"].create(
            {
                "date_from": date.today(),
                "date_to": date.today(),
                "journal_ids": [(6, 0, [self.journal.id])],
            }
        )
        book.action_generate()

        self.assertEqual(book.state, "generated")
        self.assertGreater(len(book.line_ids), 0)
        self.assertEqual(book.total_debit, 100.0)
        self.assertEqual(book.total_credit, 100.0)

    def test_reset_to_draft(self):
        """Test reset to draft"""
        book = self.env["account.journal.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()
        self.assertEqual(book.state, "generated")
        book.action_reset_to_draft()
        self.assertEqual(book.state, "draft")
