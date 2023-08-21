# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ReceivableFollowUpDetail(models.Model):
    _name = "receivable_follow_up.detail"
    _description = "Receivable Follow Up Detail"

    follow_up_id = fields.Many2one(
        string="# Follow Up",
        comodel_name="receivable_follow_up",
        required=True,
        ondelete="cascade",
    )
    invoice_id = fields.Many2one(
        string="# Invoice",
        comodel_name="account.move.line",
        required=True,
        ondelete="restrict",
    )
    partner_id = fields.Many2one(
        string="Partner", related="invoice_id.partner_id", store=True
    )
    currency_id = fields.Many2one(
        string="Currency", related="invoice_id.currency_id", store=True
    )
    date_invoice = fields.Date(string="Date", related="invoice_id.date", store=True)
    date_due = fields.Date(
        string="Date Due", related="invoice_id.date_maturity", store=True
    )
    amount_total = fields.Monetary(
        string="Amount Total", related="invoice_id.debit", store=True
    )
    amount_residual = fields.Monetary(
        string="Amount Residual", related=False, store=True
    )
    amount_collected = fields.Monetary(
        string="Amount Collected", compute="_compute_amount", store=True
    )
    amount_diff = fields.Monetary(
        string="Amount Different", compute="_compute_amount", store=True
    )

    @api.depends(
        "invoice_id",
        "invoice_id.amount_residual_currency",
    )
    def _compute_amount(self):
        for record in self:
            result = 0.0
            criteria = [
                ("debit_move_id", "=", record.invoice_id.id),
                (
                    "credit_move_id.date",
                    ">=",
                    fields.Date.to_string(record.follow_up_id.date_start),
                ),
                (
                    "credit_move_id.date",
                    "<=",
                    fields.Date.to_string(record.follow_up_id.date_end),
                ),
            ]
            for line in self.env["account.partial.reconcile"].search(criteria):
                result += abs(line.credit_move_id.amount_currency)
            record.amount_collected = result
            record.amount_diff = record.amount_residual - record.amount_collected
