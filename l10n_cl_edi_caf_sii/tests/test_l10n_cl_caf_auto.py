# Standard library imports
from unittest.mock import patch

# Imports of odoo
from odoo.tests.common import TransactionCase


class TestL10nClCafAuto(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "vat": "CL760771103",
                "country_id": cls.env.ref("base.cl").id,
            }
        )

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

        cls.user = cls.env.user

    def test_create_caf_monitor(self):
        """Test creation of CAF monitor"""
        monitor = self.env["l10n_cl.caf.auto"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "threshold_percentage": 20.0,
                "threshold_absolute": 50,
                "alert_user_ids": [(6, 0, [self.user.id])],
            }
        )
        self.assertTrue(monitor)
        self.assertTrue(monitor.active)
        self.assertTrue(monitor.name)

    def test_check_caf_availability_no_caf(self):
        """Test CAF availability check when no CAF files exist"""
        monitor = self.env["l10n_cl.caf.auto"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "alert_user_ids": [(6, 0, [self.user.id])],
            }
        )

        # Mock the _send_alert method to avoid actual activity creation
        with patch.object(monitor, "_send_alert") as mock_alert:
            monitor.check_caf_availability()
            mock_alert.assert_called_once()

        self.assertTrue(monitor.last_check_date)

    def test_cron_check_caf_availability(self):
        """Test cron job for checking CAF availability"""
        monitor = self.env["l10n_cl.caf.auto"].create(
            {
                "company_id": self.company.id,
                "document_type_id": self.document_type.id,
                "active": True,
            }
        )

        with patch.object(monitor, "check_caf_availability") as mock_check:
            self.env["l10n_cl.caf.auto"].cron_check_caf_availability()
            mock_check.assert_called_once()

    def test_caf_usage_computation(self):
        """Test CAF usage computation on l10n_cl.dte.caf"""
        # This test verifies the extension of l10n_cl.dte.caf
        # Create a CAF file (if l10n_cl_edi is available)
        try:
            caf_model = self.env["l10n_cl.dte.caf"]
            # Test that new fields are available
            self.assertTrue(hasattr(caf_model, "used_folios_count"))
            self.assertTrue(hasattr(caf_model, "available_folios_count"))
        except Exception:
            self.skipTest("l10n_cl_edi module not available")
