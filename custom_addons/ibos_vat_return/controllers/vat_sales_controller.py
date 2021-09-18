# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from odoo.http import request
from datetime import datetime
from odoo import http, _
import csv
import io
import base64
from odoo.addons import decimal_precision as dp


class KraVatSalesController(http.Controller):

    @http.route('/accounts/downloads/vat/return/sales/csv', type='http', auth='public', website=False)
    def download_sale_vat_csv_sheet(self, model, selected_description, vatsheet, company_id, start_date, end_date,
                                    file_name=None, **kw):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        csv_vat_data = None

        if vatsheet == 'general_rated_sale_sheet_b':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, 16, True)
            file_name = "ODOO_12_B_GENERAL_RATE_SALE_{}.csv".format(datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'general_rated_vat_non_reg_sale_sheet_b':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, 16, False)
            file_name = "ODOO_12_B_GENERAL_RATE_SALE(NOT VAT REG)_{}.csv".format(
                datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'zero_rated_sale_sheet_d':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, 0, True)
            file_name = "ODOO_12_D_ZERO_RATE_SALE_{}.csv".format(datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'zero_rated_vat_non_reg_sale_sheet_d':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, 0, False)
            file_name = "ODOO_12_D_ZERO_RATE_SALE(NOT VAT REG)_{}.csv".format(
                datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'exempt_sale_sheet_e':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, None, True)
            file_name = "ODOO_12_E_EXEMPTED_SALE_{}.csv".format(datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'exempt_sale_vat_non_reg_sheet_e':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, None, False)
            file_name = "ODOO_12_E_EXEMPTED_SALE(NOT VAT REG)_{}.csv".format(
                datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'other_registered':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, 8, True)
            file_name = "ODOO_12_B_OTHER_RATE_SALE_{}.csv".format(datetime.now().strftime("%d_%m_%y-%H:%M:%S"))
        elif vatsheet == 'other_not_registered':
            csv_vat_data = self.worksheet_data(selected_description, start_date, end_date, company_id, 8, False)
            file_name = "ODOO_12_B_OTHER_RATE_SALE(NOT VAT REG)_{}.csv".format(
                datetime.now().strftime("%d_%m_%y-%H:%M:%S"))

        return request.make_response(csv_vat_data, [('Content-Type', 'text/csv'),
                                                    ('Content-Disposition', content_disposition(file_name))])

    def worksheet_data(self, selected_description, start_date, end_date, id_of_company, vat_group, vat_registered_cust):
        company_invoices = request.env['account.move'].search([('company_id', '=', id_of_company)])
        printable_invoices = request.env['account.move'].search(
            [('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date),
             ('state', '=', 'posted')])

        f = io.StringIO()
        writer = csv.writer(f)

        if printable_invoices:
            for cur_invo in printable_invoices:
                sale_type = "Local"
                buyer_pin = ""
                buyer_name = ""
                etr_no = None
                invo_date = None
                invo_no = ""
                description = ""
                taxable_value = 0
                has_kra_pin = False
                relevant_invo_no = None
                relevant_invo_date = None
                relevant_paragraph = "Category A"
                exempt_cert_no = ""

                if cur_invo:
                    if cur_invo.type == 'out_invoice' or cur_invo.type == 'out_refund':
                        cur_invo_line_items = cur_invo.invoice_line_ids
                        # cur_invo_taxes = cur_invo.tax_line_ids
                        if vat_group == 16 and vat_registered_cust:
                            taxable_value = 0
                            can_add_to_csv = False
                            this_is_cnote = False
                            tax_16_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'general'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_16_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                            can_add_to_csv = True
                                # if "16.00%" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == True and (
                                    taxable_value > 0 or this_is_cnote == True):
                                writer.writerow(
                                    [buyer_pin, buyer_name, etr_no, invo_date, invo_no, description, taxable_value,
                                     None, relevant_invo_no, relevant_invo_date])
                        elif vat_group == 16 and vat_registered_cust == False:
                            taxable_value = 0
                            this_is_cnote = False
                            can_add_to_csv = False
                            tax_16_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'general'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_16_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                            can_add_to_csv = True
                                # if "16" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == False and (
                                    taxable_value > 0 or this_is_cnote == True):
                                writer.writerow(
                                    [buyer_pin, buyer_name, etr_no, invo_date, invo_no, description, taxable_value,
                                     None, relevant_invo_no, relevant_invo_date])
                        elif vat_group == 0 and vat_registered_cust:
                            taxable_value = 0
                            this_is_cnote = False
                            tax_0_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'zero'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_0_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                # if "0" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                        sale_type = "Local"
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                                        sale_type = 'Local'
                                else:
                                    buyer_pin = ''
                                    has_kra_pin = False
                                    sale_type = 'Exemption'
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if sale_type.lower() == 'local' and has_kra_pin == True and taxable_value != 0 and taxable_value > 0:  # if sale_type.lower() == 'local' and taxable_value > 0 or this_is_cnote == True:
                                writer.writerow(
                                    [sale_type, buyer_pin, buyer_name, etr_no, invo_date, invo_no, description,
                                     relevant_paragraph, exempt_cert_no, taxable_value])
                        elif vat_group == 0 and vat_registered_cust == False:
                            taxable_value = 0
                            this_is_cnote = False
                            tax_0_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'zero'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_0_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                # if "0" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                        sale_type = "Local"
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                                        sale_type = 'Local'
                                else:
                                    buyer_pin = ''
                                    has_kra_pin = False
                                    sale_type = 'Exemption'
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == False and (
                                    taxable_value > 0 or this_is_cnote == True):
                                writer.writerow(
                                    [sale_type, buyer_pin, buyer_name, etr_no, invo_date, invo_no, description,
                                     relevant_paragraph, exempt_cert_no, taxable_value])
                        elif vat_group is None and vat_registered_cust:
                            taxable_value = 0
                            this_is_cnote = False
                            tax_exm_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'exempt'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_exm_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                # if "exempt" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == True and (
                                    taxable_value > 0 and this_is_cnote == True):
                                writer.writerow(
                                    [buyer_pin, buyer_name, etr_no, invo_date, invo_no, description, taxable_value])
                        elif vat_group is None and vat_registered_cust == False:
                            taxable_value = 0
                            this_is_cnote = False
                            tax_exm_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'exempt'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_exm_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                # if "exempt" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == False and (
                                    taxable_value > 0 or this_is_cnote == True):
                                writer.writerow(
                                    [buyer_pin, buyer_name, etr_no, invo_date, invo_no, description, taxable_value])
                        if vat_group == 8 and vat_registered_cust:
                            taxable_value = 0
                            can_add_to_csv = False
                            this_is_cnote = False
                            tax_16_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'other'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = cur_invo.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_16_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                            can_add_to_csv = True
                                # if "16.00%" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == True and (
                                    taxable_value > 0 or this_is_cnote == True):
                                writer.writerow(
                                    [buyer_pin, buyer_name, etr_no, invo_date, invo_no, description,
                                     taxable_value,
                                     None, relevant_invo_no, relevant_invo_date])
                        elif vat_group == 8 and vat_registered_cust == False:
                            taxable_value = 0
                            this_is_cnote = False
                            can_add_to_csv = False
                            tax_16_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'other'), ('type_tax_use', '=', 'sale')])
                            for inv_line in cur_invo_line_items:
                                used_currency_id = inv_line.currency_id
                                db_cur = request.env['res.currency'].search([('id', '=', used_currency_id.id)])
                                conv_rate = 1
                                if db_cur.name == 'USD':
                                    res_active_curr_rate = request.env['res.currency.rate'].search(
                                        [('currency_id', '=', used_currency_id.id),
                                         ('name', '=', cur_invo.invoice_date)])
                                    if not res_active_curr_rate:
                                        last_rate_entry = request.env['res.currency.rate'].search([
                                            ('currency_id', '=', used_currency_id.id),
                                            ('name', '<', cur_invo.invoice_date)
                                        ], order="name desc", limit=1)
                                        if last_rate_entry:
                                            the_rate = last_rate_entry.rate
                                        else:
                                            the_rate = 1
                                    else:
                                        the_rate = res_active_curr_rate.rate
                                    if the_rate:
                                        conv_rate = the_rate
                                if inv_line.tax_ids:
                                    for i_tax in inv_line.tax_ids:
                                        if tax_16_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal * conv_rate)
                                            buyer_name = cur_invo.partner_id.name
                                            invo_date = cur_invo.invoice_date
                                            invo_no = cur_invo.name if cur_invo.name else ''
                                            can_add_to_csv = True
                                # if "16" in str(inv_line.tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        buyer_pin = cur_invo.partner_id.pin
                                        has_kra_pin = True
                                    else:
                                        buyer_pin = ''
                                        has_kra_pin = False
                            if selected_description == 'sales':
                                description = 'Sales'
                            else:
                                for inv in cur_invo_line_items:
                                    if inv.product_id.barcode:
                                        description = '[' + inv.product_id.barcode + ']' + inv.product_id.name or inv.name
                                    else:
                                        description = inv.product_id.name or inv.name
                            if cur_invo.type == 'out_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                relevant_invo_no = cur_invo.invoice_origin if cur_invo.invoice_origin else ''
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                else:
                                    relevant_invo_date = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)]).invoice_date or ''
                            if taxable_value != 0 and has_kra_pin == False and (
                                    taxable_value > 0 or this_is_cnote == True):
                                writer.writerow(
                                    [buyer_pin, buyer_name, etr_no, invo_date, invo_no, description,
                                     taxable_value,
                                     None, relevant_invo_no, relevant_invo_date])

                                # TODO: EXECUTES AFTER CSV READER ARE CREATED
        f.seek(0)
        data = f.read()
        f.close()
        return data
