{
    'name': 'Eunoia Clinic',
    'version': '1.0',
    'summary': 'Manage patients, doctors, appointments, rooms, and departments in a clinic.',
    'category': 'Healthcare',
    'author': 'Yin Nyein Wai',
    'depends': ['base', 'hr', 'product', 'account', 'mail', 'mrp', 'sale_management', 'stock'],
    'data': [
        'security/clinic_model.xml',
        'security/clinic_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/patient_views.xml',
        'views/doctor_views.xml',
        'views/appointment_views.xml',
        'views/room_views.xml',
        'views/treatment_views.xml',
        'views/menu_views.xml',
        'views/res_users_views.xml',
        'views/mrp_line_form_view.xml',
        'views/sale_invoice_view.xml',
        'views/clinic_appointment_filter.xml',
        'report/report_treatment.xml',
        'report/report_treatment_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'clinic_management/static/src/js/calendar_open_form.js',
        ],
    },
    'application': True,

}
