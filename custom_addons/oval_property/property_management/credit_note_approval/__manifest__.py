
{
    'name': 'Credit Note Approval',
    'version': '13.0.1.0.0',
    'summary': """
            Credit Note Approval.
     """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'license': 'LGPL-3',
    'website': 'http://serpentcs.in/product/property-management-system',
    'depends': ['account'],
    'data': ['security/group_credit_note.xml',
             'views/account_move_views.xml',
             ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
