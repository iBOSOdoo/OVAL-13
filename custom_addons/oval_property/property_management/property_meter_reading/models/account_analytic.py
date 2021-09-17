
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('wcl_reading')
    def total_consumption_water(self):
        """Compute Method For Total Water Consumption."""
        total = 0
        if self.wcl_reading:
            total = self.wcl_reading - self.wop_reading
        self.total_water_cnsm = total

    @api.depends('ecl_reading')
    def total_consumption_electric(self):
        """Compute Method For Total Electric Consumption."""
        total = 0
        if self.ecl_reading:
            total = self.ecl_reading - self.eop_reading
        self.total_electric_cnsm = total

    @api.depends('total_water_cnsm')
    def total_percentage_water(self):
        """Compute Method For Total Water Percentage."""
        total = 0
        if self.total_water_cnsm:
            total = self.total_water_cnsm * \
                self.company_id.total_cnsm_id.percentage / 100
        self.water_percentage = total

    @api.depends('total_water_cnsm')
    def total_percentage_borehole(self):
        """Compute Method For Total Borehole Percentage."""
        total = 0
        if self.total_water_cnsm:
            total = self.total_water_cnsm * \
                self.company_id.cnsm_total_id.percentage / 100
        self.borehole_percentage = total

    @api.depends('total_electric_cnsm')
    def total_amount_electricity(self):
        """Compute Method For Total Electricity Amount."""
        total = 0
        if self.total_electric_cnsm:
            total = self.total_electric_cnsm * \
                self.company_id.electricity_id.electricity_rate
        self.total_electricity = total

    wmeter_id = fields.Many2one('water.meter.reading', string='Water Meter')
    emeter_id = fields.Many2one(
        'electricity.meter.reading', string='Electricity Meter')
    wacc = fields.Char(string="ACC#",)
    wmeter = fields.Char(string="Meter#", group_operator="max")
    wop_date = fields.Date(string="Opening Date")
    wop_reading = fields.Integer(string="Opening Reading")
    wcl_date = fields.Date(string="Closing Date")
    wcl_reading = fields.Integer(string="Current Reading")
    total_water_cnsm = fields.Float(
        string='Total Consumed Unit', compute='total_consumption_water')
    wremarks = fields.Char(string="Remarks/Notes")
    eacc = fields.Char(string="ACC#",)
    emeter = fields.Char(string="Meter#", group_operator="max")
    eop_date = fields.Date(string="Opening Date")
    eop_reading = fields.Integer(string="Opening Reading")
    ecl_date = fields.Date(string="Closing Date")
    ecl_reading = fields.Integer(string="Current Reading")
    eremarks = fields.Char(string="Remarks/Notes")
    get_whide = fields.Boolean(string='Water Hide')
    total_electric_cnsm = fields.Float(
        string="Total Consumed Unit", compute="total_consumption_electric")
    get_ehide = fields.Boolean(string='Electricity Hide')
    get_fhide = fields.Boolean(string='furniater Hide')
    status_we = fields.Selection(
        [('1', 'Move In'), ('2', 'Move Out')], string='Status')
    inv = fields.Boolean(string='Invoiced?')
    water_percentage = fields.Float(
        string="Water Percentage", compute="total_percentage_water")
    borehole_percentage = fields.Float(
        string="borehole Percentage", compute="total_percentage_borehole")
    total_electricity = fields.Float(
        string="Total Amount Electricity", compute="total_amount_electricity")

    def water_reading_create(self):
        """Water Reading Create Method"""
        water_obj = self.env['water.meter.reading']
        reading = []
        for record in self:
            vals = {
                'wacc': record.wacc,
                'wmeter': record.wmeter,
                'wop_date': record.wop_date,
                'wop_reading': record.wop_reading,
                'wcl_date': record.wcl_date,
                'wcl_reading': record.wcl_reading,
                'property_id': record.property_id.id,
                'tenancy_id': record.id,
                'remarks': record.wremarks,
            }
        water_obj.create(vals)

    def get_water_reading(self):
        """Water Reading Method"""
        water_obj = self.env['water.meter.reading']
        water_id = water_obj.search([
            ('property_id', '=', self.property_id.id)], limit=1,
            order='wcl_reading desc')

        self.wacc = water_id.wacc
        self.wmeter = water_id.wmeter
        self.wop_date = datetime.now().date()
        self.wop_reading = water_id.wcl_reading
        self.wcl_date = False
        self.wcl_reading = False
        self.write({'get_whide': True})

    def electricity_reading_create(self):
        """Electricity Reading Create Method"""
        reading = []
        electricity_obj = self.env['electricity.meter.reading']
        for record in self:
            vals = {
                'eacc': record.eacc,
                'emeter': record.emeter,
                'eop_date': record.eop_date,
                'eop_reading': record.eop_reading,
                'ecl_date': record.ecl_date,
                'ecl_reading': record.ecl_reading,
                'property_id': record.property_id.id,
                'tenancy_id': record.id,
                'remarks': record.eremarks,
            }
        electricity_obj.create(vals)

    def get_electricity_reading(self):
        """Electricity Reading Method"""
        electricity_obj = self.env['electricity.meter.reading']
        electricity_id = electricity_obj.search([
            ('property_id', '=', self.property_id.id)], limit=1,
            order='ecl_reading desc')

        self.eacc = electricity_id.eacc
        self.emeter = electricity_id.emeter
        self.eop_date = datetime.now().date()
        self.eop_reading = electricity_id.ecl_reading
        self.ecl_date = False
        self.ecl_reading = False
        self.write({'get_ehide': True})

    def get_invloice_lines_water(self):
        """TO GET THE INVOICE LINES"""
        inv_line = {}
        for rec in self:
            inv_line = {
                'name': _('Water Meter Bill'),
                'price_unit': rec.total_water_cnsm or 0.00,
                'quantity': 1,
                'account_id':
                rec.property_id.account_depreciation_expense_id.id or False,
                'analytic_account_id': rec.id or False,
            }
        return [(0, 0, inv_line)]

    def create_invoice_water(self):
        """Create invoice for Watermeter Meter Bill"""
        inv_obj = self.env['account.move']
        if not self.total_water_cnsm:
            raise UserError("Total consumption has no value")

        inv_water_bill_rec = inv_obj.search([
            ('id', '=', self.invc_id.id), ('is_water_bill', '=', True)])

        if inv_water_bill_rec:
            return {
                'view_type': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.invc_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

        for rec in self:
            inv_line_values = rec.get_invloice_lines_water()
            inv_values = {
                'partner_id': rec.tenant_id.parent_id.id or False,
                'type': 'out_invoice',
                'property_id': rec.property_id.id or False,
                'invoice_date': datetime.now().strftime(
                    DEFAULT_SERVER_DATE_FORMAT) or False,
                'invoice_line_ids': inv_line_values,
                'is_water_bill': True,
                'tenancy_id': self.id,
            }
            invoice_id = inv_obj.create(inv_values)
            rec.write({'invc_id': invoice_id.id, 'inv': True})
            inv_form_id = self.env.ref('account.view_move_form').id

        return {
            'view_type': 'form',
            'view_id': inv_form_id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def get_invloice_lines_electric(self):
        """TO GET THE INVOICE LINES"""
        inv_line = {}
        for rec in self:
            inv_line = {
                'name': _('Electricity Meter Bill'),
                'price_unit': rec.company_id.electricity_id.electricity_rate or
                0.00,
                'quantity': rec.total_electric_cnsm or 1,
                'account_id':
                rec.property_id.account_depreciation_expense_id.id or False,
                'analytic_account_id': rec.id or False,

            }
        return [(0, 0, inv_line)]

    def create_invoice_electric(self):
        """Create invoice for Electric Meter Bill."""
        inv_obj = self.env['account.move']
        if not self.total_electric_cnsm:
            raise UserError("Total consumption has no value")

        inv_electric_bill_rec = inv_obj.search([
            ('id', '=', self.invc_id.id), ('is_ele_bill', '=', True)])

        if inv_electric_bill_rec:
            return {
                'view_type': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.invc_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

        for rec in self:
            inv_line_values = rec.get_invloice_lines_electric()
            inv_values = {
                'partner_id': rec.tenant_id.parent_id.id or False,
                'type': 'out_invoice',
                'property_id': rec.property_id.id or False,
                'invoice_date': datetime.now().strftime(
                    DEFAULT_SERVER_DATE_FORMAT) or False,
                'invoice_line_ids': inv_line_values,
                'is_ele_bill': True,
                'tenancy_id': self.id,
            }

            invoice_id = inv_obj.create(inv_values)
            rec.write({'invc_id': invoice_id.id, 'inv': True})
            inv_form_id = self.env.ref('account.view_move_form').id

        return {
            'view_type': 'form',
            'view_id': inv_form_id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class AccoutMove(models.Model):
    _inherit = 'account.move'

    is_water_bill = fields.Boolean(string="Is Water Bill?")
    is_ele_bill = fields.Boolean(string="Is Electricity Bill?")
    tenancy_id = fields.Many2one('account.analytic.account', string="Tenancy")
