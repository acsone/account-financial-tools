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
from openerp import netsvc
from datetime import datetime, timedelta

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class TestAccountCreditLimit(common.TransactionCase):

    def setUp(self):
        super(TestAccountCreditLimit, self).setUp()

    def test_level1(self):
        partner_id = \
            self.registry('res.partner').create(self.cr,
                                                self.uid,
                                                {'name': 'partner_01'})
        product_id = \
            self.registry('product.product').create(self.cr,
                                                    self.uid,
                                                    {'name': 'product_test_01',
                                                     'lst_price': 2000.00,
                                                     })
        today = datetime.now()
        date = today.strftime('%Y-%m-%d')
        invoice_id = self.registry('account.invoice')\
            .create(self.cr,
                    self.uid,
                    {'partner_id': partner_id,
                     'date_due': date,
                     'account_id':
                     self.ref('account.a_recv'),
                     'journal_id':
                     self.ref('account.sales_journal'),
                     })
        self.registry('account.invoice.line')\
            .create(self.cr,
                    self.uid,
                    {'invoice_id': invoice_id,
                     'name': 'test',
                     'account_id': self.ref('account.a_sale'),
                     'price_unit': 2000.00,
                     'quantity': 1,
                     'product_id': product_id,
                     })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            self.uid, 'account.invoice', invoice_id, 'invoice_open', self.cr)
        partner_obj = self.registry('res.partner').browse(self.cr,
                                                          self.uid,
                                                          [partner_id])
        self.assertAlmostEquals(partner_obj.credit_limit_level1, 0.0, 2,
                                "Level 1 isn't correct")
        yesterday = datetime.now() - timedelta(days=1)
        date = yesterday.strftime('%Y-%m-%d')
        invoice_id = self.registry('account.invoice')\
            .create(self.cr,
                    self.uid,
                    {'partner_id': partner_id,
                     'date_due': date,
                     'account_id': self.ref('account.a_recv'),
                     'journal_id':
                     self.ref('account.sales_journal'),
                     })
        self.registry('account.invoice.line').\
            create(self.cr,
                   self.uid,
                   {'invoice_id': invoice_id,
                    'name': 'test',
                    'account_id': self.ref('account.a_sale'),
                    'price_unit': 2000.00,
                    'quantity': 1,
                    'product_id': product_id,
                    })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            self.uid, 'account.invoice', invoice_id, 'invoice_open', self.cr)
        partner_obj = self.registry('res.partner').browse(self.cr,
                                                          self.uid,
                                                          [partner_id])
        self.assertAlmostEquals(partner_obj.credit_limit_level1, 2000.0, 2,
                                "Level 1 isn't correct")

    def test_level2(self):
        partner_id = self.registry('res.partner').create(self.cr,
                                                         self.uid,
                                                         {'name':
                                                          'partner_01'})
        product_id = self.registry('product.product')\
            .create(self.cr,
                    self.uid,
                    {'name': 'product_test_01',
                        'lst_price': 2000.00,
                     })
        today = datetime.now()
        date = today.strftime('%Y-%m-%d')
        invoice_id = self.registry('account.invoice')\
            .create(self.cr,
                    self.uid,
                    {'partner_id': partner_id,
                     'date_due': date,
                     'account_id': self.ref('account.a_recv'),
                     'journal_id':
                     self.ref('account.sales_journal'),
                     })
        self.registry('account.invoice.line')\
            .create(self.cr,
                    self.uid,
                    {'invoice_id': invoice_id,
                     'name': 'test',
                     'account_id': self.ref('account.a_sale'),
                     'price_unit': 2000.00,
                     'quantity': 1,
                     'product_id': product_id,
                     })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            self.uid, 'account.invoice', invoice_id, 'invoice_open', self.cr)
        partner_obj = self.registry('res.partner').browse(self.cr,
                                                          self.uid,
                                                          [partner_id])
        self.assertAlmostEquals(partner_obj.credit_limit_level2, 2000.0, 2,
                                "Level 2 isn't correct")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
