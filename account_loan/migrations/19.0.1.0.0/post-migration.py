# Copyright 2026 Acsone (http://acsone.eu)
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# If you are comming from Odoo Version < 19.0
# you will needs account_leasing module installed as
# code was extracted while moving from v18 to v19
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    leasing_module = env["ir.module.module"].search([("name", "=", "account_leasing")])
    if not leasing_module.exists():
        _logger.warning(
            "account_leasing module not found in odoo path. Related features"
            "were in account_loan in previous version, consider to install it "
            "or cleanup extra fields"
        )
        return
    _logger.info(
        "Installing account_leasing as that feature were previously part of "
        "account_loan..."
    )
    leasing_module.button_install()
