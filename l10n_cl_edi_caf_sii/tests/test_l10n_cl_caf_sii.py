# Standard library imports
from unittest.mock import patch

# Imports of odoo
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestL10nClCafSii(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "vat": "CL760771103",
                "country_id": cls.env.ref("base.cl").id,
                "l10n_cl_dte_service_provider": "SIITEST",
            }
        )

        # Get or create document type
        cls.document_type = cls.env["l10n_latam.document.type"].search(
            [
                ("code", "=", "33"),
                ("country_id.code", "=", "CL"),
            ],
            limit=1,
        )
        if not cls.document_type:
            cls.document_type = cls.env["l10n_latam.document.type"].create(
                {
                    "name": "Factura Electrónica",
                    "code": "33",
                    "country_id": cls.env.ref("base.cl").id,
                }
            )

    def test_create_caf_query(self):
        """Test creation of CAF query record"""
        caf_query = self.env["l10n_cl.caf.sii"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "date_from": 1,
                "date_to": 100,
            }
        )
        self.assertTrue(caf_query)
        self.assertEqual(caf_query.state, "draft")
        self.assertTrue(caf_query.name)

    def test_check_dates_constraint(self):
        """Test that from_folio must be less than to_folio"""
        caf_query = self.env["l10n_cl.caf.sii"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "date_from": 100,
                "date_to": 1,
            }
        )
        with self.assertRaises(UserError):
            caf_query._check_dates()

    def test_consultar_caf_no_provider(self):
        """Test CAF query fails without DTE service provider"""
        self.company.l10n_cl_dte_service_provider = False
        caf_query = self.env["l10n_cl.caf.sii"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "date_from": 1,
                "date_to": 100,
            }
        )
        with self.assertRaises(UserError):
            caf_query.consultar_caf_desde_sii()

    @patch("odoo.addons.l10n_cl_edi.models.l10n_cl_edi_util.Client")
    def test_consultar_caf_from_sii_success(self, mock_client):
        """Test successful CAF query from SII"""
        # Skip if no certificate configured
        if not self.company.sudo()._get_digital_signature(user_id=self.env.user.id):
            self.skipTest("No digital signature configured")

        caf_query = self.env["l10n_cl.caf.sii"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "date_from": 1,
                "date_to": 100,
            }
        )

        # Mock the token retrieval
        with patch.object(caf_query, "_get_token", return_value="mock_token"):
            caf_query.consultar_caf_desde_sii()

        self.assertEqual(caf_query.state, "consulted")
        self.assertTrue(caf_query.last_query_date)

    def test_action_reset_to_draft(self):
        """Test reset to draft functionality"""
        caf_query = self.env["l10n_cl.caf.sii"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "date_from": 1,
                "date_to": 100,
                "state": "consulted",
            }
        )
        caf_query.action_reset_to_draft()
        self.assertEqual(caf_query.state, "draft")
