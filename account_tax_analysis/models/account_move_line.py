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
                 "company_id.partner_id.lang")
    def _compute_analysis_tax(self):
        companies = self.mapped("company_id")
        for company in companies:
            lines = self.filtered(lambda s, c=company: s.company_id == c)
            lang_lines = lines
            if company.partner_id.lang:
                lang_lines = lines.with_context(lang=company.partner_id.lang)
            for lang_line in lang_lines:

                # computed value must be assign without a with_context()
                line = lines.filtered(lambda s, o=lang_line: s == o)

                line.analysis_tax = (
                    lang_line.tax_line_id.description or
                    ', '.join(sorted(lang_line.tax_ids.mapped('description'))))
