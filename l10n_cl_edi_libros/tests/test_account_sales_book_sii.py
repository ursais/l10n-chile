# Standard library imports
from datetime import date, timedelta

# Imports of odoo
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountSalesBookSii(TransactionCase):
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

    def test_send_sales_book_to_sii_demo(self):
        """Test sending sales book to SII in DEMO mode"""
        book = self.env["account.sales.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        # Send to SII (DEMO mode)
        book.action_send_to_sii()

        self.assertEqual(book.l10n_cl_dte_status, "accepted")

    def test_send_sales_book_not_generated(self):
        """Test that draft book cannot be sent"""
        book = self.env["account.sales.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )

        with self.assertRaises(UserError):
            book.action_send_to_sii()

    def test_generate_libro_ventas_xml(self):
        """Test XML generation for sales book"""
        book = self.env["account.sales.book"].create(
            {
                "date_from": date.today() - timedelta(days=30),
                "date_to": date.today(),
            }
        )
        book.action_generate()

        xml_content = book._generate_libro_ventas_xml()
        self.assertTrue(xml_content)
        self.assertIn(b"LibroCompraVenta", xml_content)
        self.assertIn(b"VENTA", xml_content)
