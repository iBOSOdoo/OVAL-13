# See LICENSE file for full copyright and licensing details

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class Recurring(models.Model):
    _name = 'property.rent'
    _description = 'Property Rent'

    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property',
        copy='False',
        help='Property name')
    ground = fields.Float(
        string='Ground Rent',
        copy='False',
        help='Rent of property', )
    ten_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Ten')

    @api.onchange('property_id')
    def ground_rent(self):
        """
        This method is used to get rent when select the property
        """
        val = 0.0
        if self.property_id:
            val = float(self.property_id.ground_rent)
        self.ground = val


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'


    @api.onchange('prop_ids', 'multi_prop')
    def _total_prop_rent(self):
        """
        This method calculate total rent of all the selected property.
        @param self: The object pointer
        """
        tot = 0.00
        prop_val = self.property_id.ground_rent or 0.0
        for pro_record in self:
            if pro_record.multi_prop:
                for prope_ids in pro_record.prop_ids:
                    tot += prope_ids.ground
                pro_record.rent = tot + prop_val
            else:
                pro_record.rent = prop_val

    prop_ids = fields.One2many(
        comodel_name='property.rent',
        inverse_name='ten_id',
        copy='False',
        string="Property Rent")

    multi_prop = fields.Boolean(
        string='Multiple Property',
        help="Check this box Multiple property.")

    @api.model
    def create(self, vals):
        """
        This Method is used to overrides orm create method,
        to change state and tenant of related property.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        res = super(AccountAnalyticAccount, self).create(vals)
        if vals.get('multi_prop'):
            if not vals.get('prop_ids'):
                raise Warning(
                _('You have to select property from properties tab.'))
            for property in vals.get('prop_ids'):
                multi_prop_brw = self.env['account.asset'].browse(
                    property[2].get('property_id'))
                multi_prop_brw.write(
                    {'current_tenant_id': vals.get('tenant_id', False),
                        'state': 'book'})
        return res


    
    def button_start(self):
        """
        This button method is used to Change Tenancy state to Open.
        @param self: The object pointer
        """
        self.ensure_one()
        res = super(AccountAnalyticAccount, self).button_start()
        user_obj = self.env['res.users']
        if self.multi_prop:
            for current_rec in self.prop_ids:
                if current_rec.property_id.property_manager and \
                        current_rec.property_id.property_manager.id:
                    releted_user = current_rec.property_id.property_manager.id
                    new_ids = user_obj.search(
                        [('partner_id', '=', releted_user)])
                    if releted_user and new_ids and new_ids.ids:
                        new_ids.write(
                            {'tenant_ids': [(4, self.tenant_id.id)]})
            self.write({'state': 'open', 'rent_entry_chck': False})
        return res

    
    def write(self, vals):
        """
        This Method is used to overrides orm write method,
        to change state and tenant of related property.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        rec = super(AccountAnalyticAccount, self).write(vals)

        for tenancy_rec in self:
            if tenancy_rec.multi_prop:
                for prop in tenancy_rec.prop_ids:
                    property = prop.property_id
                    if vals.get('state'):
                        if vals['state'] == 'open':
                            property.write({
                                'current_tenant_id': tenancy_rec.tenant_id.id,
                                'state': 'normal'})
                        if vals['state'] == 'close':
                            property.write(
                                {'state': 'draft', 'current_tenant_id': False})
        return rec

    @api.onchange('multi_prop')
    def onchange_multi_prop(self):
        """
        If the context is get is_tenanacy_rent then property id is 0
        or if get than prop_idss is zero
        @param self: The object pointer
        """
        if self.multi_prop is True:
            if not self._context.get('is_landlord_rent'):
                self.property_id = False
        else:
            self.prop_ids = []


class TenancyRentSchedule(models.Model):
    _inherit = "tenancy.rent.schedule"

    
    def get_invloice_lines(self):
        """
        TO GET THE INVOICE LINES
        """
        for rec in self:
            inv_lines = super(TenancyRentSchedule, self).get_invloice_lines()
            inv_line_values = inv_lines[0][2]
            if rec.tenancy_id.multi_prop:
                for data in rec.tenancy_id.prop_ids:
                    for account in data.property_id.income_acc_id:
                        inv_line_values.update({'account_id': account.id})
            return inv_lines
