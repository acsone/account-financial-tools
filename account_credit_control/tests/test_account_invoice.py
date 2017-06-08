# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from dateutil import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestAccountInvoice(TransactionCase):
    post_install = True
    at_install = False

    def test_action_cancel(self):
        """
        Test the method action_cancel on invoice
        We will create an old invoice, generate a control run
        and check if I can unlink this invoice
        :return:
        """
        journal = self.env['account.invoice']._default_journal()
        account = self.env.ref('__setup__.account_400000')
        analytic_account = self.env.ref('__setup__.account_701000')
        payment_term = self.env.ref('account.account_payment_term_immediate')

        product = self.env['product.product'].create({
            'name': 'Product test'
        })

        policy = self.env.ref('account_credit_control.credit_control_3_time')
        policy.write({
            'account_ids': [(6, 0, [account.id])]
        })

        partner = self.env['res.partner'].create({
            'name': 'Partner',
            'credit_policy_id': policy.id,
        })

        date_invoice = datetime.today() - relativedelta.relativedelta(years=1)
        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'journal_id': journal.id,
            'type': 'out_invoice',
            'payment_term_id': payment_term.id,
            'date_invoice': fields.Datetime.to_string(date_invoice),
            'date_due': fields.Datetime.to_string(date_invoice),
        })

        invoice.invoice_line_ids.create({
            'invoice_id': invoice.id,
            'product_id': product.id,
            'name': product.name,
            'account_id': analytic_account.id,
            'quantity': 5,
            'price_unit': 100,
        })

        # Validate the invoice
        invoice.action_invoice_open()

        control_run = self.env['credit.control.run'].create({
            'date': fields.Date.today(),
            'policy_ids': [(6, 0, [policy.id])]
        })
        control_run.generate_credit_lines()

        self.assertTrue(len(invoice.credit_control_line_ids), 1)
        control_line = invoice.credit_control_line_ids

        control_marker = self.env['credit.control.marker']
        marker_line = control_marker\
            .with_context(active_model='credit.control.line',
                          active_ids=[control_line.id])\
            ._get_line_ids()

        self.assertIn(control_line, marker_line)

        marker = self.env['credit.control.marker'].create({
            'name': 'to_be_sent',
            'line_ids': [(6, 0, [control_line.id])]
        })
        marker.mark_lines()

        with self.assertRaises(UserError):
            invoice.unlink()
