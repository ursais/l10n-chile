# Standard library imports
from datetime import date, timedelta

# Imports of odoo
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountPurchaseBookSii(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "vat": "CL760771103",
                "country_id": cls.env.ref("base.cl").id,
                "l10n_cl_dte_service_provider": "SIIDEMO",
            }
        )

    def test_send_purchase_book_to_sii_demo(self):
        """Test sending purchase book to SII in DEMO mode"""
        book = self.env["account.purchase.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        # Send to SII (DEMO mode)
        book.action_send_to_sii()

        self.assertEqual(book.l10n_cl_dte_status, "accepted")

    def test_send_purchase_book_not_generated(self):
        """Test that draft book cannot be sent"""
        book = self.env["account.purchase.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )

        with self.assertRaises(UserError):
            book.action_send_to_sii()

    def test_generate_libro_compras_xml(self):
        """Test XML generation for purchase book"""
        book = self.env["account.purchase.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        xml_content = book._generate_libro_compras_xml()
        self.assertTrue(xml_content)
        self.assertIn(b"LibroCompraVenta", xml_content)
        self.assertIn(b"COMPRA", xml_content)
