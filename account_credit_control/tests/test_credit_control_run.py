# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
from datetime import datetime
from dateutil import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestCreditControlRun(TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestCreditControlRun, self).setUp()

        journal = self.env['account.invoice']._default_journal()
        account = self.env.ref('__setup__.account_400000')
        analytic_account = self.env.ref('__setup__.account_701000')
        payment_term = self.env.ref('account.account_payment_term_immediate')

        product = self.env['product.product'].create({
            'name': 'Product test'
        })

        self.policy = \
            self.env.ref('account_credit_control.credit_control_3_time')
        self.policy.write({
            'account_ids': [(6, 0, [account.id])]
        })

        partner = self.env['res.partner'].create({
            'name': 'Partner',
            'credit_policy_id': self.policy.id,
        })

        date_invoice = datetime.today() - relativedelta.relativedelta(years=1)
        self.invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'journal_id': journal.id,
            'type': 'out_invoice',
            'payment_term_id': payment_term.id,
            'date_invoice': fields.Datetime.to_string(date_invoice),
            'date_due': fields.Datetime.to_string(date_invoice),
        })

        self.invoice.invoice_line_ids.create({
            'invoice_id': self.invoice.id,
            'product_id': product.id,
            'name': product.name,
            'account_id': analytic_account.id,
            'quantity': 5,
            'price_unit': 100,
        })

        # Validate the invoice
        self.invoice.action_invoice_open()

    def test_check_run_date(self):
        """
        Create a control run older than the last control run
        :return:
        """
        control_run = self.env['credit.control.run'].create({
            'date': fields.Date.today(),
            'policy_ids': [(6, 0, [self.policy.id])]
        })

        with self.assertRaises(UserError):
            previous_date = datetime.today() - \
                            relativedelta.relativedelta(days=15)
            previous_date_str = fields.Date.to_string(previous_date)
            control_run._check_run_date(previous_date_str)

    def test_generate_credit_lines(self):
        """
        Test the method generate_credit_lines
        :return:
        """
        control_run = self.env['credit.control.run'].create({
            'date': fields.Date.today(),
            'policy_ids': [(6, 0, [self.policy.id])]
        })

        control_run.with_context(lang='en_US').generate_credit_lines()

        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, 'done')

        report_regex = \
            r'<p>Policy "<b>%s</b>" has generated <b>' \
            r'\d+ Credit Control Lines.</b><br></p>' % self.policy.name
        regex_result = re.match(report_regex, control_run.report)
        self.assertIsNotNone(regex_result)

    def test_multi_credit_control_run(self):
        """
        Generate several control run
        :return:
        """

        six_months = datetime.today() - relativedelta.relativedelta(months=6)
        six_months_str = fields.Date.to_string(six_months)
        three_months = datetime.today() - relativedelta.relativedelta(months=2)
        three_months_str = fields.Date.to_string(three_months)

        # First run
        first_control_run = self.env['credit.control.run'].create({
            'date': six_months_str,
            'policy_ids': [(6, 0, [self.policy.id])]
        })
        first_control_run.with_context(lang='en_US').generate_credit_lines()
        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)

        # Second run
        second_control_run = self.env['credit.control.run'].create({
            'date': three_months_str,
            'policy_ids': [(6, 0, [self.policy.id])]
        })
        second_control_run.with_context(lang='en_US').generate_credit_lines()
        self.assertTrue(len(self.invoice.credit_control_line_ids), 2)

        # Last run
        last_control_run = self.env['credit.control.run'].create({
            'date': fields.Date.today(),
            'policy_ids': [(6, 0, [self.policy.id])]
        })
        last_control_run.with_context(lang='en_US').generate_credit_lines()
        self.assertTrue(len(self.invoice.credit_control_line_ids), 2)
