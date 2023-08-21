# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReceivableFollowUpType(models.Model):
    _name = "receivable_follow_up_type"
    _description = "Receivable Follow Up Type"
    _inherit = ["mixin.master_data"]

    allowed_collector_ids = fields.Many2many(
        string="Allowed Collectors",
        comodel_name="res.users",
        relation="rel_receivable_follow_up_type_2_collector",
        column1="type_id",
        column2="user_id",
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        relation="rel_receivable_follow_up_type_2_account",
        column1="type_id",
        column2="account_id",
    )
    allowed_journal_ids = fields.Many2many(
        string="Allowed Journals",
        comodel_name="account.journal",
        relation="rel_receivable_follow_up_type_2_journal",
        column1="type_id",
        column2="account_id",
    )
    max_date_due = fields.Integer(string="Max Date Due", required=True)
    min_date_due = fields.Integer(string="Min Date Due", required=True)
