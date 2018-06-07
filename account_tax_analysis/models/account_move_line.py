# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    analysis_tax = fields.Char(compute="_compute_analysis_tax", store=True)

    @api.multi
    @api.depends("tax_line_id",
                 "tax_ids",
                 "company_id")
    def _compute_analysis_tax(self):
        companies = self.mapped("company_id")
        for company in companies:
            lines = self.filtered(lambda s: s.company_id == company)
            lang_lines = lines
            if (company.partner_id.lang and
                    company.partner_id.lang != self.env.user.partner_id.lang):
                lang_lines = lines.with_context(lang=company.partner_id.lang)
            for line, lang_line in zip(lines, lang_lines):
                if lang_line.tax_line_id.description:
                    line.analysis_tax = lang_line.tax_line_id.description
                else:
                    descriptions = lang_line.tax_ids.mapped('description')
                    if False in descriptions:
                        # remove all False from the descriptions list
                        descriptions = filter(lambda c: c, descriptions)
                    line.analysis_tax = ', '.join(sorted(descriptions))
