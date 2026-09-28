# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import AccountAccountUsedCommon


@tagged("post_install", "-at_install")
class TestAccountAccountModificationReason(AccountAccountUsedCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reason = cls.env["account.account.modification.reason"].create(
            {"name": "Chart of accounts review"}
        )
        cls._create_move(cls.account, post=True)
        # Records created in the current transaction are not tracked
        cls.env.cr.precommit.run()
        cls.account = cls.account.with_context(
            tracking_disable=False, mail_notrack=False
        )

    def _get_last_tracked_fields(self):
        self.env.cr.precommit.run()
        message = self.account.message_ids.sorted("id")[-1:]
        return message.tracking_value_ids.field_id.mapped("name")

    def test_unused_account_no_reason(self):
        self.other_account.name = "New name"
        self.assertEqual(self.other_account.name, "New name")

    def test_used_account_without_reason(self):
        with self.assertRaisesRegex(UserError, "modification reason is required"):
            self.account.name = "New name"

    def test_used_account_sudo_or_skip(self):
        self.account.sudo().name = "New name"
        self.account.with_context(skip_account_modification_reason=True).note = "Note"
        self.assertEqual(self.account.name, "New name")
        self.assertEqual(self.account.note, "Note")

    def test_used_account_reason_tracked(self):
        self.account.write(
            {"name": "New name", "modification_reason_id": self.reason.id}
        )
        self.assertEqual(self.account.modification_reason_id, self.reason)
        self.assertEqual(
            sorted(self._get_last_tracked_fields()),
            ["modification_reason_id", "name"],
        )

    def test_used_account_same_reason_tracked(self):
        self.account.write(
            {"name": "New name", "modification_reason_id": self.reason.id}
        )
        self._get_last_tracked_fields()
        self.account.write({"note": "Note", "modification_reason_id": self.reason.id})
        self.assertEqual(
            sorted(self._get_last_tracked_fields()),
            ["modification_reason_id", "note"],
        )
