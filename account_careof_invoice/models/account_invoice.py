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

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('partner_id')
    @api.one
    def _compute_account_careof_partner_id(self):
        if self.type not in ['out_invoice', 'out_refund']:
            self.account_careof_partner_id = False
        elif self.partner_id.id:
            self.account_careof_partner_id = self.partner_id\
                .get_account_careof_partner(self.date_invoice)

    account_careof_partner_id = fields.Many2one(
        compute='_compute_account_careof_partner_id',
        comodel_name='res.partner', string='Care Of')
