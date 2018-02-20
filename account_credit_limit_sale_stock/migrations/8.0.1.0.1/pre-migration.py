# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging


logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    query = "ALTER TABLE sale_order_line ADD COLUMN has_invoice_lines " \
            "BOOLEAN DEFAULT FALSE"
    cr.execute(query)
    query = "SELECT distinct order_line_id FROM sale_order_line_invoice_rel " \
            "WHERE invoice_id IS NOT NULL"

    cr.execute(query)
    res = [r[0] for r in cr.fetchall()]
    if res:
        query = "UPDATE sale_order_line SET has_invoice_lines=True " \
                "WHERE id in %s"
        cr.execute(query, (tuple(res),))
