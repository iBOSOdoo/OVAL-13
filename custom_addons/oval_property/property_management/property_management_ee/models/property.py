# See LICENSE file for full copyright and licensing details

from datetime import datetime
import threading

from odoo import _, api, fields, models, sql_db
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError, Warning


class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property Type"

    name = fields.Char(
        string='Name',
        size=50,
        required=True)


class RentType(models.Model):
    _name = "rent.type"
    _description = "Rent Type"
    _order = 'sequence_in_view'

    
    @api.depends('name', 'renttype')
    def name_get(self):
        """
        Added name_get for purpose of displaying company name with rent type.
        """
        res = []
        for rec in self:
            rec_str = ''
            if rec.name:
                rec_str += rec.name
            if rec.renttype:
                rec_str += ' ' + rec.renttype
            res.append((rec.id, rec_str))
        return res

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """
         Added name_search for purpose to search by name and rent type
        """
        args += ['|', ('name', operator, name), ('renttype', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

    name = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'),
         ('4', '4'), ('5', '5'), ('6', '6'),
         ('7', '7'), ('8', '8'), ('9', '9'),
         ('10', '10'), ('11', '11'), ('12', '12')],
        required=True)
    renttype = fields.Selection(
        [('Monthly', 'Monthly'),
         ('Yearly', 'Yearly'),
         ('Weekly', 'Weekly')],
        string='Rent Type',
        required=True)
    sequence_in_view = fields.Integer(
        string='Sequence')

    @api.constrains('sequence_in_view')
    def _check_value(self):
        for rec in self:
            if rec.search([
                    ('sequence_in_view', '=', rec.sequence_in_view),
                    ('id', '!=', rec.id)]):
                raise ValidationError(_('Sequence should be Unique!'))


class RoomType(models.Model):
    _name = "room.type"
    _description = "Room Type"

    name = fields.Char(
        string='Name',
        size=50,
        required=True)


class Utility(models.Model):
    _name = "utility"
    _description = "Utility"

    name = fields.Char(
        string='Name',
        size=50,
        required=True)


class PlaceType(models.Model):
    _name = 'place.type'
    _description = 'Place Type'

    name = fields.Char(
        string='Place Type',
        size=50,
        required=True)


class PropertyPhase(models.Model):
    _name = "property.phase"
    _description = 'Property Phase'
    _rec_name = 'property_id'

    end_date = fields.Date(
        string='End Date')
    start_date = fields.Date(
        string='Beginning Date')
    commercial_tax = fields.Float(
        string='Commercial Tax (in %)')
    occupancy_rate = fields.Float(
        string='Occupancy Rate (in %)')
    lease_price = fields.Float(
        string='Sales/lease Price Per Month')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')
    # operational_budget = fields.Float(
    #     string='Operational Budget (in %)')
    company_income = fields.Float(
        string='Company Income Tax CIT (in %)')


class PropertyPhoto(models.Model):
    _name = "property.photo"
    _description = 'Property Photo'
    _rec_name = 'doc_name'

    photos = fields.Binary(
        string='Photos')
    doc_name = fields.Char(
        string='Filename')
    photos_description = fields.Char(
        string='Description')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')

class PropertyPhoto(models.Model):
    _name = "property.floor.plans"
    _description = 'Floor Plans'
    _rec_name = 'doc_name'

    photos = fields.Binary(
        string='Photos')
    doc_name = fields.Char(
        string='Filename')
    photos_description = fields.Char(
        string='Description')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')


class PropertyRoom(models.Model):
    _name = "property.room"
    _description = 'Property Room'

    note = fields.Text(
        string='Notes')
    width = fields.Float(
        string='Width')
    height = fields.Float(
        string='Height')
    length = fields.Float(
        string='Length')
    image = fields.Binary(
        string='Picture')
    name = fields.Char(
        string='Name',
        size=60)
    attach = fields.Boolean(
        string='Attach Bathroom')
    type_id = fields.Many2one(
        comodel_name='room.type',
        string='Room Type')
    assets_ids = fields.One2many(
        comodel_name='room.assets',
        inverse_name='room_id',
        string='Assets')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')


class NearbyProperty(models.Model):
    _name = 'nearby.property'
    _description = 'Nearby Property'

    distance = fields.Float(
        string='Distance (Km)')
    name = fields.Char(
        string='Name',
        size=100)
    type = fields.Many2one(
        comodel_name='place.type',
        string='Type')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')


# class CostCost(models.Model):
#     _name = "cost.cost"
#     _description = 'Cost'
#     _order = 'date'

    
#     @api.depends('move_id')
#     def _compute_move_check(self):
#         for rec in self:
#             rec.move_check = bool(rec.move_id)

#     date = fields.Date(
#         string='Date')
#     amount = fields.Float(
#         string='Amount')
#     name = fields.Char(
#         string='Description',
#         size=100)
#     payment_details = fields.Char(
#         string='Payment Details',
#         size=100)
#     currency_id = fields.Many2one(
#         comodel_name='res.currency',
#         string='Currency')
#     move_id = fields.Many2one(
#         comodel_name='account.move',
#         string='Purchase Entry')
#     property_id = fields.Many2one(
#         comodel_name='account.asset',
#         string='Property')
#     remaining_amount = fields.Float(
#         string='Remaining Amount',
#         help='Shows remaining amount in currency')
#     move_check = fields.Boolean(
#         compute='_compute_move_check',
#         method=True,
#         string='Posted',
#         store=True)
#     rmn_amnt_per = fields.Float(
#         string='Remaining Amount In %',
#         help='Shows remaining amount in Percentage')
#     invc_id = fields.Many2one(
#         comodel_name='account.move',
#         string='Invoice')

    
#     def create_invoice(self):
#         """
#         This button Method is used to create account invoice.
#         @param self: The object pointer
#         """
#         account_jrnl_obj = self.env['account.journal'].search(
#             [('type', '=', 'purchase')], limit=1)
#         context = dict(self._context or {})
#         wiz_form_id = self.env.ref('account.invoice_supplier_form').id
#         inv_obj = self.env['account.invoice']
#         for rec in self:
#             if not rec.property_id.partner_id:
#                 raise Warning(_('Please Select Partner!'))
#             if not rec.property_id.expense_account_id:
#                 raise Warning(_('Please Select Expense Account!'))

#             inv_line_values = {
#                 'origin': 'Cost.Cost',
#                 'name':
#                     _('Purchase Cost For')+''+rec.property_id.name,
#                 'price_unit': rec.amount or 0.00,
#                 'quantity': 1,
#                 'account_id': rec.property_id.expense_account_id.id,
#             }

#             inv_values = {
#                 'payment_term_id':
#                     rec.property_id.payment_term.id or False,
#                 'partner_id': rec.property_id.partner_id.id or False,
#                 'type': 'in_invoice',
#                 'property_id': rec.property_id.id or False,
#                 'invoice_line_ids': [(0, 0, inv_line_values)],
#                 'journal_id': account_jrnl_obj and account_jrnl_obj.id or False,
#             }
#             invoice_rec = inv_obj.create(inv_values)
#             rec.write({'invc_id': invoice_rec.id, 'move_check': True})
#         return {
#                 'view_type': 'form',
#                 'view_id': wiz_form_id,
#                 'view_mode': 'form',
#                 'res_model': 'account.invoice',
#                 'res_id': self.invc_id.id,
#                 'type': 'ir.actions.act_window',
#                 'target': 'current',
#                 'context': context,
#             }

    
#     def open_invoice(self):
#         """
#         This Method is used to Open invoice
#         @param self: The object pointer
#         """
#         context = dict(self._context or {})
#         wiz_form_id = self.env.ref('account.invoice_supplier_form').id
#         return {
#             'view_type': 'form',
#             'view_id': wiz_form_id,
#             'view_mode': 'form',
#             'res_model': 'account.invoice',
#             'res_id': self.invc_id.id,
#             'type': 'ir.actions.act_window',
#             'target': 'current',
#             'context': context,
#         }


class RoomAssets(models.Model):
    _name = "room.assets"
    _description = "Room Assets"

    date = fields.Date(
        string='Date')
    name = fields.Char(
        string='Description',
        size=60)
    type = fields.Selection(
        [('fixed', 'Fixed Assets'),
         ('movable', 'Movable Assets'),
         ('other', 'Other Assets')],
        string='Type')
    qty = fields.Float(
        string='Quantity')
    room_id = fields.Many2one(
        comodel_name='property.room',
        string='Property')


class PropertyInsurance(models.Model):
    _name = "property.insurance"
    _description = "Property Insurance"

    premium = fields.Float(
        string='Premium')
    end_date = fields.Date(
        string='End Date')
    doc_name = fields.Char(
        string='Filename')
    contract = fields.Binary(
        string='Contract')
    start_date = fields.Date(
        string='Start Date')
    name = fields.Char(
        string='Description',
        size=60)
    policy_no = fields.Char(
        string='Policy Number',
        size=60)
    contact = fields.Many2one(
        comodel_name='res.company',
        string='Insurance Comapny')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Related Company')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')
    payment_mode_type = fields.Selection(
        [('monthly', 'Monthly'),
         ('semi_annually', 'Semi Annually'),
         ('yearly', 'Annually')],
        string='Payment Term',
        size=40)


class PropertyUtility(models.Model):
    _name = "property.utility"
    _description = 'Property Utility'

    note = fields.Text(
        string='Remarks')
    ref = fields.Char(
        string='Reference',
        size=60)
    expiry_date = fields.Date(
        string='Expiry Date')
    issue_date = fields.Date(
        string='Issuance Date')
    utility_id = fields.Many2one(
        comodel_name='utility',
        string='Utility')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')
    tenancy_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Tenancy')
    contact_id = fields.Many2one(
        comodel_name='tenant.partner',
        string='Contact',
        domain="[('tenant', '=', True)]")


class PropertySafetyCertificate(models.Model):
    _name = "property.safety.certificate"
    _description = 'Property Safety Certificate'

    ew = fields.Boolean(
        'EW')
    weeks = fields.Integer(
        'Weeks')
    ref = fields.Char(
        'Reference',
        size=60)
    expiry_date = fields.Date(
        string='Expiry Date')
    name = fields.Char(
        string='Certificate',
        size=60,
        required=True)
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')
    contact_id = fields.Many2one(
        comodel_name='tenant.partner',
        string='Contact',
        domain="[('tenant', '=', True)]")


class PropertyAttachment(models.Model):
    _name = 'property.attachment'
    _description = 'Property Attachment'

    doc_name = fields.Char(
        string='Filename')
    expiry_date = fields.Date(
        string='Expiry Date')
    contract_attachment = fields.Binary(
        string='Attachment')
    name = fields.Char(
        string='Description',
        size=64,
        requiered=True)
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')


# class SaleCost(models.Model):
#     _name = "sale.cost"
#     _description = 'Sale Cost'
#     _order = 'date'

    
#     @api.depends('move_id')
#     def _compute_move_check(self):
#         for rec in self:
#             rec.move_check = bool(rec.move_id)

#     date = fields.Date(
#         string='Date')
#     amount = fields.Float(
#         string='Amount')
#     name = fields.Char(
#         string='Description',
#         size=100)
#     payment_details = fields.Char(
#         string='Payment Details',
#         size=100)
#     currency_id = fields.Many2one(
#         comodel_name='res.currency',
#         string='Currency')
#     move_id = fields.Many2one(
#         comodel_name='account.move',
#         string='Purchase Entry')
#     property_id = fields.Many2one(
#         comodel_name='account.asset',
#         string='Property')
#     remaining_amount = fields.Float(
#         string='Remaining Amount',
#         help='Shows remaining amount in currency')
#     move_check = fields.Boolean(
#         string='Posted',
#         compute='_compute_move_check',
#         method=True,
#         store=True)
#     rmn_amnt_per = fields.Float(
#         string='Remaining Amount In %',
#         help='Shows remaining amount in Percentage')
#     invc_id = fields.Many2one(
#         comodel_name='account.move',
#         string='Invoice')

    
    # def create_invoice(self):
    #     """
    #     This button Method is used to create account invoice.
    #     @param self: The object pointer
    #     """
    #     if not self.property_id.customer_id:
    #         raise Warning(_('Please Select Customer!'))
    #     if not self.property_id.income_acc_id:
    #         raise Warning(_('Please Configure Income Account from Property!'))
    #     account_jrnl_obj = self.env['account.journal'].search(
    #         [('type', '=', 'sale')], limit=1)

    #     inv_line_values = {
    #         'origin': 'sale.cost',
    #         'name': _('Purchase Cost For')+''+self.property_id.name,
    #         'price_unit': self.amount or 0.00,
    #         'quantity': 1,
    #         'account_id': self.property_id.income_acc_id.id,
    #     }

    #     inv_values = {
    #         'payment_term_id': self.property_id.payment_term.id or False,
    #         'partner_id': self.property_id.customer_id.id or False,
    #         'type': 'out_invoice',
    #         'property_id': self.property_id.id or False,
    #         'invoice_line_ids': [(0, 0, inv_line_values)],
    #         'journal_id': account_jrnl_obj and account_jrnl_obj.id or False,
    #     }
    #     acc_id = self.env['account.invoice'].create(inv_values)
    #     self.write({'invc_id': acc_id.id, 'move_check': True})
    #     context = dict(self._context or {})
    #     wiz_form_id = self.env.ref('account.invoice_form').id
    #     return {
    #         'view_type': 'form',
    #         'view_id': wiz_form_id,
    #         'view_mode': 'form',
    #         'res_model': 'account.invoice',
    #         'res_id': self.invc_id.id,
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'context': context,
    #     }

    
    # def open_invoice(self):
    #     """
    #     This Method is used to Open invoice
    #     @param self: The object pointer
    #     """
    #     context = dict(self._context or {})
    #     wiz_form_id = self.env.ref('account.invoice_form').id
    #     return {
    #         'view_type': 'form',
    #         'view_id': wiz_form_id,
    #         'view_mode': 'form',
    #         'res_model': 'account.invoice',
    #         'res_id': self.invc_id.id,
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'context': context,
    #     }
