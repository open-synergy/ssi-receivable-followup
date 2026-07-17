# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Receivable Follow Up + Operating Unit",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "ssi_receivable_follow_up",
        "ssi_operating_unit_mixin",
    ],
    "data": [
        "security/res_group/receivable_follow_up.xml",
        "security/ir_rule/receivable_follow_up.xml",
        "view/receivable_follow_up.xml",
    ],
}
