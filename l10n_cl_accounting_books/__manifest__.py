{
    "name": "Chile - Accounting Books",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations/Reporting",
    "summary": "Electronic Accounting Books for Chile (SII) - Journal, Ledger and Inventory Books",
    "author": "Odoo Community Association (OCA)",
    "maintainer": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-chile",
    "license": "AGPL-3",
    "depends": [
        # Odoo
        "account",
        # OCA
        "l10n_cl",
    ],
    "external_dependencies": {
        "python": ["lxml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/account_book_data.xml",
        "views/account_journal_book_views.xml",
        "views/account_ledger_book_views.xml",
        "views/account_inventory_book_views.xml",
        "views/account_book_menus.xml",
        "wizards/account_book_export_wizard_views.xml",
        "reports/account_journal_book_report.xml",
        "reports/account_ledger_book_report.xml",
        "reports/account_inventory_book_report.xml",
    ],
    "demo": [
        "demo/account_book_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
