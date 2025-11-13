{
    "name": "Chile - Electronic Books to SII",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/l10n-chile",
    "category": "Accounting/Localizations",
    "summary": "Send Purchase and Sales Books to SII via web services",
    "depends": [
        # Enterprise
        "l10n_cl_edi",
        # OCA
        "l10n_cl_purchase_sales_book",
    ],
    "external_dependencies": {
        "python": ["zeep", "lxml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/account_purchase_book_views.xml",
        "views/account_sales_book_views.xml",
        "wizards/enviar_libro_sii_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "maintainers": ["ursais"],
}
