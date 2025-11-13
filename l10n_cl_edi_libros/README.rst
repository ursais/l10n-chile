====================================
Chile - Electronic Books to SII
====================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--chile-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-chile/tree/18.0/l10n_cl_edi_libros
    :alt: OCA/l10n-chile

|badge1| |badge2| |badge3|

This module extends l10n_cl_purchase_sales_book to send books electronically
to SII (Servicio de Impuestos Internos) via web services.

**Features**:

* Send Purchase Books to SII
* Send Sales Books to SII
* Query submission status
* Integration with SII authentication (same as DTEs)
* Track submission history

**Table of contents**

.. contents::
   :local:

Configuration
=============

1. Ensure l10n_cl_edi is configured with:
   - Digital signature certificate
   - DTE Service Provider (SII, SIITEST, or SIIDEMO)
2. Company must have:
   - Valid Chilean RUT
   - SII Resolution Number and Date

Usage
=====

Send Purchase Book
------------------

1. Generate a Purchase Book (via l10n_cl_purchase_sales_book)
2. Click **Send to SII** button
3. System will:
   - Generate SII-compliant XML
   - Sign with digital certificate
   - Send to SII web service
   - Track submission status

Send Sales Book
---------------

1. Generate a Sales Book (via l10n_cl_purchase_sales_book)
2. Click **Send to SII** button
3. Follow same process as purchase book

Verify Status
-------------

For books in "Ask For Status" state:

1. Click **Verify Status** button
2. System will query SII for current status
3. Status will be updated automatically

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

This module is part of the `OCA/l10n-chile <https://github.com/OCA/l10n-chile/tree/18.0/l10n_cl_edi_libros>`_ project on GitHub.

