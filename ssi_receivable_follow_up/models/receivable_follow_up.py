# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReceivableFollowUp(models.Model):
    _name = "receivable_follow_up"
    _description = "Receivable Follow Up"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False

    _statusbar_visible_label = "draft,open,confirm,done"

    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "open_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_open",
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_open",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    date_start = fields.Date(
        string="Date Start",
        required=True,
        readonly=False,
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
        readonly=False,
    )

    type_id = fields.Many2one(
        string="Type",
        comodel_name="receivable_follow_up_type",
        required=True,
        ondelete="restrict",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        ondelete="restrict",
    )
    allowed_collector_ids = fields.Many2many(
        string="Allowed Collectors",
        comodel_name="res.users",
        related="type_id.allowed_collector_ids",
        store=False,
    )
    collector_id = fields.Many2one(
        string="Collector",
        comodel_name="res.users",
        required=True,
        ondelete="restrict",
    )
    amount_due = fields.Monetary(
        string="Amount Due",
        compute="_compute_amount",
        store=True,
    )
    amount_collected = fields.Monetary(
        string="Amount Collected",
        compute="_compute_amount",
        store=True,
    )
    collection_rate = fields.Float(
        string="Collection Rate",
        compute="_compute_amount",
        store=True,
    )
    detail_ids = fields.One2many(
        string="Details",
        comodel_name="receivable_follow_up.detail",
        inverse_name="follow_up_id",
        readonly=True,
    )
    state = fields.Selection(
        string="State",
        default="draft",
        selection=[
            ("draft", "Draft"),
            ("open", "In Progress"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
    )

    @api.model
    def _get_policy_field(self):
        res = super(ReceivableFollowUp, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "open_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.onchange("type_id")
    def onchange_collector_id(self):
        self.collector_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    @api.depends(
        "detail_ids",
        "detail_ids.amount_total",
        "detail_ids.amount_residual",
        "detail_ids.amount_collected",
        "detail_ids.amount_diff",
    )
    def _compute_amount(self):
        for record in self:
            amount_due = 0.0
            amount_collected = 0.0
            for detail in record.detail_ids:
                amount_due = amount_due + detail.amount_residual
                amount_collected = amount_collected + detail.amount_collected
            record.amount_due = amount_due
            record.amount_collected = amount_collected
            record.collection_rate = (
                amount_due != 0.0 and amount_collected / amount_due or 0.0
            ) * 100.0

    @api.multi
    def _prepare_move_line_criteria(self):
        self.ensure_one()
        result = [
            ("reconciled", "=", False),
            ("journal_id", "in", self.type_id.allowed_journal_ids.ids),
            ("account_id", "in", self.type_id.allowed_account_ids.ids),
            ("move_id.state", "=", "posted"),
            ("invoice_id.date", "<=", self.date_end),
            ("invoice_id.days_overdue", ">=", self.type_id.min_date_due),
            ("invoice_id.days_overdue", "<=", self.type_id.max_date_due),
            ("invoice_id.collector_id.id", "=", self.collector_id.id),
        ]

        return result

    @api.multi
    def action_populate(self):
        for record in self.sudo():
            record._populate()

    @api.multi
    def _populate(self):
        self.ensure_one()
        self.detail_ids.unlink()
        lines = self.env["account.move.line"].search(self._prepare_move_line_criteria())
        for line in lines:
            residual = (
                line.currency_id
                and line.amount_residual_currency
                or line.amount_residual
            )
            self.env["receivable_follow_up.detail"].create(
                {
                    "invoice_id": line.invoice_id.id,
                    "move_line_id": line.id,
                    "follow_up_id": self.id,
                    "amount_residual": residual,
                }
            )

    @api.constrains("date_start", "date_end")
    def _check_date_start_end(self):
        for record in self:
            if record.date_start and record.date_end:
                strWarning = _("Date end must be greater than date start")
                if record.date_end < record.date_start:
                    raise UserError(strWarning)

    @api.model
    def create(self, vals):
        _super = super(ReceivableFollowUp, self)
        res = _super.create(vals)
        if not res.policy_template_id:
            res.onchange_policy_template_id()
        return res
