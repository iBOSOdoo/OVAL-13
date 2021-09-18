# -*- coding: utf-8 -*-

{
    'name': 'Kenya VAT Return',
    'version': '1.1',
    'author': 'Integrity Business Outsourcing Solutions',
    'website': 'http://ibos.co.ke',
    'category': 'Accounting',
    'description': """
KRA Compliant Importable VAT Return CSV Documents
=================================================

This module goes through all the sales and purchases transactions, gets all the vat details required
for import to KRA standard macro enabled excel workbook version 11.0.4

    """,
    'depends': ['account', 'l10n_ke', 'ibos_kra_pin_validation'],
    'data': [
        'views/vat_popup_modal_view.xml',
        'views/account_tax_view.xml'
    ],
    'application': False
}
