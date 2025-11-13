# Imports of odoo
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.country_cl = cls.env.ref("base.cl")

    def test_create_partner_with_valid_rut(self):
        """Test creating partner with valid RUT format"""
        partner = self.partner_model.create(
            {
                "name": "Test Partner CL",
                "country_id": self.country_cl.id,
                "vat": "76077110-3",
            }
        )
        self.assertTrue(partner)
        self.assertEqual(partner.vat, "76077110-3")

    def test_create_partner_with_invalid_rut(self):
        """Test that invalid RUT raises validation error"""
        with self.assertRaises(ValidationError):
            self.partner_model.create(
                {
                    "name": "Test Partner Invalid",
                    "country_id": self.country_cl.id,
                    "vat": "12345678-0",  # Invalid check digit
                }
            )

    def test_validate_rut_format(self):
        """Test RUT format validation"""
        partner = self.partner_model.create(
            {
                "name": "Test Partner",
                "country_id": self.country_cl.id,
            }
        )

        # Valid formats
        self.assertTrue(partner._validate_rut_format("76077110-3"))
        self.assertTrue(partner._validate_rut_format("76.077.110-3"))
        self.assertTrue(partner._validate_rut_format("CL760771103"))

        # Invalid formats
        self.assertFalse(partner._validate_rut_format("12345678-0"))
        self.assertFalse(partner._validate_rut_format("invalid"))
        self.assertFalse(partner._validate_rut_format(""))

    def test_validate_rut_check_digit(self):
        """Test RUT check digit validation"""
        partner = self.partner_model.create(
            {
                "name": "Test Partner",
                "country_id": self.country_cl.id,
            }
        )

        # Valid check digits
        self.assertTrue(partner._validate_rut_check_digit("76077110-3"))
        self.assertTrue(partner._validate_rut_check_digit("11111111-K"))

        # Invalid check digits
        self.assertFalse(partner._validate_rut_check_digit("76077110-4"))
        self.assertFalse(partner._validate_rut_check_digit("11111111-1"))

    def test_action_validate_rut_no_vat(self):
        """Test validation fails without VAT"""
        partner = self.partner_model.create(
            {
                "name": "Test Partner No VAT",
                "country_id": self.country_cl.id,
            }
        )
        with self.assertRaises(UserError):
            partner.action_validate_rut_with_sii()

    def test_action_validate_rut_not_chile(self):
        """Test validation fails for non-Chilean partners"""
        partner = self.partner_model.create(
            {
                "name": "Test Partner US",
                "country_id": self.env.ref("base.us").id,
                "vat": "123456789",
            }
        )
        with self.assertRaises(UserError):
            partner.action_validate_rut_with_sii()
