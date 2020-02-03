# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    allowed_journal_ids = fields.Many2many(
        string="Allowed journals", comodel_name="account.journal"
    )
