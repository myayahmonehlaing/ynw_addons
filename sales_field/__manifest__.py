{
    "name": "Sales Field",
    "website": "https://www.facebook.com/odooerpdevelopment",
    "category": "Productivity",
    "summary": "Extra field in Sales",
    "author": "YinNyeinWai",
    "application": True,
    # "depends": ["base"],
    "depends": ['base','sale'],
    "data": [
        "views/salesfield_views.xml",
        "security/security.xml",
        # "report/standard_cv_report_pdf.xml",
        # "report/standard_cv_report_template.xml",

    ]
}