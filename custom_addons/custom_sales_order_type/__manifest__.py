{
    'name': 'Custom Sales Menu',
    'version': '1.0',
    'summary': 'Add Order Types to Sale Orders and Invoices',
    'author': 'Yin Nyein Wai',
    'depends': ['sale', 'account', 'base','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_type_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'report/sale_order_report_templates.xml',

    ],
    'installable': True,
    'application': False,
}
