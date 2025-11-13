# Imports of odoo
from odoo.tests.common import TransactionCase


class TestL10nClContribuyente(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contribuyente_model = cls.env["l10n_cl.contribuyente"]

    def test_validar_rut_valid(self):
        """Test RUT validation with valid RUT"""
        result = self.contribuyente_model.validar_rut_en_sii("76077110-3")
        self.assertTrue(result.get("valid"))

    def test_validar_rut_invalid_format(self):
        """Test RUT validation with invalid format"""
        result = self.contribuyente_model.validar_rut_en_sii("invalid")
        self.assertFalse(result.get("valid"))
        self.assertTrue(result.get("error"))

    def test_validar_rut_invalid_check_digit(self):
        """Test RUT validation with invalid check digit"""
        result = self.contribuyente_model.validar_rut_en_sii("76077110-4")
        self.assertFalse(result.get("valid"))

    def test_validate_check_digit_valid(self):
        """Test check digit validation"""
        # Valid RUTs
        self.assertTrue(self.contribuyente_model._validate_check_digit("76077110", "3"))
        self.assertTrue(self.contribuyente_model._validate_check_digit("11111111", "K"))

        # Invalid RUTs
        self.assertFalse(
            self.contribuyente_model._validate_check_digit("76077110", "4")
        )
        self.assertFalse(
            self.contribuyente_model._validate_check_digit("11111111", "1")
        )

    def test_consultar_contribuyente_sii(self):
        """Test taxpayer consultation from SII"""
        result = self.contribuyente_model.consultar_contribuyente_sii("76077110-3")
        # Should return validation result since API not implemented yet
        self.assertTrue(result.get("valid"))
