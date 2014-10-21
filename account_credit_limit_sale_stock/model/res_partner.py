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


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _compute_multi_credit_limit(self, cr, uid, ids, field_name, arg,
                                    context=None):
        res = {}
        fields = ['id', 'commercial_partner_id', 'credit_limit',
                  'manual_blocking', 'level1_blocking', 'level2_blocking',
                  'level3_blocking', 'level4_blocking', 'credit', 'debit']
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
            credit_limit_level3 = self._compute_level3(cr, uid, partner,
                                                       res[partner['id']],
                                                       context=context)
            res[partner['id']].update({'credit_limit_level3':
                                       credit_limit_level3})
            credit_limit_level4 = self._compute_level4(cr, uid, partner,
                                                       res[partner['id']],
                                                       context=context)
            res[partner['id']].update({'credit_limit_level4':
                                       credit_limit_level4})
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

    def _compute_level3(self, cr, uid, partner, values, context=None):
        stock_move_model = self.pool.get('stock.move')
        draft_partner_account_invoice_line = \
            self.pool.get('account.invoice.line')\
                .search(cr,
                        uid,
                        [('invoice_id.commercial_partner_id',
                          '=', partner['commercial_partner_id'][0]),
                         ('invoice_id.state', '=', 'draft')]
                        )
        stock_move_ids = stock_move_model\
            .search(cr,
                    uid,
                    [('picking_id.picking_type_id.code', '=', 'outgoing'),
                     ('state', '=', 'done'),
                     ('procurement_id', '<>', False),
                     ('procurement_id.sale_line_id.order_id.'
                      'commercial_partner_id',
                      '=', partner['commercial_partner_id'][0]), '|',
                     ('procurement_id.sale_line_id.invoice_lines', '=',
                      False),
                     ('procurement_id.sale_line_id.invoice_lines', 'in',
                      draft_partner_account_invoice_line)]
                    )
        credit = 0.0
        for stock_move in stock_move_model.browse(cr, uid, stock_move_ids,
                                                  context=context):
            sale_order_line = stock_move.procurement_id.sale_line_id
            tax_ids = sale_order_line.tax_id
            tax = 1.0
            for tax_id in tax_ids:
                tax = tax + tax_id.amount
            credit = credit + (sale_order_line.price_unit *
                               stock_move.product_qty) * tax
        res = values['credit_limit_level2'] + credit
        return res

    def _compute_level4(self, cr, uid, partner, values, context=None):
        draft_partner_account_invoice_line = \
            self.pool.get('account.invoice.line')\
                .search(cr,
                        uid,
                        [('invoice_id.commercial_partner_id', '=',
                          partner['commercial_partner_id'][0]),
                         ('invoice_id.state', '=', 'draft')]
                        )
        stock_move_ids = \
            self.pool.get('stock.move')\
                .search(cr,
                        uid,
                        [('procurement_id.sale_line_id.order_id.'
                          'commercial_partner_id', '=',
                          partner['commercial_partner_id'][0]),
                         ('picking_id.state', 'not in',
                          ('draft', 'done', 'cancel')),
                         ('procurement_id', '<>', False), '|',
                         ('procurement_id.sale_line_id.invoice_lines',
                          '=', False),
                         ('procurement_id.sale_line_id.invoice_lines',
                          'in', draft_partner_account_invoice_line)]
                        )
        somme = 0.0
        for stock_move in self.pool.get('stock.move')\
            .browse(cr,
                    uid,
                    stock_move_ids,
                    context=context):
            sale_order_line = stock_move.procurement_id.sale_line_id
            tax_ids = sale_order_line.tax_id
            tax = 1.0
            for tax_id in tax_ids:
                tax = tax + tax_id.amount
            somme = somme + sale_order_line.price_subtotal * tax
        res = values['credit_limit_level3'] + somme
        return res

    def _is_blocked(self, cr, uid, partner, values, context=None):
        res = super(res_partner, self)._is_blocked(cr,
                                                   uid,
                                                   partner,
                                                   values,
                                                   context=context)
        if res is False:
            blocked = False
            if (partner['level3_blocking'] is True):
                if (values['credit_limit_level3'] > partner['credit_limit']):
                    blocked = True
            elif (partner['level4_blocking'] is True):
                if ((values['credit_limit_level4'] + 1.0) >
                        partner['credit_limit']):
                    blocked = True
            res = blocked
        return res

    def _compute_amount_blocked(self, cr, uid, partner, values,
                                context=None):
        res = super(res_partner, self)._compute_amount_blocked(cr,
                                                               uid,
                                                               partner,
                                                               values,
                                                               context=context)
        if res == "N/A":
            if values['blocked_customer']:
                if (partner['level3_blocking'] is True):
                    blocked = values['credit_limit_level3'] - \
                        partner['credit_limit']
                elif (partner['level4_blocking'] is True):
                    blocked = values['credit_limit_level4'] - \
                        partner['credit_limit']
            else:
                blocked = "N/A"
            res = str(blocked)
        return res

    def _level_amount(self, cr, uid, partner, values, context=None):
        res = super(res_partner, self)._level_amount(cr,
                                                     uid,
                                                     partner,
                                                     values,
                                                     context=context)
        if res is None:
            if (partner['level3_blocking'] is True):
                res = values['credit_limit_level3']
            elif (partner['level4_blocking'] is True):
                res = values['credit_limit_level4']
        return res

    _columns = {
        'credit_limit_level3':
            fields.function(_compute_multi_credit_limit,
                            multi='compute_creditlimit',
                            type="float",
                            string='CL exceeded on INV and CDO'),
        'credit_limit_level4':
            fields.function(_compute_multi_credit_limit,
                            multi='compute_creditlimit',
                            type="float",
                            string='CL exceeded on INV, CDO and Open SO'),
        'level3_blocking': fields.boolean(),
        'level4_blocking': fields.boolean(),
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
        value = super(res_partner, self).levels_change(cr, uid, ids)
        value['level3_blocking'] = False
        value['level4_blocking'] = False
        return value

    def level3_change(self, cr, uid, ids, boolval):
        value = {}
        res = {}
        if boolval is True:
            value = self.levels_change(cr, uid, ids)
            value['level3_blocking'] = True
            res.update({'value': value})
        return res

    def level4_change(self, cr, uid, ids, boolval):
        value = {}
        res = {}
        if boolval is True:
            value = self.levels_change(cr, uid, ids)
            value['level4_blocking'] = True
            res.update({'value': value})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
