# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api, _
from datetime import date
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from odoo import http
from odoo.http import request


class VatPurchaseExportWizard(models.TransientModel):
    _name = "vat.purchase.export.wizard"

    from_date = fields.Date(string='Return Period From', required=True)
    to_date = fields.Date(string='Return Period To', required=True)
    vat_type = fields.Selection([
        ('general_rated_purchase_sheet_f', 'F_General_Rated_Purchase_Dtls'),
        ('zero_rated_purchase_sheet_h', 'H_Zero_Rated_Purchase_Dtls'),
        ('exempt_purchase_sheet_i', 'I_Exempted_Purchases_Dtls'),
        ('other_rated_purchase_sheet_g', 'G_Other_Rated_Purchase_Dtls')
    ], string='VAT Sheet No.', required=True)

    def kra_purchase_vat_import_csv(self):
        if (not self.from_date is False) and (not self.to_date is False):
            selected_vat_sheet = self.vat_type
            return {
                'type': 'ir.actions.act_url',
                'target': 'blank',
                'url': "/accounts/downloads/vat/return/purchases/csv?model=account.move&vatsheet={}&company_id={}&start_date={}&end_date={}&file_name=purchase_vat.csv".format(
                    selected_vat_sheet, self.env.user.company_id.id, self.from_date, self.to_date)
            }


class VatSaleExportWizard(models.TransientModel):
    _name = "vat.sale.export.wizard"

    from_date = fields.Date(string='Return Period From', required=True)
    to_date = fields.Date(string='Return Period To', required=True)
    vat_type = fields.Selection([
        ('general_rated_sale_sheet_b', 'B_General_Rated_Sales_Dtls'),
        ('general_rated_vat_non_reg_sale_sheet_b', 'B_General_Rated_Sales_Dtls(NOT VAT REGISTERED)'),
        ('zero_rated_sale_sheet_d', 'D_Zero_Rated_Sales_Dtls'),
        ('zero_rated_vat_non_reg_sale_sheet_d', 'D_Zero_Rated_Sales_Dtls(NOT VAT REGISTERED)'),
        ('exempt_sale_sheet_e', 'E_Exempted_Sales_Dtls'),
        ('exempt_sale_vat_non_reg_sheet_e', 'E_Exempted_Sales_Dtls(NOT VAT REGISTERED)'),
        ('other_registered', 'Other Registered'),
        ('other_not_registered', 'Other Not Registered')
    ], string='VAT Sheet No.', required=True)
    description = fields.Selection([
        ('sales', 'Sales'),
        ('product_name', 'Product Name')
    ], string='Description', required=True)

    def kra_sales_vat_import_csv(self):
        if (not self.from_date is False) and (not self.to_date is False):
            selected_vat_sheet = self.vat_type
            selected_description = self.description
            return {
                'type': 'ir.actions.act_url',
                'target': 'blank',
                'url': "/accounts/downloads/vat/return/sales/csv?model=account.move&selected_description={}&vatsheet={}&company_id={}&start_date={}&end_date={}&file_name=sale_vat.csv".format(
                    selected_description, selected_vat_sheet, self.env.user.company_id.id, self.from_date, self.to_date)
            }
