# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    sheet_type = fields.Selection([
        ('general', 'General'),
        ('other', 'Other'),
        ('zero', 'Zero'),
        ('exempt', 'Exempt'),
    ], string='VAT Sheet Type', )
