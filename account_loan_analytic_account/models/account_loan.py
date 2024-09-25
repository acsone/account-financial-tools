# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountLoan(models.Model):
    _name = "account.loan"
    _inherit = ["account.loan", "analytic.mixin"]

    def write(self, vals):
        ret = super().write(vals)
        for rec in self:
            if "analytic_distribution" in vals.keys():
                move_lines = rec.move_ids.mapped("line_ids").filtered(
                    lambda l: l.account_id.id == rec.interest_expenses_account_id.id
                )
                move_lines.write(
                    {"analytic_distribution": vals["analytic_distribution"]}
                )
        return ret
