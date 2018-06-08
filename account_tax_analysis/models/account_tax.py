# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountTax(models.Model):

    _inherit = 'account.tax'

    analysis_name = fields.Char(compute="_compute_analysis_name", store=True)

    @api.multi
    @api.depends("name", "description", "company_id")
    def _compute_analysis_name(self):
        companies = self.mapped("company_id")
        for company in companies:
            taxes = self.filtered(lambda s: s.company_id == company)
            lang_taxes = taxes
            if (company.partner_id.lang and
                    company.partner_id.lang != self.env.user.partner_id.lang):
                lang_taxes = taxes.with_context(lang=company.partner_id.lang)
            for tax, lang_tax in zip(taxes, lang_taxes):
                if tax.description:
                    tax.analysis_name = "%s - %s" % (lang_tax.name,
                                                     lang_tax.description)
                else:
                    tax.analysis_name = lang_tax.name
