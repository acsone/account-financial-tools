# -*- coding: utf-8 -*-
# Copyright 2012-2017 Camptocamp SA
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    """Check on cancelling of an invoice"""
    _inherit = 'account.invoice'

    credit_policy_id = fields.Many2one(
        'credit.control.policy',
        string='Credit Control Policy',
        help="The Credit Control Policy used for this "
             "invoice. If nothing is defined, it will "
             "use the account setting or the partner "
             "setting.",
        readonly=True,
        copy=False,
        groups="account_credit_control.group_account_credit_control_manager,"
               "account_credit_control.group_account_credit_control_user,"
               "account_credit_control.group_account_credit_control_info",
    )

    credit_control_line_ids = fields.One2many(
        'credit.control.line', 'invoice_id',
        string='Credit Lines',
        readonly=True,
        copy=False,
    )
    credit_control_notes = fields.Char(
        compute='_compute_credit_control_notes',
        inverse='_inverse_credit_control_notes',
        readonly=True,
        states={'open': [('readonly', False)]}
    )
    credit_control_date = fields.Date(
        compute='_compute_credit_control_date',
        inverse='_inverse_credit_control_date',
        string='Credit Control Ignore Before',
        readonly=True,
        states={'open': [('readonly', False)]}
    )

    @api.multi
    def _inverse_credit_control_notes(self):
        """
        Set credit control notes on every move line if invoice notes
        have been modified
        :return:
        """
        invoices = self.filtered('move_id')
        # Search all moves once
        moves = invoices._get_all_related_move_line()
        for invoice in invoices:
            invoice_moves = moves.filtered(
                lambda m: m.invoice_id == invoice.id)

            for invoice_move in invoice_moves:
                invoice_move.credit_control_notes =\
                    invoice.credit_control_notes
                break

    @api.multi
    def _compute_credit_control_notes(self):
        invoices = self.filtered('move_id')
        # Search all moves once
        moves = invoices._get_all_related_move_line()
        for invoice in invoices:
            invoice_moves = moves.filtered(
                lambda m: m.invoice_id.id == invoice.id).with_context(
                from_parent_object=True)
            for invoice_move in invoice_moves:
                invoice.credit_control_notes =\
                    invoice_move.credit_control_notes
                break

    @api.model
    def _get_all_related_move_line(self):
        # Search for the payable or receivable account move line
        # (1 for each invoice)
        return self.env['account.move.line'].search([
            ('account_id.internal_type', 'in', ['payable', 'receivable']),
            ('invoice_id', 'in', self.ids)
        ])

    @api.multi
    def _inverse_credit_control_date(self):
        invoices = self.filtered('move_id')
        moves = invoices._get_all_related_move_line()
        for invoice in invoices:
            invoice_moves = moves.filtered(
                lambda m: m.invoice_id.id == invoice.id).with_context(
                from_parent_object=True)
            for invoice_move in invoice_moves:
                invoice_move.credit_control_date = invoice.credit_control_date
                break

    @api.multi
    @api.depends('move_id.line_ids.credit_control_date',
                 'move_id.line_ids.invoice_id')
    def _compute_credit_control_date(self):
        invoices = self.filtered('move_id')
        for invoice in invoices:
            move_line = self._get_all_related_move_line()
            assert len(move_line) == 1
            invoice_moves = move_line.filtered(
                lambda m: m.invoice_id.id == invoice.id)
            for move in invoice_moves:
                invoice.credit_control_date = move.credit_control_date
                # TODO: better implementation
                break

    @api.multi
    def action_cancel(self):
        """Prevent to cancel invoice related to credit line"""
        # We will search if this invoice is linked with credit
        cc_line_obj = self.env['credit.control.line']
        for invoice in self:
            nondraft_domain = [('invoice_id', '=', invoice.id),
                               ('state', '!=', 'draft')]
            cc_nondraft_lines = cc_line_obj.search(nondraft_domain)
            if cc_nondraft_lines:
                raise UserError(
                    _('You cannot cancel this invoice.\n'
                      'A payment reminder has already been '
                      'sent to the customer.\n'
                      'You must create a credit note and '
                      'issue a new invoice.')
                )
            draft_domain = [('invoice_id', '=', invoice.id),
                            ('state', '=', 'draft')]
            cc_draft_line = cc_line_obj.search(draft_domain)
            cc_draft_line.unlink()
        return super(AccountInvoice, self).action_cancel()
