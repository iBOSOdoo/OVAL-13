
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    total_cnsm_id = fields.Many2one('total.consumption',
                                    string="Water percentage")
    cnsm_total_id = fields.Many2one('total.consumption',
                                    string="Borehole percentage")
    electricity_id = fields.Many2one('total.consumption',
                                     string="Electricity percentage")
