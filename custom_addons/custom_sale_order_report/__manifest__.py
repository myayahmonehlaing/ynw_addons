{
    'name': 'Custom Sale Order Report',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds a delivery type field to Sales Orders and PDF printout',
    'depends': ['sale', 'stock', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/report_saleorder_document_inherit.xml',
    ],
    'installable': True,
    'application': False,

}
