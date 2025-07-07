{
    'name': 'Custom Discount Fix',
    'version': '1.0',
    'summary': 'Add fixed discount to Sale Orders and Invoices',
    'author': 'Yin Nyein Wai',
    'depends': ['sale', 'account', 'sale_management', 'base'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/account_move_views.xml',
        'views/sale_order_views.xml',

    ],
    'installable': True,
    'application': False,
}
