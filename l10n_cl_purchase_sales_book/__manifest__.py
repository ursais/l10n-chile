{
    "name": "Chile - Purchase and Sales Books",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/l10n-chile",
    "category": "Accounting/Localizations/Reporting",
    "summary": "Electronic Purchase and Sales Books for Chile (SII) integrated with DTEs",
    "depends": [
        # Odoo
        "account",
        # OCA
        "l10n_cl",
        # Enterprise (optional but recommended)
        "l10n_cl_edi",
    ],
    "external_dependencies": {
        "python": ["lxml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/account_purchase_book_views.xml",
        "views/account_sales_book_views.xml",
        "views/account_book_menus.xml",
        "wizards/book_export_wizard_views.xml",
        "reports/purchase_book_report.xml",
        "reports/sales_book_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "maintainers": ["ursais"],
}
