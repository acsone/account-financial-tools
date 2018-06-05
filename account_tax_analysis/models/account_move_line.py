# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    analysis_tax = fields.Char(compute="_compute_analysis_tax", store=True)

    @api.multi
    @api.depends("tax_line_id.description",
                 "tax_ids.description",
                 "company_id.partner_id.lang")
    def _compute_analysis_tax(self):
        for line in self:
            lang_line = line
            if line.company_id.partner_id.lang:
                lang_line = line.with_context(
                    lang=line.company_id.partner_id.lang)
            line.analysis_tax = (
                lang_line.tax_line_id.description or
                ', '.join(sorted(lang_line.tax_ids.mapped('description'))))
