# -*- coding: utf-8 -*-
# Author: Vincent Renaville
# Copyright 2013 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountTaxDeclarationAnalysis(models.TransientModel):
    _name = 'account.vat.declaration.analysis'
    _description = 'Account Vat Declaration'

    start_date = fields.Date(required=True,)
    end_date = fields.Date(required=True,)

    @api.multi
    def show_vat(self):
        self.ensure_one()
        domain = [('date', '>=', self.start_date),
                  ('date', '<=', self.end_date)]
        action = self.env.ref('account_tax_analysis.action_view_tax_analysis')
        action_fields = action.read()[0]
        action_fields['domain'] = domain
        return action_fields
