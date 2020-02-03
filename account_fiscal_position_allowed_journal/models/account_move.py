# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("fiscal_position_id")
    def _onchange_fiscal_position(self):
        self.ensure_one()
        journal_domain = [
            ("company_id", "=", self.company_id.id),
            ("type", "=?", self.invoice_filter_type_domain),
        ]
        if self.fiscal_position_id:
            if (
                self.journal_id
                and self.journal_id not in self.fiscal_position_id.allowed_journal_ids
            ):
                self.journal_id = False
            if (
                not self.journal_id
                and len(self.fiscal_position_id.allowed_journal_ids) == 1
            ):
                self.journal_id = self.fiscal_position_id.allowed_journal_ids[0]
            journal_domain.append(
                ("id", "in", self.fiscal_position_id.allowed_journal_ids.ids)
            )
        return {"domain": {"journal_id": journal_domain}}

    def post(self):
        if any(
            rec.is_invoice(include_receipts=True)
            and self.fiscal_position_id
            and self.fiscal_position_id.allowed_journal_ids
            and rec.journal_id not in self.fiscal_position_id.allowed_journal_ids
            for rec in self
        ):
            raise UserError(_("The journal is not allowed on the fiscal position."))
        return super().post()
