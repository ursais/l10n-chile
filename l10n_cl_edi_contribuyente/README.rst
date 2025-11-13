===============================
Chile - Taxpayer Validation
===============================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--chile-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-chile/tree/18.0/l10n_cl_edi_contribuyente
    :alt: OCA/l10n-chile

|badge1| |badge2| |badge3|

This module provides Chilean RUT (Rol Único Tributario) validation and taxpayer
data verification for Odoo.

**Features**:

* Automatic RUT format validation
* RUT check digit verification
* Partner data validation with SII (when available)
* JSON API endpoints for RUT validation
* Auto-complete partner data from SII

**Table of contents**

.. contents::
   :local:

Configuration
=============

No special configuration is required. The module extends the partner form
for Chilean partners.

Usage
=====

Manual Validation
-----------------

1. Go to **Contacts**
2. Open or create a Chilean partner (Country = Chile)
3. Enter the RUT in the VAT field (format: 12345678-9)
4. Click **Validate with SII** button to verify with SII services
5. The system will:
   - Validate RUT format and check digit
   - Query SII for taxpayer data (when API available)
   - Auto-complete partner information

Automatic Validation
---------------------

The module automatically validates RUT format when:

* Creating a new Chilean partner
* Updating VAT field of Chilean partner
* The validation happens client-side and server-side

API Endpoints
-------------

JSON endpoints are available for integration:

* ``/l10n_cl/validate_rut`` - Validate RUT
* ``/l10n_cl/format_rut`` - Format RUT to standard format

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

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is part of the `OCA/l10n-chile <https://github.com/OCA/l10n-chile/tree/18.0/l10n_cl_edi_contribuyente>`_ project on GitHub.

You are welcome to contribute.

