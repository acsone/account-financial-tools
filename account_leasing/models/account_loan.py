# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


class AccountLoan(models.Model):
    _inherit = "account.loan"

    loan_type = fields.Selection(
        selection_add=[("leasing", "Leasing")],
        ondelete={"leasing": "set default"},
        readonly=False,
    )
    leased_asset_account_id = fields.Many2one(
        "account.account",
        domain="[('company_ids', '=', company_id)]",
    )
    long_term_journal_id = fields.Many2one(
        "account.journal",
        domain="[('company_id', '=', company_id),('type', '=', 'general')]",
        readonly=True,
        check_company=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Loan product",
        help="Product where the amount of the loan will be assigned when the "
        "invoice is created",
    )
    interests_product_id = fields.Many2one(
        "product.product",
        string="Interest product",
        help="Product where the amount of interests will be assigned when the "
        "invoice is created",
    )
    post_invoice = fields.Boolean(
        default=True, help="Invoices will be posted automatically"
    )

    @api.constrains("loan_type", "loan_amount")
    def _contrains_no_negative_leasing(self):
        negative_leasing = self.filtered(
            lambda loan: loan.loan_type == "leasing" and loan.loan_amount < 0
        )
        if negative_leasing:
            raise ValidationError(
                self.env._(
                    "Negative leasing is not supported, loan(s): %s",
                    negative_leasing.mapped("name"),
                )
            )

    @api.depends("loan_amount")
    def _compute_loan_type(self):
        leasing = self.filtered(lambda loan: loan.loan_type == "leasing")
        loan = self - leasing
        res = super(AccountLoan, loan)._compute_loan_type()
        leasing.loan_type = "leasing"
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # as loan_type is now setable by the user, the api.depends
        # is compute method is triggered only if we are not setting
        # the value which is always the case with the default value
        loans = super().create(vals_list)
        loans._compute_loan_type()
        return loans

    @api.depends("loan_type")
    def _compute_journal_type(self):
        for record in self:
            if record.loan_type == "leasing":
                record.journal_type = "purchase"
            else:
                record.journal_type = "general"

    @api.onchange("journal_type", "company_id")
    def _onchange_loan_type(self):
        self.journal_id = self.env["account.journal"].search(
            Domain(
                [
                    ("company_id", "=", self.company_id.id),
                    ("type", "=", self.journal_type),
                ]
            ),
            limit=1,
        )
        self.residual_amount = 0.0

    def view_account_invoices(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        result["domain"] = Domain(
            [("loan_id", "=", self.id), ("move_type", "=", "in_invoice")]
        )
        return result

    @api.model
    def _generate_leasing_entries(self, date):
        res = []
        for record in self.search(
            Domain([("state", "=", "posted"), ("loan_type", "=", "leasing")])
        ):
            res += record.line_ids.filtered(
                lambda r: r.date <= date and not r.move_ids
            )._generate_invoice()
        return res

    @api.model
    def _loan_and_borrow_domain(self):
        return Domain("loan_type", "!=", "leasing")
