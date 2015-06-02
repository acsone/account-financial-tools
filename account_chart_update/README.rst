.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Detect changes and update the Account Chart from a template
===========================================================

This is a pretty useful tool to update Odoo installations after tax reforms
on the official charts of accounts, or to apply fixes performed on the chart
template.

The wizard:

* Allows the user to compare a chart and a template showing differences
  on accounts, taxes, tax codes and fiscal positions.
* It may create the new account, taxes, tax codes and fiscal positions detected
  on the template.
* It can also update (overwrite) the accounts, taxes, tax codes and fiscal
  positions that got modified on the template.

Installation
============

To install this module, you need to:

 * do this ...

Configuration
=============

To configure this module, you need to:

 * go to ...

Usage
=====

The wizard, accesible from *Accounting > Configuration > Accounts > Update
chart of accounts*, lets the user select what kind of objects must
be checked/updated, and whether old records must be checked for changes and
updates.

It will display all the objects to be created / updated with some information
about the detected differences, and allow the user to exclude records
individually.

Known issues / Roadmap
======================

 * ...
 
Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-financial-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-financial-tools/issues/new?body=module:%20account_chart_update%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Jordi Esteve
* Borja López Soilán
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Joaquín Gutierrez <joaquingpedrosa@gmail.com>
* invitu
* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
