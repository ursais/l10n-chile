# Chilean Localization for Odoo

This repository contains Chilean localization modules for Odoo 18.0+.

## Modules

### Core Modules

#### l10n_cl_accounting_books
Electronic Accounting Books for Chile (Libro Diario, Libro Mayor, Libro de Inventarios y Balances).
- Compliant with SII regulations
- Export to XML and PDF
- Integration with Odoo accounting

#### l10n_cl_purchase_sales_book
Purchase and Sales Books for Chilean tax compliance.
- Libro de Compras (Purchase Book)
- Libro de Ventas (Sales Book)
- Integration with DTEs
- SII-compliant XML export

### SII Integration Modules

#### l10n_cl_edi_caf_sii
CAF (Folios Authorization) management with SII web services.
- Query available CAF from SII
- Automatic monitoring and alerts
- Low folio warnings

#### l10n_cl_edi_contribuyente
Chilean taxpayer (RUT) validation and verification.
- RUT format validation
- Check digit verification
- SII taxpayer data query (when API available)
- JSON API endpoints

#### l10n_cl_edi_libros
Electronic submission of Purchase and Sales Books to SII.
- Send Libro de Compras to SII
- Send Libro de Ventas to SII
- Track submission status
- Integration with l10n_cl_edi authentication

## Installation

### Requirements

```bash
pip install zeep lxml requests cryptography
```

### Install Modules

1. Update Odoo addons path to include this repository
2. Update apps list in Odoo
3. Install desired modules from Apps menu

## Usage

See each module's README.rst for detailed usage instructions.

## Contributing

This repository follows OCA (Odoo Community Association) guidelines.

### Development

1. Fork the repository
2. Create a feature branch
3. Follow OCA coding standards
4. Add tests (coverage > 80%)
5. Submit pull request

### Code Standards

- Follow PEP 8
- Use OCA module structure
- Write comprehensive tests
- Document all public methods

## License

AGPL-3

## Maintainers

- Open Source Integrators

## Links

- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [SII Chile](https://www.sii.cl)
- [Chilean Electronic Invoicing](https://www.sii.cl/factura_electronica/)
