# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    analysis_tax = fields.Char(compute="_compute_analysis_tax", store=True)
    account_type = fields.Many2one(related='account_id.user_type_id',
                                   store=True)

    @api.multi
    @api.depends("tax_line_id", "tax_ids")
    def _compute_analysis_tax(self):
        for line, in self:
            line.analysis_tax = (
                line.tax_line_id.analysis_name or
                ', '.join(sorted(line.tax_ids.mapped('analysis_name'))))
