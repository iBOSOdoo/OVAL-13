
# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('to_approve', 'To Approve')])

    def button_to_approve(self):
        for order in self:
            order.write({'state': 'to_approve'})
        return True

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for order in self:
            if order._context.get('default_type') == 'out_refund' and \
                    order.user_has_groups(
                        'credit_note_approval.group_credit_note_approval'):
                raise AccessError(
                    _("You don't have the access rights to post a credit note."
                      ))
        return res
