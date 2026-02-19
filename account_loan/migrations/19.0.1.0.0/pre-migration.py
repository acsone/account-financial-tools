# Copyright 2026 Acsone (http://acsone.eu)
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Rename loan_type into loan_method (on account.loan model)")
    openupgrade.rename_fields(
        env,
        [
            ("account.loan", "account_loan", "loan_type", "loan_method"),
        ],
    )
