{
    'name': 'Sale Order Direct Payment',
    'version': '1.0',
    'depends': ['sale_management', 'account', 'sale'],
    'author': 'YinNyeinWai',
    'category': 'Sales',
    'data': [
        'views/sale_order_view.xml',
        'views/payment_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
