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
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = 'sale.order'
    _columns = {'commercial_partner_id': fields.related('partner_id', 'commercial_partner_id',
                                                        string='Commercial Entity', type='many2one',
                                                        relation='res.partner', store=True, readonly=True,
                                                        help="The commercial entity that will be used on Journal\
                                                         Entries for this invoice")
                }

    def action_button_confirm(self, cr, uid, ids, context={}):
        sale_order_obj = self.browse(cr, uid, ids, context=context)[0]
        if context.get('force', False) is not True:
            res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
            if ((sale_order_obj.commercial_partner_id.blocked_customer) is True):
                raise orm.except_orm(_('Warning !'),
                                     _("This customer is blocked or this confirmation implies to blocked it"))
            else:
                return res
        else:
            if (context.get('validate', False) is False):
                context.update({'validate': False, 'force': False})
                values = {'order_id': sale_order_obj.id,
                          }

                wizard_id = self.pool.get('warning.force.sale.order.wizard').create(cr, uid, values, context=context)
                return {
                    'name': _('Force Order'),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'warning.force.sale.order.wizard',
                    'res_id': wizard_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    'context': context,
                }
            else:
                context.update({'validate': False, 'force': False})
                return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)


class warning_force_sale_order_wizard(orm.TransientModel):
    _name = 'warning.force.sale.order.wizard'
    _columns = {'order_id': fields.many2one('sale.order', string='Order', required=True),
                }

    def validate(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)
        if this.order_id.commercial_partner_id.level_amount is None:
            amount = _('Manual Blocking')
        else:
            amount = this.order_id.amount_total
        diff = this.order_id.commercial_partner_id.credit_limit - this.order_id.commercial_partner_id.level_amount
        if (diff > 0):
            amount = amount - diff
        self.pool.get('force.tracking').create(cr, uid, {'user_id': uid,
                                                         'type': 'sale_order',
                                                         'source_document': this.order_id.name,
                                                         'partner_id': this.order_id.partner_id.id,
                                                         'amount': str(amount),
                                                         })
        context.update({'validate': True, 'force': True})
        return self.pool.get('sale.order').action_button_confirm(cr, uid, [this.order_id.id], context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
