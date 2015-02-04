# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, orm, osv
from openerp.tools.translate import _


class ValidateAccountMove(orm.TransientModel):
    _name = "validate.account.move"
    _inherit = "validate.account.move"

    _columns = {
        'journal_ids': fields.many2many('account.journal', string='Journals',
                                        required=True),
        'period_ids': fields.many2many('account.period', string='Periods',
                                       required=True,
                                       domain=[('state', '<>', 'done')]),
        'exclude_move_ids': fields.many2many('account.move',
                                             string='Exclude Journal Entries'),
        # re-define existing fields as non-mandatory
        'journal_id': fields.many2one('account.journal', 'Journal',
                                      required=False),
        'period_id': fields.many2one('account.period', 'Period',
                                     required=False),
    }

    def _get_domain(self, cr, uid, journal_ids, period_ids, exclude_move_ids):
        return [('state', '=', 'draft'),
                ('journal_id', 'in', journal_ids),
                ('period_id', 'in', period_ids),
                ('id', 'not in', exclude_move_ids),
                ]

    def on_change_journal_period(self, cr, uid, ids, journal_ids, period_ids,
                                 exclude_move_ids):
        res = {}
        journal_ids = journal_ids[0][2]
        period_ids = period_ids[0][2]
        exclude_move_ids = exclude_move_ids[0][2]
        domain = [('id', '=', -1)]
        if journal_ids or period_ids:
            domain = self._get_domain(cr, uid, journal_ids,
                                      period_ids, exclude_move_ids)

        res['domain'] = {'exclude_move_ids': str(domain)}
        return res

    def validate_move(self, cr, uid, ids, context=None):
        obj_move = self.pool.get('account.move')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        journal_ids = [journal.id for journal in data.journal_ids]
        period_ids = [period.id for period in data.period_ids]
        exclude_move_ids = [move.id for move in data.exclude_move_ids]
        ids_move = obj_move.search(cr, uid,
                                   self._get_domain(cr, uid,
                                                    journal_ids,
                                                    period_ids,
                                                    exclude_move_ids),
                                   order='date',
                                   context=context)
        if not ids_move:
            raise osv.except_osv(
                _('Warning!'),
                _('Specified journal does not have any account move entries '
                  'in draft state for this period.')
            )
        obj_move.button_validate(cr, uid, ids_move, context=context)
        return {'type': 'ir.actions.act_window_close'}
