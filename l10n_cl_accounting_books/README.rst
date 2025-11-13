Chile - Accounting Books
========================

This module generates the mandatory accounting books required by SII (Servicio de Impuestos Internos).

Features
--------

* **Journal Book (Libro Diario)**: Chronological record of all accounting entries
* **Ledger Book (Libro Mayor)**: Movements grouped by account
* **Inventory and Balance Book (Libro de Inventario y Balances)**: Initial and final balances
* XML export for SII submission
* Date range filtering
* Journal filtering
* Balance validation

Installation
------------

Install the module as usual.

Configuration
-------------

No specific configuration needed. The module uses the company's accounting setup.

Usage
-----

1. Go to **Accounting > Accounting Books**
2. Select the type of book you want to generate:
   - **Journal Book**: For chronological record
   - **Ledger Book**: For account-based movements
   - **Inventory Book**: For initial and final balances
3. Create a new book and set:
   - Date range (From Date / To Date)
   - Optional: Filter by specific journals or accounts
4. Click **Generate** to create the book
5. Review the generated lines
6. Click **Export XML** to download the file for SII submission

Known Issues / Roadmap
----------------------

* Electronic signature integration (planned)
* Direct SII submission (planned)
* PDF reports enhancement (planned)
* Validation against SII format (planned)

Credits
-------

Authors
~~~~~~~

* Odoo Community Association (OCA)

Contributors
~~~~~~~~~~~~

* FOSSA Team

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.



