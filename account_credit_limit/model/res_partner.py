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

from openerp.osv import fields, orm
import time


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _compute_multi_credit_limit(self, cr, uid, ids, field_name, arg,
                                    context=None):
        res = {}
        fields = ['id', 'commercial_partner_id', 'credit_limit',
                  'manual_blocking', 'level1_blocking', 'level2_blocking',
                  'credit', 'debit']
        for partner in self.read(cr, uid, ids, fields):
            res[partner['id']] = {}
            credit_limit_level1 = self._compute_level1(cr, uid, partner,
                                                       context=context)
            res[partner['id']].update({'credit_limit_level1':
                                       credit_limit_level1})
            credit_limit_level2 = self._compute_level2(cr, uid, partner,
                                                       context=context)
            res[partner['id']].update({'credit_limit_level2':
                                       credit_limit_level2})
            blocked_customer = self._is_blocked(cr, uid, partner,
                                                res[partner['id']],
                                                context=context)
            res[partner['id']].update({'blocked_customer': blocked_customer})
            amount_blocked = self._compute_amount_blocked(cr, uid, partner,
                                                          res[partner['id']],
                                                          context=context)
            res[partner['id']].update({'amount_blocked': amount_blocked})
            level_amount = self._level_amount(cr, uid, partner,
                                              res[partner['id']],
                                              context=context)
            res[partner['id']].update({'level_amount': level_amount})
        return res

    def _compute_level1(self, cr, uid, partner, context=None):
        date = time.strftime('%Y-%m-%d', time.localtime())
        account_ids = \
            self.pool.get('account.account').search(cr,
                                                    uid,
                                                    [('type',
                                                      'in',
                                                      ('receivable',
                                                       'payable'))],
                                                    context=context)
        move_line_ids = \
            self.pool.get('account.move.line')\
                .search(cr,
                        uid,
                        [('partner_id.id', '=',
                          partner['commercial_partner_id'][0]),
                         ('account_id.id', 'in', account_ids),
                         ('reconcile_id', '=', False), '|',
                         ('date_maturity', '=', False),
                         ('date_maturity', '<', date)
                         ],
                        context=context)
        somme = 0
        for line in \
            self.pool.get('account.move.line').read(cr,
                                                    uid,
                                                    move_line_ids,
                                                    context=context):
            somme = somme + (line['debit'] - line['credit'])
        return somme

    def _compute_level2(self, cr, uid, partner, context=None):
        return partner['credit']

    def _is_blocked(self, cr, uid, partner, values, context=None):
        blocked = False
        if (partner['level1_blocking'] is True):
            if (values['credit_limit_level1'] > partner['credit_limit']):
                blocked = True
        elif (partner['level2_blocking'] is True):
            if (values['credit_limit_level2'] > partner['credit_limit']):
                blocked = True
        elif (partner['manual_blocking'] is True):
            blocked = True
        return blocked

    def _compute_amount_blocked(self, cr, uid, partner, values, context=None):
        if values['blocked_customer']:
            if (partner['level1_blocking'] is True):
                blocked = values['credit_limit_level1'] - \
                    partner['credit_limit']
            elif (partner['level2_blocking'] is True):
                blocked = values['credit_limit_level2'] - \
                    partner['credit_limit']
            elif (partner['manual_blocking'] is True):
                blocked = "Manual Blocking"
            else:
                blocked = "N/A"
        else:
            blocked = "N/A"
        return str(blocked)

    def _level_amount(self, cr, uid, partner, values, context=None):
        res = None
        if (partner['level1_blocking'] is True):
            res = values['credit_limit_level1']
        elif (partner['level2_blocking'] is True):
            res = values['credit_limit_level2']
        elif (partner['manual_blocking'] is True):
            res = None
        return res

    _columns = {
        'credit_limit_level1': fields.function(_compute_multi_credit_limit,
                                               multi='compute_creditlimit',
                                               type="float",
                                               string='Exceeded due'),
        'credit_limit_level2': fields.function(_compute_multi_credit_limit,
                                               multi='compute_creditlimit',
                                               type="float",
                                               string='CL exceeded on INV'),
        'manual_blocking': fields.boolean(string="Manual Blocking"),
        'level1_blocking': fields.boolean(),
        'level2_blocking': fields.boolean(),
        'blocked_customer': fields.function(_compute_multi_credit_limit,
                                            multi='compute_creditlimit',
                                            type='boolean',
                                            string="Blocked Customer"),
        'amount_blocked': fields.function(_compute_multi_credit_limit,
                                          multi='compute_creditlimit',
                                          type='char',
                                          string='Amount Blocked'),
        'level_amount': fields.function(_compute_multi_credit_limit,
                                        multi='compute_creditlimit',
                                        type='float',
                                        string='Level Amount'),
    }

    def levels_change(self, cr, uid, ids):
        value = {}
        value['level1_blocking'] = False
        value['level2_blocking'] = False
        value['manual_blocking'] = False
        return value

    def level1_change(self, cr, uid, ids, boolval):
        value = {}
        res = {}
        if boolval is True:
            value = self.levels_change(cr, uid, ids)
            value['level1_blocking'] = True
            res.update({'value': value})
        return res

    def level2_change(self, cr, uid, ids, boolval):
        value = {}
        res = {}
        if boolval is True:
            value = self.levels_change(cr, uid, ids)
            value['level2_blocking'] = True
            res.update({'value': value})
        return res

    def manual_blocking_change(self, cr, uid, ids, boolval):
        value = {}
        res = {}
        if boolval is True:
            value = self.levels_change(cr, uid, ids)
            value['manual_blocking'] = True
            res.update({'value': value})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
