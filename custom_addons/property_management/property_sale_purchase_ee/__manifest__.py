# See LICENSE file for full copyright and licensing details
{
    'name': 'Property Sales And Purchase EE',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'summary': """
        Property Sales And Purchase
        Asset sales purchase
        real estate sale purchase
        building sale purchase
     """,
    'license': 'LGPL-3',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.in/product/property-management-system',
    'depends': ['property_management_ee'],
    'data': [
        'security/ir.model.access.csv',
        'report/investment_report_view.xml',
        'views/sale_purchase_asset.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price': 49,
    'currency': 'EUR',
}
