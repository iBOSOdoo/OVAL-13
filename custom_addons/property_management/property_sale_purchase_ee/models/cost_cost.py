# See LICENSE file for full copyright and licensing details
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CostCost(models.Model):
    _name = "cost.cost"
    _description = 'Cost'
    _order = 'date'

    
    @api.depends('move_id')
    def _compute_move_check(self):
        for cost in self:
            cost.move_check = bool(cost.move_id)

    date = fields.Date(
        string='Date')
    amount = fields.Float(
        string='Amount')
    name = fields.Char(
        string='Description',
        size=100)
    payment_details = fields.Char(
        string='Payment Details',
        size=100)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Purchase Entry')
    property_id = fields.Many2one(
        comodel_name='account.asset',
        string='Property')
    remaining_amount = fields.Float(
        string='Remaining Amount',
        help='Shows remaining amount in currency')
    move_check = fields.Boolean(
        compute='_compute_move_check',
        method=True,
        string='Posted',
        store=True)
    rmn_amnt_per = fields.Float(
        string='Remaining Amount In %',
        help='Shows remaining amount in Percentage')
    invc_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice')

    def create_invoice(self):
        """
        This button Method is used to create account invoice.
        @param self: The object pointer
        """
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1)
        wiz_form_id = self.env.ref('account.view_move_form').id
        inv_obj = self.env['account.move']
        for cost in self:
            if not cost.property_id.partner_id:
                raise UserError(_('Please Select Partner!'))
            if not cost.property_id.account_depreciation_expense_id:
                raise UserError(_('Please Select Expense Account!'))

            inv_line_values = {
                # 'origin': 'Cost.Cost',
                'name':
                    _('Purchase Cost For ') + cost.property_id.name,
                'price_unit': cost.amount or 0.00,
                'quantity': 1,
                'account_id': cost.property_id.account_depreciation_expense_id.id,
            }

            inv_values = {
                'invoice_payment_term_id':
                    cost.property_id.payment_term.id or False,
                'partner_id': cost.property_id.partner_id.id or False,
                'type': 'in_invoice',
                'property_id': cost.property_id.id or False,
                'invoice_line_ids': [(0, 0, inv_line_values)],
                'journal_id': account_jrnl_obj and account_jrnl_obj.id or False,
            }
            invoice_rec = inv_obj.with_context({'default_type': 'in_invoice'}).create(inv_values)
            cost.write({'invc_id': invoice_rec.id, 'move_check': True})
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': self._context or {},
        }

    
    def open_invoice(self):
        """
        This Method is used to Open invoice
        @param self: The object pointer
        """
        wiz_form_id = self.env.ref('account.view_move_form').id
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': self._context or {},
        }
