# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = [
        "account.invoice",
    ]

    @api.depends(
        "partner_id",
        "manual_collector_id",
    )
    def _compute_collector_id(self):
        for record in self:
            result = record.manual_collector_id
            if record.partner_id.commercial_partner_id.collector_id:
                result = record.partner_id.commercial_partner_id.collector_id
            record.collector_id = result

    collector_id = fields.Many2one(
        string="Collector",
        comodel_name="res.users",
        compute="_compute_collector_id",
        store=True,
    )
    manual_collector_id = fields.Many2one(
        string="Collector (Manual Input)",
        comodel_name="res.users",
    )
