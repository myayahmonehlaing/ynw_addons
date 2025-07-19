{
    'name': "Consignment Orders",
    'version': '1.0',
    'depends': ['base', 'sale', 'stock'],
    'category': 'Sales',
    'description': "Manage Consignment Orders like Sale Orders",
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/consignment_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/pivot_view.xml',
        'report/report_consignment_order.xml',
        'report/report_consignment_order_template.xml',
        'report/consignment_report_wizard.xml',
        'report/consignment_qweb_template.xml',
    ],

    'installable': True,
    'application': False,
}
