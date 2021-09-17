# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
{
    'name': 'Property Management - Odoo Enterprise Compatible',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'license': 'LGPL-3',
    'summary': """
        property management
        asset management
        tenancy tenant contract
        recurring contract
        penalty maintenance management
        property sale purchase
        booking management
        property rent sale purchase
     """,
    'description': """
        property management
        asset management
        tenancy tenant contract
        recurring contract
        penalty maintenance management
        property sale purchase
        booking management
        property rent sale purchase
     """,
    'sequence': 1,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.in/product/property-management-system',
    'depends': [
        'property_management_ee',
        'property_recurring_maintenance_ee',
        'property_penalty_ee',
        'property_sale_purchase_ee',
        'property_rent_report_ee',
        'property_booking_ee',
        'property_landlord_management_ee',
        'property_maintenance_ee',
        'multiple_property_rent_ee',
        'property_commission_ee',
        # 'property_website_ee'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price': 49,
    'currency': 'EUR',
}
