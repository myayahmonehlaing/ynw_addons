{
    'name': 'Custom Invoice Report',
    'version': '1.0',
    'depends': ['account'],
    'category': 'Accounting',
    'summary': 'Remove discount line from invoice and show discount in totals',
    'description': """
        - Hides invoice lines where name is "discount"
        - Shows Discount separately in totals
        - Replaces Untaxed Amount with Sub Total
    """,
    'data': [
        'views/custom_invoice_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
