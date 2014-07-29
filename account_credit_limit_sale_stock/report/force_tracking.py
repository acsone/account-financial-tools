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
from datetime import datetime
from openerp.tools.translate import _


class force_tracking(orm.Model):
    _name = "force.tracking"
    _columns = {'user_id': fields.many2one('res.users', string='User', ondelete='cascade'),
                'date_forcing': fields.datetime(string='Date'),
                'type': fields.selection([
                    ('delivery_order', _('Delivery Order')),
                    ('sale_order', _('Sale Order')), ], string='Type'),
                'source_document': fields.char(string='Source Document'),
                'partner_id': fields.many2one('res.partner', string='Customer', required=True),
                'amount': fields.char(string='Amount Forced', required=True),
                }
    _defaults = {
        'date_forcing': fields.datetime.now,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
