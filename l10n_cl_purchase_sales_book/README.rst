======================================
Chile - Purchase and Sales Books
======================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--chile-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-chile/tree/18.0/l10n_cl_purchase_sales_book
    :alt: OCA/l10n-chile

|badge1| |badge2| |badge3|

This module provides Electronic Purchase and Sales Books for Chilean localization,
integrated with Chilean DTEs (Electronic Tax Documents).

**Features**:

* Purchase Book (Libro de Compras) generation from supplier invoices
* Sales Book (Libro de Ventas) generation from customer invoices
* Integration with Chilean DTEs (l10n_cl_edi)
* Export to XML format (SII compatible)
* PDF reports for printing
* Automatic validation and totals calculation

**Table of contents**

.. contents::
   :local:

Usage
=====

Generate Purchase Book
-----------------------

1. Go to **Accounting > Reporting > Purchase/Sales Books > Generate Book**
2. Select:
   - Book Type: Purchase Book
   - Period (From/To Date)
   - Export Format (XML or PDF)
3. Click **Generate and Export**

Generate Sales Book
-------------------

1. Go to **Accounting > Reporting > Purchase/Sales Books > Generate Book**
2. Select:
   - Book Type: Sales Book
   - Period (From/To Date)
   - Export Format (XML or PDF)
3. Click **Generate and Export**

The system will:
* Collect all posted invoices for the period
* Generate book lines with all required data
* Calculate totals
* Export in the selected format

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-chile/issues>`_.

Credits
=======

Authors
-------

* Open Source Integrators

Contributors
------------

* Open Source Integrators <https://www.opensourceintegrators.com>

Maintainers
-----------

This module is maintained by the OCA.

This module is part of the `OCA/l10n-chile <https://github.com/OCA/l10n-chile/tree/18.0/l10n_cl_purchase_sales_book>`_ project on GitHub.

