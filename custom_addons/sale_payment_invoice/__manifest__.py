{
    'name': 'Sale Payment Invoice',
    'version': '1.0',
    'depends': ['account', 'sale', 'payment', 'sale_management'],
    'author': 'YinNyeinWai',
    'category': 'Sales',
    'data': [
        'views/sale_order_views.xml',
        'views/sale_payment_wizard_view.xml',
        'views/account_payment_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
