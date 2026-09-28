# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged

from .common import AccountAccountUsedCommon


@tagged("post_install", "-at_install")
class TestAccountAccountModificationReasonTour(AccountAccountUsedCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reason = cls.env["account.account.modification.reason"].create(
            {"name": "Tour reason"}
        )
        cls._create_move(cls.account, post=True)

    def test_tour(self):
        self.start_tour(
            f"/odoo/action-account.action_account_form/{self.account.id}",
            "account_account_control",
            login=self.env.user.login,
        )
        self.assertEqual(self.account.name, "Modified by tour")
        self.assertEqual(self.account.modification_reason_id, self.reason)
