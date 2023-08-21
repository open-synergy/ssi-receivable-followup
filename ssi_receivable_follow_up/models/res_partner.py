# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = [
        "res.partner",
    ]

    collector_id = fields.Many2one(
        string="Collector",
        comodel_name="res.users",
    )
