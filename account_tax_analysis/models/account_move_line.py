# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    analysis_tax = fields.Char(
        string="Analysis Tax",
        compute="_compute_analysis_tax",
        store=True,
    )
    account_type = fields.Many2one(
        string="Account Type",
        related='account_id.user_type_id',
        readonly=True,
        store=True,
    )

    @api.multi
    @api.depends("tax_line_id", "tax_ids", "company_id")
    def _compute_analysis_tax(self):
        companies = self.mapped("company_id")
        for company in companies:
            lines = self.filtered(lambda s: s.company_id == company)
            lang_lines = lines
            if (company.partner_id.lang and
                    company.partner_id.lang != self.env.user.partner_id.lang):
                lang_lines = lines.with_context(lang=company.partner_id.lang)
            for line, lang_line in zip(lines, lang_lines):
                line.analysis_tax = (
                    lang_line.tax_line_id.analysis_name or
                    ', '.join(sorted(
                        lang_line.tax_ids.mapped('analysis_name'))))

    def action_show_invoice(self):
        if len(self) != 1 or not self.invoice_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.invoice_id.id,
            'res_model': 'account.invoice',
        }
