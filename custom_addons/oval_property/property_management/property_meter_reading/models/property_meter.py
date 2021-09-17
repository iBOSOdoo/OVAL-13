
from odoo import models, fields


class WaterMeterReading(models.Model):
    _name = 'water.meter.reading'
    _description = 'Detail of Water Meter'

    date = fields.Datetime(string='Date')
    wacc = fields.Char(string="ACC#",)
    wmeter = fields.Char(string="Meter#", group_operator="max")
    wop_date = fields.Date(string="Opening Date")
    wop_reading = fields.Integer(string="Opening Reading")
    wcl_date = fields.Date(string="Closing Date")
    wcl_reading = fields.Integer(string="Closing Reading")
    property_id = fields.Many2one('account.asset', string="Property")
    tenancy_id = fields.Many2one("account.analytic.account", string='Tenancy')
    remarks = fields.Char(string="Remarks/Notes")


class ElectricityMeterReading(models.Model):
    _name = 'electricity.meter.reading'
    _description = 'Detail of Electricity Meter'

    date = fields.Datetime(string='Date')
    eacc = fields.Char(string="ACC#",)
    emeter = fields.Char(string="Meter#")
    eop_date = fields.Date(string="Opening Date")
    eop_reading = fields.Integer(string="Opening Reading")
    ecl_date = fields.Date(string="Closing Date")
    ecl_reading = fields.Integer(string="Closing Reading")
    property_id = fields.Many2one('account.asset', string="Property")
    tenancy_id = fields.Many2one("account.analytic.account", string='Tenancy')
    remarks = fields.Char(string="Remarks/Notes")


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset'

    water_reading_ids = fields.One2many(
        'water.meter.reading', 'property_id', string='Water Meter')
    electricity_reading_ids = fields.One2many(
        'electricity.meter.reading', 'property_id', string='Electric Meter')


class TotalConsumption(models.Model):
    _name = 'total.consumption'
    _description = 'Detail of Total Consumption'
    _rec_name = 'cnsm_type'

    cnsm_type = fields.Selection([('water', 'Waterbill'),
                                  ('borehole', 'Borehole'),
                                  ('electricity', 'Electricity')],
                                 default='water', string='Consumption Rule')
    date = fields.Date(string='Date')
    cnsm_unit_ids = fields.One2many(
        'consumption.unit', 'cnsm_id', string='Consumption Unit')
    percentage = fields.Integer(string="Percentage")
    sewer_cost = fields.Float(string="Sewer Cost In Percentage")
    meter_rent = fields.Float(string="Meter Rent")
    electricity_rate = fields.Float(string="Unit Rate")


class ConsumptionUnit(models.Model):
    _name = 'consumption.unit'
    _description = 'Detail of consumptioin Unit and Price'
    _rec_name = 'cnsm_unit'

    name = fields.Char(string='Name')
    cnsm_unit = fields.Float(string="Cosumption Unit")
    cnsm_rate = fields.Float(string='Rate')
    max_unit = fields.Float(string="Minimam")
    cnsm_id = fields.Many2one('total.consumption', string='Consumption')
