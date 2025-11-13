{
    "name": "Chile - CAF Query from SII",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/l10n-chile",
    "category": "Accounting/Localizations",
    "summary": "Query and manage CAF (Folios Authorization) from SII web services",
    "depends": [
        # Enterprise
        "l10n_cl_edi",
    ],
    "external_dependencies": {
        "python": ["zeep", "lxml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/l10n_cl_caf_sii_views.xml",
        "views/l10n_cl_caf_sii_menu.xml",
        "wizards/solicitar_caf_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "maintainers": ["ursais"],
}
