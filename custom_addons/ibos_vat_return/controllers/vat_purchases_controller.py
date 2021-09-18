# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.http import request
from odoo import http
import csv
import io
import base64


class KraVatPurchasesController(http.Controller):

    @http.route('/accounts/downloads/vat/return/purchases/csv', type='http', auth='public', website=False)
    def download_purchase_vat_csv_sheet(self, model, vatsheet, company_id, start_date, end_date, file_name=None, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        csv_vat_data = None

        if vatsheet == 'general_rated_purchase_sheet_f':
            csv_vat_data = self.worksheet_data(start_date, end_date, company_id, 16)
            file_name = 'ODOO_12_F_GENERAL_RATE_PURCHASE_{}.csv'.format(datetime.now().strftime('%d_%m_%y-%H:%M:%S'))
        elif vatsheet == 'zero_rated_purchase_sheet_h':
            csv_vat_data = self.worksheet_data(start_date, end_date, company_id, 0)
            file_name = 'ODOO_12_H_ZERO_RATE_PURCHASE_{}.csv'.format(datetime.now().strftime('%d_%m_%y-%H:%M:%S'))
        elif vatsheet == 'exempt_purchase_sheet_i':
            csv_vat_data = self.worksheet_data(start_date, end_date, company_id, None)
            file_name = 'ODOO_12_I_EXEMPTED_PURCHASE_{}.csv'.format(datetime.now().strftime('%d_%m_%y-%H:%M:%S'))
        elif vatsheet == 'other_rated_purchase_sheet_g':
            csv_vat_data = self.worksheet_data(start_date, end_date, company_id, 8)
            file_name = 'ODOO_12_G_OTHER_RATE_PURCHASE_{}.csv'.format(datetime.now().strftime('%d_%m_%y-%H:%M:%S'))

        return request.make_response(csv_vat_data, [('Content-Type', 'text/csv'),
                                                    ('Content-Disposition', content_disposition(file_name))])

    def worksheet_data(self, start_date, end_date, id_of_company, vat_group):
        company_invoices = request.env['account.move'].search([('company_id', '=', id_of_company)])
        printable_invoices = request.env['account.move'].search(
            [('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date), ('state', '=', 'posted')])

        f = io.StringIO()
        writer = csv.writer(f)

        if printable_invoices:
            for cur_invo in printable_invoices:
                purchase_type = "Local"
                seller_pin = ""
                seller_name = ""
                invo_date = None
                invo_no = ""
                description = ""
                import_type = "Goods"
                custom_entry_no = ""
                taxable_value = ""
                vat_amt = None
                relevant_inv_no = None
                relevant_inv_date = None

                if cur_invo:
                    if cur_invo.type == 'in_invoice' or cur_invo.type == 'in_refund':
                        cur_invo_line_items = cur_invo.invoice_line_ids
                        # cur_invo_taxes = cur_invo.tax_line_ids
                        if vat_group == 16:
                            taxable_value = 0
                            this_is_cnote = False
                            can_add_to_csv = False
                            tax_16_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'general'), ('type_tax_use', '=', 'purchase')])
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
                                            taxable_value += (inv_line.price_subtotal / conv_rate)
                                            can_add_to_csv = True
                                # if "16" in str(inv_line.invoice_line_tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)

                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        seller_pin = cur_invo.partner_id.pin
                                        purchase_type = "Local"
                                    else:
                                        seller_pin = ''
                                        purchase_type = "Import"
                            seller_name = cur_invo.partner_id.name
                            invo_date = datetime.strftime(cur_invo.invoice_date, DEFAULT_SERVER_DATE_FORMAT) or ''
                            invo_no = cur_invo.name if cur_invo.name else ''
                            description = 'Purchases'
                            if cur_invo.type == 'in_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                    relevant_invo_no = ''
                                else:
                                    relevant_invo = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)])
                                    if relevant_invo:
                                        relevant_invo_no = relevant_invo.reference if relevant_invo.reference else ''
                                        relevant_invo_date = relevant_invo.invoice_date if relevant_invo.invoice_date else ''
                            if taxable_value > 0 or this_is_cnote is True:
                                writer.writerow(
                                    [purchase_type, seller_pin, seller_name, invo_date, invo_no, description,
                                     custom_entry_no, taxable_value,
                                     vat_amt, relevant_inv_no, relevant_inv_date])
                        elif vat_group == 0:
                            taxable_value = 0
                            tax_0_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'zero'), ('type_tax_use', '=', 'purchase')])
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
                                            taxable_value += (inv_line.price_subtotal / conv_rate)
                                # if "0" in str(inv_line.invoice_line_tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        seller_pin = cur_invo.partner_id.pin
                                        purchase_type = "Local"
                                    else:
                                        seller_pin = ''
                                        purchase_type = "Import"
                            seller_name = cur_invo.partner_id.name
                            invo_date = datetime.strftime(cur_invo.invoice_date, DEFAULT_SERVER_DATE_FORMAT) or ''
                            invo_no = cur_invo.name if cur_invo.name else ''
                            description = 'Purchases'
                            if taxable_value > 0:
                                writer.writerow(
                                    [purchase_type, seller_pin, seller_name, invo_date, invo_no, import_type,
                                     description, custom_entry_no, taxable_value])
                        elif vat_group is None:
                            taxable_value = 0
                            tax_exm_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'exempt'), ('type_tax_use', '=', 'purchase')])
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
                                            taxable_value += (inv_line.price_subtotal / conv_rate)
                                # if "exempt" in str(inv_line.invoice_line_tax_ids.name).lower():
                                #     taxable_value += (inv_line.price_subtotal / conv_rate)
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        seller_pin = cur_invo.partner_id.pin
                                        purchase_type = "Local"
                                    else:
                                        seller_pin = ''
                                        purchase_type = "Import"
                            seller_name = cur_invo.partner_id.name
                            invo_date = datetime.strftime(cur_invo.invoice_date, DEFAULT_SERVER_DATE_FORMAT) or ''
                            invo_no = cur_invo.name if cur_invo.name else ''
                            description = 'Purchases'
                            if taxable_value > 0:
                                writer.writerow(
                                    [purchase_type, seller_pin, seller_name, invo_date, invo_no, description,
                                     custom_entry_no, taxable_value])
                        elif vat_group == 8:
                            taxable_value = 0
                            this_is_cnote = False
                            tax_8_percent = request.env['account.tax'].search(
                                [('sheet_type', '=', 'other'), ('type_tax_use', '=', 'purchase')])
                            for inv_line in cur_invo_line_items:
                                can_add_to_csv = False
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
                                        if tax_8_percent.id == i_tax.id:
                                            taxable_value += (inv_line.price_subtotal / conv_rate)
                                            can_add_to_csv = True
                            if cur_invo.partner_id.country_id:
                                str_kenyan = cur_invo.partner_id.country_id.name
                                if str_kenyan.lower() == 'kenya':
                                    if cur_invo.partner_id.pin:
                                        seller_pin = cur_invo.partner_id.pin
                                        purchase_type = "Local"
                                    else:
                                        seller_pin = ''
                                        purchase_type = "Import"
                            seller_name = cur_invo.partner_id.name
                            invo_date = datetime.strftime(cur_invo.invoice_date, DEFAULT_SERVER_DATE_FORMAT) or ''
                            invo_no = cur_invo.name if cur_invo.name else ''
                            description = 'Purchases'
                            if cur_invo.type == 'in_refund':
                                taxable_value = (-taxable_value)
                                this_is_cnote = True
                                if cur_invo.invoice_origin is False or cur_invo.invoice_origin == '':
                                    relevant_invo_date = ''
                                    relevant_invo_no = ''
                                else:
                                    relevant_invo = request.env['account.move'].search(
                                        [('name', '=', cur_invo.invoice_origin)])
                                    if relevant_invo:
                                        relevant_invo_no = relevant_invo.reference if relevant_invo.reference else ''
                                        relevant_invo_date = relevant_invo.invoice_date if relevant_invo.invoice_date else ''
                            if taxable_value > 0 or this_is_cnote is True:
                                writer.writerow(
                                    [purchase_type, seller_pin, seller_name, invo_date, invo_no, description,
                                     custom_entry_no, taxable_value,
                                     vat_amt, relevant_inv_no, relevant_inv_date])

        # TODO: EXECUTES AFTER CSV READER ARE CREATED
        f.seek(0)
        data = f.read()
        f.close()
        return data
