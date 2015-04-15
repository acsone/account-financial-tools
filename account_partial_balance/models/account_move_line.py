# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_partial_balance,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_partial_balance is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_partial_balance is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_partial_balance.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    def _query_get(self, cr, uid, obj='l', context=None):
        res = super(AccountMoveLine, self)._query_get(cr, uid, obj=obj,
                                                      context=context)
        if context.get('query', False) and context.get('query_params', False):
            res += 'AND' + context.get('query') % context.get('query_params')
        return res
