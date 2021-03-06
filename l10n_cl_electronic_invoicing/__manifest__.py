# Copyright (C) 2019 Konos
# Copyright (C) 2019 Blanco Martín & Asociados
# Copyright (C) 2019 CubicERP
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Electronic Invoicing for Chile",
    "summary": "Get your customer invoices signed by SII.",
    "version": "12.0.1.0.0",
    "category": "Localization/Chile",
    "author": "Daniel Santibáñez Polanco, "
              "Cooperativa OdooCoop, "
              "Konos, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-chile",
    "license": "AGPL-3",
    "depends": [
        "account",
        "purchase",
        "sale_management",
        "l10n_cl_toponym",
        "l10n_cl_chart_of_account",
        "l10n_cl_sii_activity",
        "report_xlsx",
        "portal",
    ],
    "external_dependencies": {
        "python": [
            "chardet",
            "dicttoxml",
            "M2Crypto",
            "num2words",
            "pdf417gen",
            "pysftp",
            "signxml",
            "suds",
            "urllib3",
            "xlsxwriter",
            "xmltodict",
        ]
    },
    "data": [
        "data/sii_responsability.xml",
        "data/ir_cron.xml",
        "data/sii_document_type.xml",
        "data/product_template.xml",
        "data/ir_sequence.xml",
        "data/sii.concept.type.csv",
        "data/sii.document.letter.csv",
        "data/sii.document.class.csv",
        "data/sii.regional.offices.csv",
        "data/res.currency.csv",
        "security/ir.model.access.csv",
        "wizard/journal_config_wizard_view.xml",
        "wizard/masive_send_dte.xml",
        "wizard/masive_dte_process.xml",
        "wizard/masive_dte_accept.xml",
        "wizard/notas.xml",
        "wizard/upload_xml.xml",
        "wizard/validar.xml",
        "views/sii_menuitem.xml",
        "views/invoice_view.xml",
        "views/consumo_folios.xml",
        "views/caf.xml",
        "views/export.xml",
        "views/invoice_view.xml",
        "views/layout.xml",
        "views/libro_compra_venta.xml",
        "views/libro_honorarios.xml",
        "views/mail_dte.xml",
        "views/payment_t_view.xml",
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/sii_activity_description.xml",
        "views/sii_cola_envio.xml",
        "views/sii_regional_offices_view.xml",
        "views/res_users.xml",
        "views/account_journal_sii_document_class_view.xml",
        "views/account_move_line_view.xml",
        "views/account_move_view.xml",
        "views/res_currency_view.xml",
        "views/honorarios.xml",
        "views/invoice_import.xml",
        "views/journal_view.xml",
        "views/report_invoice.xml",
        "views/sii_concept_type_view.xml",
        "views/sii_document_class_view.xml",
        "views/sii_document_letter_view.xml",
        "views/sii_document_type_view.xml",
        "views/sii_optional_type_view.xml",
        "views/sii_responsability_view.xml",
        "views/sii_sucursal_view.xml",
        "views/sii_xml_envio.xml",
        "views/global_descuento_recargo.xml",
        "views/res_config_settings.xml",
        "views/portal_boleta_layout.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "development_status": "Beta",
    "maintainers": ["nelsonramirezs"],
}
