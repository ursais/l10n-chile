# Standard library imports
import base64
import logging

# Third party imports
from lxml import etree

# Imports of odoo
from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountSalesBook(models.Model):
    _inherit = "account.sales.book"
    _name = "account.sales.book"

    # Add fields for SII submission
    l10n_cl_sii_send_file = fields.Many2one(
        "ir.attachment",
        string="SII Send File",
        copy=False,
        readonly=True,
    )
    l10n_cl_sii_send_ident = fields.Char(
        string="SII Send Identification (Track ID)",
        copy=False,
        readonly=True,
    )
    l10n_cl_dte_status = fields.Selection(
        [
            ("not_sent", "Pending To Be Sent"),
            ("ask_for_status", "Ask For Status"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        string="SII Status",
        default="not_sent",
        copy=False,
        readonly=True,
    )

    # Inherit edi util to use SII methods
    _inherit = ["l10n_cl.edi.util", "account.sales.book"]

    # Business methods
    def action_send_to_sii(self):
        """Send sales book to SII web services.

        :return: True if sent successfully
        :raises UserError: If sending fails
        """
        self.ensure_one()

        if self.state != "generated":
            raise UserError(_("Book must be generated before sending to SII"))

        # Get digital signature
        digital_signature_sudo = self.company_id.sudo()._get_digital_signature(
            user_id=self.env.user.id
        )
        if not digital_signature_sudo:
            raise UserError(_("Please configure a digital signature certificate"))

        # Generate XML for SII
        xml_content = self._generate_libro_ventas_xml()

        # Sign XML
        signed_xml = self._sign_libro_xml(xml_content, digital_signature_sudo)

        # Create attachment
        filename = f"LibroVentas_{self.date_from}_{self.date_to}.xml"
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": base64.b64encode(signed_xml),
                "mimetype": "application/xml",
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        self.l10n_cl_sii_send_file = attachment.id

        # Send to SII
        mode = self.company_id.l10n_cl_dte_service_provider
        if mode == "SIIDEMO":
            self.l10n_cl_dte_status = "accepted"
            self.message_post(
                body=_("Book sent in DEMO mode (not actually sent to SII)")
            )
            return True

        # Prepare parameters
        params = {
            "rutSender": digital_signature_sudo.subject_serial_number[:-2],
            "dvSender": digital_signature_sudo.subject_serial_number[-1],
            "rutCompany": self._l10n_cl_format_vat(self.company_id.vat)[:-2],
            "dvCompany": self._l10n_cl_format_vat(self.company_id.vat)[-1],
            "archivo": (filename, signed_xml, "application/xml"),
        }

        # Send via SOAP
        response = self._send_xml_to_sii(
            mode,
            self.company_id.website,
            params,
            digital_signature_sudo,
            post="/cgi_dte/UPL/LibroUpload",
        )

        if not response:
            self.l10n_cl_dte_status = "rejected"
            return False

        # Parse response
        response_parsed = etree.fromstring(response)
        self.l10n_cl_sii_send_ident = response_parsed.findtext("TRACKID")
        sii_response_status = response_parsed.findtext("STATUS")

        if sii_response_status == "0":
            self.l10n_cl_dte_status = "ask_for_status"
            self.message_post(
                body=_("Sales Book sent to SII. Track ID: %s")
                % self.l10n_cl_sii_send_ident
            )
        else:
            self.l10n_cl_dte_status = "rejected"
            self.message_post(
                body=_("Sales Book rejected by SII. Status: %s") % sii_response_status
            )

        return True

    def _generate_libro_ventas_xml(self):
        """Generate XML for Libro de Ventas according to SII specifications.

        :return: XML string (bytes)
        """
        # Build XML structure (similar to purchase book)
        root = etree.Element("LibroCompraVenta", version="1.0")

        # Envelope
        envelope = etree.SubElement(root, "EnvioLibro", ID="SetDoc")

        # Header
        header = etree.SubElement(envelope, "Caratula")
        etree.SubElement(header, "RutEmisorLibro").text = self._l10n_cl_format_vat(
            self.company_id.vat
        )
        etree.SubElement(header, "RutEnvia").text = self._l10n_cl_format_vat(
            self.company_id.vat
        )
        etree.SubElement(header, "PeriodoTributario").text = self.date_from.strftime(
            "%Y-%m"
        )
        etree.SubElement(header, "FchResol").text = (
            str(self.company_id.l10n_cl_dte_resolution_date)
            if hasattr(self.company_id, "l10n_cl_dte_resolution_date")
            else ""
        )
        etree.SubElement(header, "NroResol").text = (
            str(self.company_id.l10n_cl_dte_resolution_number)
            if hasattr(self.company_id, "l10n_cl_dte_resolution_number")
            else "0"
        )
        etree.SubElement(header, "TipoOperacion").text = "VENTA"
        etree.SubElement(header, "TipoLibro").text = "MENSUAL"
        etree.SubElement(header, "TipoEnvio").text = "TOTAL"

        # Sales
        for line in self.line_ids:
            detail = etree.SubElement(envelope, "Detalle")
            etree.SubElement(detail, "TpoDoc").text = (
                line.document_type_id.code if line.document_type_id else "33"
            )
            etree.SubElement(detail, "NroDoc").text = (
                str(line.document_number) if line.document_number else ""
            )
            etree.SubElement(detail, "FchDoc").text = line.invoice_date.strftime(
                "%Y-%m-%d"
            )
            etree.SubElement(detail, "RUTDoc").text = (
                self._l10n_cl_format_vat(line.partner_vat) if line.partner_vat else ""
            )
            etree.SubElement(detail, "RznSoc").text = (
                line.partner_id.name[:50] if line.partner_id else ""
            )
            etree.SubElement(detail, "MntNeto").text = str(int(line.net_amount))
            etree.SubElement(detail, "MntIVA").text = str(int(line.tax_amount))
            etree.SubElement(detail, "MntTotal").text = str(int(line.total_amount))

        # Totals
        totals = etree.SubElement(envelope, "TotalesResumen")
        etree.SubElement(totals, "TpoDoc").text = "33"
        etree.SubElement(totals, "TotDoc").text = str(len(self.line_ids))
        etree.SubElement(totals, "TotMntNeto").text = str(int(self.total_net))
        etree.SubElement(totals, "TotMntIVA").text = str(int(self.total_tax))
        etree.SubElement(totals, "TotMntTotal").text = str(int(self.total_amount))

        return etree.tostring(
            root, pretty_print=True, encoding="ISO-8859-1", xml_declaration=True
        )

    def _sign_libro_xml(self, xml_content, digital_signature):
        """Sign libro XML with digital signature.

        :param xml_content: XML content bytes
        :param digital_signature: Digital signature record
        :return: Signed XML bytes
        """
        # For now return unsigned (full signing implementation requires deep integration)
        _logger.warning("XML signing for libros not yet fully implemented")
        return xml_content

    def action_verify_status_sii(self):
        """Verify status of book sent to SII"""
        self.ensure_one()

        if not self.l10n_cl_sii_send_ident:
            raise UserError(_("No Track ID found. Book has not been sent to SII yet."))

        digital_signature_sudo = self.company_id.sudo()._get_digital_signature(
            user_id=self.env.user.id
        )

        # Query status
        mode = self.company_id.l10n_cl_dte_service_provider
        response = self._get_send_status(
            mode,
            self.l10n_cl_sii_send_ident,
            self._l10n_cl_format_vat(self.company_id.vat),
            digital_signature_sudo,
        )

        if not response:
            return False

        # Parse and update status
        response_parsed = etree.fromstring(response.encode("utf-8"))
        status = self._analyze_sii_result(response_parsed)

        self.l10n_cl_dte_status = status
        self.message_post(body=_("Book status updated from SII: %s") % status)

        return True
