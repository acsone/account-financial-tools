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

import openerp.tests.common as common

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class TestAccountCreditLimitSaleStock(common.TransactionCase):

    def setUp(self):
        super(TestAccountCreditLimitSaleStock, self).setUp()

    def test_level3(self):
        partner_id = self.registry('res.partner').create(self.cr,
                                                         self.uid,
                                                         {'name': 'partner_01',
                                                          })
        product_id = self.registry('product.product')\
            .create(self.cr,
                    self.uid,
                    {'name': 'product_test_01',
                        'lst_price': 2000.00,
                     })
        so_id = self.registry('sale.order')\
            .create(self.cr,
                    self.uid,
                    {'partner_id': partner_id,
                     'partner_invoice_id': partner_id,
                     'partner_shipping_id': partner_id,
                     })

        self.registry('sale.order.line')\
            .create(self.cr,
                    self.uid,
                    {'order_id': so_id,
                     'order_partner_id': partner_id,
                     'name': "test",
                     'product_id': product_id,
                     'price_unit': 2000.0
                     })
        self.registry('sale.order').action_button_confirm(self.cr,
                                                          self.uid,
                                                          [so_id],
                                                          {'force': True,
                                                           'validate': True})
        partner_obj = self.registry('res.partner').browse(self.cr,
                                                          self.uid,
                                                          [partner_id])
        self.assertAlmostEquals(partner_obj.credit_limit_level3, 0.0, 3,
                                "Level 3 isn't correct (Assert 1)")

        sale_order_obj = self.registry('sale.order').browse(self.cr,
                                                            self.uid,
                                                            [so_id])
        for picking in sale_order_obj.picking_ids:
            self.registry('stock.picking').force_assign(self.cr,
                                                        self.uid,
                                                        [picking.id])
            self.registry('stock.picking').do_transfer(self.cr,
                                                       self.uid,
                                                       [picking.id])
        partner_obj = self.registry('res.partner').browse(self.cr,
                                                          self.uid,
                                                          [partner_id])
        self.assertAlmostEquals(partner_obj.credit_limit_level3, 2000.0, 2,
                                "Level 3 isn't correct (Assert 2)")

    def test_level4(self):
        partner_id = self.registry('res.partner').create(self.cr,
                                                         self.uid,
                                                         {'name': 'partner_01',
                                                          })
        product_id = self.registry('product.product')\
            .create(self.cr,
                    self.uid,
                    {'name': 'product_test_01',
                     'lst_price': 2000.00,
                     })
        so_id = self.registry('sale.order')\
            .create(self.cr,
                    self.uid,
                    {'partner_id': partner_id,
                     'partner_invoice_id': partner_id,
                     'partner_shipping_id': partner_id,
                     })

        self.registry('sale.order.line').create(self.cr,
                                                self.uid,
                                                {'order_id': so_id,
                                                 'order_partner_id':
                                                    partner_id,
                                                 'name': "test",
                                                 'product_id': product_id,
                                                 'price_unit': 2000.0
                                                 })
        self.registry('sale.order').action_button_confirm(self.cr,
                                                          self.uid,
                                                          [so_id],
                                                          {'force': True,
                                                           'validate': True})
        partner_obj = self.registry('res.partner').browse(self.cr,
                                                          self.uid,
                                                          [partner_id])
        self.assertAlmostEquals(partner_obj.credit_limit_level4, 2000.0, 3,
                                "Level 4 isn't correct")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
