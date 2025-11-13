{
    "name": "Chile - Taxpayer Validation",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/l10n-chile",
    "category": "Accounting/Localizations",
    "summary": "Validate Chilean RUT and taxpayer data with SII services",
    "depends": [
        # Odoo
        "contacts",
        # OCA
        "l10n_cl",
    ],
    "external_dependencies": {
        "python": ["requests", "lxml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "maintainers": ["ursais"],
}
