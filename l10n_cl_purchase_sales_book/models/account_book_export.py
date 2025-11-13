# Standard library imports
import base64
import logging

# Third party imports
from lxml import etree

# Imports of odoo
from odoo import models

_logger = logging.getLogger(__name__)


class AccountBookExport(models.AbstractModel):
    _name = "account.book.export"
    _description = "Account Book Export Utilities"

    def export_to_xml_sii(self, book_type="purchase"):
        """Export book to SII XML format.

        :param book_type: 'purchase' or 'sales'
        :return: XML string
        """
        # Prepare XML structure according to SII specifications
        root = etree.Element("LibroCompraVenta")

        # Add header
        header = etree.SubElement(root, "EnvioLibro")
        etree.SubElement(header, "TipoLibro").text = (
            "COMPRA" if book_type == "purchase" else "VENTA"
        )
        etree.SubElement(header, "RutEmisorLibro").text = self._format_rut(
            self.company_id.vat
        )
        etree.SubElement(header, "PeriodoTributario").text = self.date_from.strftime(
            "%Y-%m"
        )

        # Add details
        details = etree.SubElement(root, "Detalles")
        for line in self.line_ids:
            detail = etree.SubElement(details, "Detalle")
            etree.SubElement(detail, "TpoDoc").text = (
                line.document_type_id.code if line.document_type_id else "0"
            )
            etree.SubElement(detail, "NroDoc").text = line.document_number or ""
            etree.SubElement(detail, "FchDoc").text = line.invoice_date.strftime(
                "%Y-%m-%d"
            )
            etree.SubElement(detail, "RUTDoc").text = self._format_rut(line.partner_vat)
            etree.SubElement(detail, "MntNeto").text = str(int(line.net_amount))
            etree.SubElement(detail, "MntIVA").text = str(int(line.tax_amount))
            etree.SubElement(detail, "MntTotal").text = str(int(line.total_amount))

        # Add totals
        totals = etree.SubElement(root, "Totales")
        etree.SubElement(totals, "TotalMntNeto").text = str(int(self.total_net))
        etree.SubElement(totals, "TotalMntIVA").text = str(int(self.total_tax))
        etree.SubElement(totals, "TotalMntTotal").text = str(int(self.total_amount))

        # Convert to string
        xml_string = etree.tostring(
            root,
            pretty_print=True,
            encoding="ISO-8859-1",
            xml_declaration=True,
        )

        return xml_string

    def _format_rut(self, vat):
        """Format RUT for SII XML.

        :param vat: VAT string
        :return: Formatted RUT (12345678-9)
        """
        if not vat:
            return ""

        # Remove country code and formatting
        rut = vat.replace("CL", "").replace("cl", "").replace(".", "").strip()

        # Ensure it has dash
        if "-" not in rut:
            rut = rut[:-1] + "-" + rut[-1]

        return rut

    def action_export_xml(self):
        """Export book to XML and download"""
        self.ensure_one()

        book_type = "purchase" if self._name == "account.purchase.book" else "sales"
        xml_content = self.export_to_xml_sii(book_type=book_type)

        # Create attachment
        filename = f"{book_type}_book_{self.date_from}_{self.date_to}.xml"
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": base64.b64encode(xml_content),
                "mimetype": "application/xml",
                "res_model": self._name,
                "res_id": self.id,
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
