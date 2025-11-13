# Standard library imports
import logging

# Third party imports
# Imports of odoo
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ValidarRutController(http.Controller):
    @http.route("/l10n_cl/validate_rut", type="json", auth="user", methods=["POST"])
    def validate_rut(self, rut):
        """JSON API endpoint to validate Chilean RUT.

        :param rut: RUT string to validate
        :return: JSON with validation result
        """
        if not rut:
            return {
                "valid": False,
                "error": "RUT is required",
            }

        try:
            contribuyente_model = request.env["l10n_cl.contribuyente"]
            result = contribuyente_model.validar_rut_en_sii(rut)
            return result
        except Exception as error:
            _logger.error("Error validating RUT via API: %s", error)
            return {
                "valid": False,
                "error": str(error),
            }

    @http.route("/l10n_cl/format_rut", type="json", auth="user", methods=["POST"])
    def format_rut(self, rut):
        """Format Chilean RUT to standard format.

        :param rut: RUT string (with or without formatting)
        :return: JSON with formatted RUT
        """
        try:
            # Remove all formatting
            rut_clean = (
                rut.replace("CL", "")
                .replace("cl", "")
                .replace(".", "")
                .replace("-", "")
                .strip()
            )

            if len(rut_clean) < 2:
                return {"formatted": rut, "error": "Invalid RUT"}

            # Split number and check digit
            number = rut_clean[:-1]
            check_digit = rut_clean[-1].upper()

            # Format with dots: 12.345.678-9
            formatted_number = ""
            for i, digit in enumerate(reversed(number)):
                if i > 0 and i % 3 == 0:
                    formatted_number = "." + formatted_number
                formatted_number = digit + formatted_number

            formatted_rut = f"{formatted_number}-{check_digit}"

            return {
                "formatted": formatted_rut,
                "clean": f"{number}-{check_digit}",
                "with_country": f"CL{number}{check_digit}",
            }
        except Exception as error:
            _logger.error("Error formatting RUT: %s", error)
            return {
                "formatted": rut,
                "error": str(error),
            }
