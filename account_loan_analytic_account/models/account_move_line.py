# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "move_id" in vals:
                move = self.env["account.move"].browse(vals["move_id"])
                loan = move.loan_id
                if (
                    "account_id" in vals
                    and loan
                    and vals["account_id"] == loan.interest_expenses_account_id.id
                ):
                    vals["analytic_distribution"] = loan.analytic_distribution
        return super().create(vals_list)

    def write(self, vals):
        if "move_id" in vals:
            move = self.env["account.move"].browse(vals["move_id"])
            loan = move.loan_id
            if (
                "account_id" in vals
                and loan
                and vals["account_id"] == loan.interest_expenses_account_id.id
            ):
                vals["analytic_distribution"] = loan.analytic_distribution
        return super().write(vals)
