# Standard library imports
import logging

# Known third party imports
from lxml import etree

# Imports of odoo
from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBookExport(models.AbstractModel):
    _name = "account.book.export"
    _description = "Base class for accounting book exports"

    def generate_journal_book_xml(self, book):
        """Generate XML for Journal Book (Libro Diario)"""
        if not book.line_ids:
            raise UserError(_("No lines to export"))

        # Create XML structure according to SII format
        # Note: This is a basic structure. Actual SII format may vary
        root = etree.Element("LibroDiario")
        root.set("xmlns", "http://www.sii.cl/SiiDte")
        root.set("version", "1.0")

        # Header
        encabezado = etree.SubElement(root, "Encabezado")
        etree.SubElement(encabezado, "RutEmisor").text = (
            (book.company_id.vat or "").replace(".", "").replace("-", "")
        )
        etree.SubElement(encabezado, "RazonSocial").text = book.company_id.name or ""
        etree.SubElement(encabezado, "Periodo").text = book.date_from.strftime("%Y-%m")
        etree.SubElement(encabezado, "FechaInicio").text = book.date_from.strftime(
            "%Y-%m-%d"
        )
        etree.SubElement(encabezado, "FechaFin").text = book.date_to.strftime(
            "%Y-%m-%d"
        )

        # Details
        detalle = etree.SubElement(root, "Detalle")
        for line in book.line_ids:
            item = etree.SubElement(detalle, "Item")
            etree.SubElement(item, "Fecha").text = line.date.strftime("%Y-%m-%d")
            etree.SubElement(item, "Diario").text = line.journal_code or ""
            etree.SubElement(item, "Asiento").text = line.move_name or ""
            etree.SubElement(item, "Cuenta").text = line.account_code or ""
            etree.SubElement(item, "Descripcion").text = line.name or ""
            if line.partner_vat:
                etree.SubElement(item, "RutTercero").text = (
                    (line.partner_vat or "").replace(".", "").replace("-", "")
                )
            etree.SubElement(item, "Debe").text = "%.2f" % line.debit
            etree.SubElement(item, "Haber").text = "%.2f" % line.credit

        # Totals
        totales = etree.SubElement(root, "Totales")
        etree.SubElement(totales, "TotalDebe").text = "%.2f" % book.total_debit
        etree.SubElement(totales, "TotalHaber").text = "%.2f" % book.total_credit

        return etree.tostring(
            root, encoding="utf-8", xml_declaration=True, pretty_print=True
        )

    def generate_ledger_book_xml(self, book):
        """Generate XML for Ledger Book (Libro Mayor)"""
        if not book.line_ids:
            raise UserError(_("No lines to export"))

        root = etree.Element("LibroMayor")
        root.set("xmlns", "http://www.sii.cl/SiiDte")
        root.set("version", "1.0")

        # Header
        encabezado = etree.SubElement(root, "Encabezado")
        etree.SubElement(encabezado, "RutEmisor").text = (
            (book.company_id.vat or "").replace(".", "").replace("-", "")
        )
        etree.SubElement(encabezado, "RazonSocial").text = book.company_id.name or ""
        etree.SubElement(encabezado, "Periodo").text = book.date_from.strftime("%Y-%m")
        etree.SubElement(encabezado, "FechaInicio").text = book.date_from.strftime(
            "%Y-%m-%d"
        )
        etree.SubElement(encabezado, "FechaFin").text = book.date_to.strftime(
            "%Y-%m-%d"
        )

        # Details
        detalle = etree.SubElement(root, "Detalle")
        for line in book.line_ids:
            item = etree.SubElement(detalle, "Item")
            etree.SubElement(item, "Cuenta").text = line.account_code or ""
            etree.SubElement(item, "Descripcion").text = line.account_name or ""
            etree.SubElement(item, "Debe").text = "%.2f" % line.debit
            etree.SubElement(item, "Haber").text = "%.2f" % line.credit
            etree.SubElement(item, "Saldo").text = "%.2f" % line.balance

        return etree.tostring(
            root, encoding="utf-8", xml_declaration=True, pretty_print=True
        )

    def generate_inventory_book_xml(self, book):
        """Generate XML for Inventory Book (Libro de Inventario y Balances)"""
        if not book.initial_balance_ids and not book.final_balance_ids:
            raise UserError(_("No lines to export"))

        root = etree.Element("LibroInventario")
        root.set("xmlns", "http://www.sii.cl/SiiDte")
        root.set("version", "1.0")

        # Header
        encabezado = etree.SubElement(root, "Encabezado")
        etree.SubElement(encabezado, "RutEmisor").text = (
            (book.company_id.vat or "").replace(".", "").replace("-", "")
        )
        etree.SubElement(encabezado, "RazonSocial").text = book.company_id.name or ""
        etree.SubElement(encabezado, "Periodo").text = book.date_from.strftime("%Y-%m")
        etree.SubElement(encabezado, "FechaInicio").text = book.date_from.strftime(
            "%Y-%m-%d"
        )
        etree.SubElement(encabezado, "FechaFin").text = book.date_to.strftime(
            "%Y-%m-%d"
        )

        # Initial Balance
        if book.initial_balance_ids:
            saldo_inicial = etree.SubElement(root, "SaldoInicial")
            for line in book.initial_balance_ids:
                item = etree.SubElement(saldo_inicial, "Item")
                etree.SubElement(item, "Cuenta").text = line.account_code or ""
                etree.SubElement(item, "Descripcion").text = line.account_name or ""
                etree.SubElement(item, "Debe").text = "%.2f" % line.debit
                etree.SubElement(item, "Haber").text = "%.2f" % line.credit
                etree.SubElement(item, "Saldo").text = "%.2f" % line.balance

        # Final Balance
        if book.final_balance_ids:
            saldo_final = etree.SubElement(root, "SaldoFinal")
            for line in book.final_balance_ids:
                item = etree.SubElement(saldo_final, "Item")
                etree.SubElement(item, "Cuenta").text = line.account_code or ""
                etree.SubElement(item, "Descripcion").text = line.account_name or ""
                etree.SubElement(item, "Debe").text = "%.2f" % line.debit
                etree.SubElement(item, "Haber").text = "%.2f" % line.credit
                etree.SubElement(item, "Saldo").text = "%.2f" % line.balance

        return etree.tostring(
            root, encoding="utf-8", xml_declaration=True, pretty_print=True
        )
