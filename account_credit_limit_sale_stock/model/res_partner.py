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

    def _compute_level3(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        stock_move_model = self.pool.get('stock.move')
        for partner in self.browse(cr, uid, ids):
            draft_partner_account_invoice_line = \
                self.pool.get('account.invoice.line')\
                    .search(cr,
                            uid,
                            [('invoice_id.commercial_partner_id',
                              '=', partner.commercial_partner_id.id),
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
                          '=', partner.commercial_partner_id.id), '|',
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
            res[partner.id] = partner.credit_limit_level2 + credit
        return res

    def _compute_level4(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids):
            draft_partner_account_invoice_line = \
                self.pool.get('account.invoice.line')\
                    .search(cr,
                            uid,
                            [('invoice_id.commercial_partner_id', '=',
                              partner.commercial_partner_id.id),
                             ('invoice_id.state', '=', 'draft')]
                            )
            stock_move_ids = \
                self.pool.get('stock.move')\
                    .search(cr,
                            uid,
                            [('procurement_id.sale_line_id.order_id.'
                              'commercial_partner_id', '=',
                              partner.commercial_partner_id.id),
                             ('picking_id.state', 'not in',
                              ('draft', 'cancel')),
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
            res[partner.id] = partner.credit_limit_level2 + somme
        return res

    def _is_blocked(self, cr, uid, ids, field_name, arg, context=None):
        res = super(res_partner, self)._is_blocked(cr,
                                                   uid,
                                                   ids,
                                                   field_name,
                                                   arg,
                                                   context=context)
        for partner in self.browse(cr, uid, ids):
            if res[partner.id] is False:
                blocked = False
                if (partner.level3_blocking is True):
                    if (partner.credit_limit_level3 > partner.credit_limit):
                        blocked = True
                elif (partner.level4_blocking is True):
                    if ((partner.credit_limit_level4 + 1.0) >
                            partner.credit_limit):
                        blocked = True
                res[partner.id] = blocked
        return res

    def _compute_amount_blocked(self, cr, uid, ids, field_name, arg,
                                context=None):
        res = super(res_partner, self)._compute_amount_blocked(cr,
                                                               uid,
                                                               ids,
                                                               field_name,
                                                               arg,
                                                               context=context)
        for partner in self.browse(cr, uid, ids):
            if res[partner.id] == "N/A":
                if partner.blocked_customer:
                    if (partner.level3_blocking is True):
                        blocked = partner.credit_limit_level3 - \
                            partner.credit_limit
                    elif (partner.level4_blocking is True):
                        blocked = partner.credit_limit_level4 - \
                            partner.credit_limit
                else:
                    blocked = "N/A"
                res[partner.id] = str(blocked)
        return res

    def _level_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = super(res_partner, self)._level_amount(cr,
                                                     uid,
                                                     ids,
                                                     context=context)
        for partner in self.browse(cr, uid, ids):
            if res[partner.id] is None:
                if (partner.level3_blocking is True):
                    res[partner.id] = partner.credit_limit_level3
                elif (partner.level4_blocking is True):
                    res[partner.id] = partner.credit_limit_level4
        return res

    _columns = {
        'credit_limit_level3':
            fields.function(_compute_level3, type="float",
                            string='CL exceeded on INV and CDO'),
        'credit_limit_level4':
            fields.function(_compute_level4, type="float",
                            string='CL exceeded on INV, CDO and Open SO'),
        'level3_blocking': fields.boolean(string='Level 3 Blocking'),
        'level4_blocking': fields.boolean(string='Level 4 Blocking'),
        'blocked_customer': fields.function(_is_blocked,
                                            type='boolean',
                                            string="Blocked Customer"),
        'amount_blocked': fields.function(_compute_amount_blocked,
                                          type='char',
                                          string='Amount Blocked'),
        'level_amount': fields.function(_level_amount, type='float',
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
