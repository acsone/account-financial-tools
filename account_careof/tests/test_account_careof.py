# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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
##############################################################################

import openerp.tests.common as common
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.partner_relations.model import PADDING


class TestAccountCareOf(common.TransactionCase):

    def setUp(self):
        super(TestAccountCareOf, self).setUp()
        self.careoff_relation =\
            self.env.ref('account_careof.relation_account_careof')
        self.care_off_all_obj = self.env['res.partner.relation']
        self.partner01 = self.env.ref('base.res_partner_1')
        self.partner02 = self.env.ref('base.res_partner_2')
        self.partner03 = self.env.ref('base.res_partner_3')
        today = datetime.now()
        self.date_today = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        tomorrow = (today + timedelta(days=1))
        self.date_tomorrow = tomorrow.strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = (today - timedelta(days=1))
        self.date_yesterday = yesterday.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def test_no_relation(self):
        # Just call the method to get care of the partner
        partner_cutoff = self.partner01.get_account_careof_partner()
        self.assertEqual(len(partner_cutoff.ids), 0)

    def test_one_relation(self):
        vals = {
            'left_partner_id': self.partner01.id,
            'right_partner_id': self.partner02.id,
            'type_selection_id': (self.careoff_relation.id * PADDING)
        }
        self.care_off_all_obj.create(vals)
        partner_cutoff = self.partner01.get_account_careof_partner()
        self.assertEqual(partner_cutoff, self.partner02)

    def test_date_relation(self):
        vals = {
            'left_partner_id': self.partner01.id,
            'right_partner_id': self.partner02.id,
            'type_selection_id': (self.careoff_relation.id * PADDING),
            'date_start': self.date_yesterday,
        }
        relation = self.care_off_all_obj.create(vals)
        partner_cutoff = self.partner01.get_account_careof_partner()
        self.assertEqual(partner_cutoff, self.partner02)
        relation.date_end = self.date_yesterday
        partner_cutoff = self.partner01.get_account_careof_partner()
        self.assertEqual(len(partner_cutoff.ids), 0)
        vals = {
            'left_partner_id': self.partner01.id,
            'right_partner_id': self.partner03.id,
            'type_selection_id': (self.careoff_relation.id * PADDING),
            'date_start': self.date_tomorrow,
        }
        relation = self.care_off_all_obj.create(vals)
        partner_cutoff = self.partner01.get_account_careof_partner()
        self.assertEqual(len(partner_cutoff.ids), 0)
        relation.date_start = self.date_today
        partner_cutoff = self.partner01.get_account_careof_partner()
        self.assertEqual(partner_cutoff, self.partner03)
