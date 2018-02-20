# -*- coding: utf-8 -*-
#
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{
    "name": "Account Credit Limit Sale Stock",
    "version": "8.0.1.0.1",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "images": [],
    "category": "Accounting",
    "depends": [
                "account_credit_limit",
                "sale",
                "stock",
                "sale_stock"],
    "description": """
Account Credit Limit Sale Stock
==============================
Compute 2 others level of credit limit
- Level 3 : All delivery order which is transfer but not invoiced
- level 4 : All delivery order which is ready to delivered but not invoiced

Select a level for a customer

If the amount of the selected level is greater than credit limit of
this customer, it is blocked

If a customer is blocked, a compute field in res_partner is True and you
can't confirm a sale ordre or transfer a
delivery order. You can bypass it by clicking on force confirm button or
force tranfer button.
If you click on this button, the forcing is register in reporting menu ->
credit limit forcing

""",
    "data": [
        "view/res_partner_view.xml",
        "view/stock_view.xml",
        "view/sale_view.xml",
        "view/account_credit_limit_sale_stock.xml",
        "report/force_tracking_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "test": [],
    "licence": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
