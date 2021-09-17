# See LICENSE file for full copyright and licensing details
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%d'

class document_expiry(models.AbstractModel):
    _name = 'report.property_management_ee.report_document_expiry'
    _description = 'Document Expiry Report'

    def get_details(self, start_date, end_date):
        data_1 = []
        certificate_obj = self.env["property.attachment"]
        certificate_ids = certificate_obj.search(
            [('expiry_date', '>=', start_date),
             ('expiry_date', '<=', end_date)])
        for data in certificate_ids:
            data_1.append({
                'name': data.name,
                'property_id': data.property_id.name,
                'expiry_date': data.expiry_date,
            })
        return data_1

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        start_date_obj = datetime.strptime(data['form'].get('start_date'), '%Y-%m-%d')
        start_date_report = start_date_obj.strftime('%m-%d-%Y')
        end_date_obj = datetime.strptime(data['form'].get('end_date'), '%Y-%m-%d')
        end_date_report = end_date_obj.strftime('%m-%d-%Y')
        start_date = data['form'].get('start_date', fields.Date.today())
        end_date = data['form'].get(
            'end_date', str(datetime.now() + relativedelta(
                months=+1, day=1, days=-1))[:10])
        detail_res = self.with_context(
            data['form'].get('used_context', {})).get_details(
                start_date, end_date)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_details': detail_res,
        }
        docargs['data'].update({
            'end_date': end_date_report,
            'start_date': start_date_report})
        return docargs
