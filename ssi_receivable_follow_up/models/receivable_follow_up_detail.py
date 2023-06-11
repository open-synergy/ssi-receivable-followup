# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
        comodel_name="account.invoice",
        required=True,
        ondelete="restrict",
    )
    move_line_id = fields.Many2one(
        string="# Move Line",
        comodel_name="account.move.line",
        required=True,
        ondelete="restrict",
    )
    partner_id = fields.Many2one(
        string="Partner",
        related="move_line_id.partner_id",
        store=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        related="move_line_id.currency_id",
        store=True,
    )
    date_invoice = fields.Date(
        string="Date",
        related="move_line_id.date",
        store=True,
    )
    date_due = fields.Date(
        string="Date Due",
        related="move_line_id.date_maturity",
        store=True,
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        related="move_line_id.debit",
        store=True,
        currency_field="currency_id",
    )
    amount_residual = fields.Monetary(
        string="Amount Residual",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    amount_collected = fields.Monetary(
        string="Amount Collected",
        compute="_compute_amount",
        store=True,
        currency_field="currency_id",
    )
    amount_diff = fields.Monetary(
        string="Amount Different",
        compute="_compute_amount",
        store=True,
        currency_field="currency_id",
    )

    @api.depends(
        "move_line_id",
        "move_line_id.amount_residual",
        "move_line_id.amount_residual_currency",
    )
    def _compute_amount(self):
        for record in self:
            residual = collected = collected_residual = 0.0
            ml = record.move_line_id
            criteria = [
                ("debit_move_id", "=", record.move_line_id.id),
                ("credit_move_id.date", "<", record.follow_up_id.date_start),
            ]
            for line in self.env["account.partial.reconcile"].search(criteria):
                collected_residual += (
                    line.currency_id and line.amount_currency or line.amount
                )

            residual = (
                ml.currency_id and ml.amount_currency or ml.debit
            ) - collected_residual

            criteria = [
                ("debit_move_id", "=", record.move_line_id.id),
                ("credit_move_id.date", ">=", record.follow_up_id.date_start),
                ("credit_move_id.date", "<=", record.follow_up_id.date_end),
            ]
            for line in self.env["account.partial.reconcile"].search(criteria):
                collected += line.currency_id and line.amount_currency or line.amount
            record.amount_collected = collected
            record.amount_residual = residual
            record.amount_diff = residual - collected
