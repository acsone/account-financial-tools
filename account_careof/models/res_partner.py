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

from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_account_careof_partner(self, current_date=False):
        self.ensure_one()
        if not current_date:
            current_date = datetime.now()\
                .strftime(DEFAULT_SERVER_DATE_FORMAT)
        relation_type_id = self.env['ir.model.data']\
            .xmlid_to_res_id('account_careof.relation_account_careof',
                             raise_if_not_found=True)
        domain_relation = [('this_partner_id', '=', self.id),
                           ('type_id', '=', relation_type_id),
                           ('record_type', '=', 'a')]
        domain_date = ['&',
                       '|',
                       ('date_start', '<=', current_date),
                       ('date_start', '=', False),
                       '|',
                       ('date_end', '>=', current_date),
                       ('date_end', '=', False)]
        domain_relation.extend(domain_date)
        care_off = self.env['res.partner.relation.all'].search(domain_relation)
        return care_off.id and care_off.other_partner_id or\
            self.env['res.partner']
