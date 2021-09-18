# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import logging
import string
import re
import datetime

_logger = logging.getLogger(__name__)

try:
    import vatnumber
except ImportError:
    _logger.warning("PIN validation partially unavailable because the `pinnumber` Python library cannot be found. "
                    "Install it to support more countries, for example with `easy_install vatnumber`.")
    vatnumber = None

_ref_vat = {
    'ke': 'A012345678S'
}


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    kra_pin = fields.Char(string='KRA PIN', size=12)
    nhif_no = fields.Char("NHIF No.")
    nssf_no = fields.Char("NSSF No.")

    @api.model
    def simple_vat_check(self, pin_number):

        check_func_name = 'check_pin_ke'
        check_func = getattr(self, check_func_name, None) or getattr(vatnumber, check_func_name, None)
        if not check_func:
            # No VAT validation available, default to check that the country code exists
            return bool(self.env['res.country'].search([('code', '=ilike', 'KE')]))
        return check_func(pin_number)

    @api.constrains("kra_pin")
    def check_pin(self):
        # quick and partial off-line checksum validation
        check_func = self.simple_vat_check

        for partner in self:
            if not partner.kra_pin:
                continue
            pin_number = partner.kra_pin
            if not check_func(pin_number):
                _logger.info("Importing PIN Number [%s] is not valid !" % pin_number)
                msg = partner._construct_constraint_msg()
                raise ValidationError(msg)

    def _construct_constraint_msg(self):
        self.ensure_one()

        def default_pin_check(pn):
            # by default, in Kenya, a PIN number is valid if:
            #  it starts with a letter and P for company with A for individuals
            #  followed by 9 digits
            #  ends with an alphabetic letter.
            return pn[0] in string.ascii_lowercase and pn[10] in string.ascii_lowercase

        pin_number = self.kra_pin
        pin_no = "'C##D' (C=Alphabet Letter, ##=9 Numerics, D=Alphabet Letter)\n First letter starts with A"
        return '\n' + _(
            'The PIN number [%s] for employee [%s] does not seem to be valid. \nNote: the expected format is %s') % (
                   self.kra_pin, self.name, pin_no)

    def check_pin_ke(self, pin):

        KENYAN_PIN_REGEX = re.compile(r"\d?[A]\d[0-9]\d[0-9]\d[0-9]\d[0-9]\d?[A-Z]")

        if not KENYAN_PIN_REGEX.match(pin):
            return False

        return True
