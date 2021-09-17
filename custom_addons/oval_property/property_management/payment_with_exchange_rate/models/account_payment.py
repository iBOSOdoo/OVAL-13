
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class account_payment(models.Model):
    _inherit = "account.payment"

    exchange_rate = fields.Float(string='Exchange Rate', digits=(12, 6))
    exchange_rate_currency_name = fields.Char(
        related='currency_id.name', readonly=True, string="Currency Name")

    @api.model
    def default_get(self, default_fields):
        rec = super(account_payment, self).default_get(default_fields)
        currency_id = self.env['res.currency'].browse(rec.get('currency_id'))
        if currency_id:
            rec.update({
                'exchange_rate': currency_id.rate,
            })
        return rec

    @api.onchange('currency_id')
    def _onchange_currency(self):
        rec = super(account_payment, self)._onchange_currency()
        if self.currency_id:
            self.write({'exchange_rate': self.currency_id.rate})
        return rec

    @api.onchange('exchange_rate')
    def _onchange_exchange_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company = self.env['res.company'].browse(
            self._context.get('company_id')) or self.env.company
        currency_rates = self.currency_id._get_rates(company, date)
        if currency_rates:
            if currency_rates.get(self.currency_id.id) != self.exchange_rate:
                currency_rate = self.env['res.currency.rate'].search([('name', '=', date),('currency_id', '=', self.currency_id.id),('company_id','=',company.id)], limit=1)
                if currency_rate:
                    currency_rate.write({'rate': self.exchange_rate})
                    self._onchange_currency()
                else:
                    self.env['res.currency.rate'].create({
                        'name': date,
                        'rate': self.exchange_rate,
                        'currency_id': self.currency_id.id,
                        "company_id": company.id,
                    })
                    self._onchange_currency()
