{
    'name': 'Property Meter Reading',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'summary': """
            Property Meter Reading System.
     """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'license': 'LGPL-3',
    'website': 'http://serpentcs.in/product/property-management-system',
    'depends': ['property_ee', 'account_asset','property_management_ee', 'base'],
    'data': ['security/ir.model.access.csv',
             'views/view_property_meter.xml',
             'views/view_account_analytic.xml',
             'views/view_res_company.xml',
             'views/inherit_invoice_template.xml',
             'views/custom_invoice.xml'],
    'auto_install': False,
    'installable': True,
    'application': True,
}
