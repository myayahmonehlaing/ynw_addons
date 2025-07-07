{
    "name": "Curriculum Vitae",
    "website": "https://www.facebook.com/odooerpdevelopment",
    "category": "Productivity",
    "summary": "Custom module for the CV form creation!",
    "author": "YinNyeinWai",
    "application": True,
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
        "views/standard_cv_views.xml",
        "views/standard_cv_views_form.xml",
        "views/standard_cv_views_kanban.xml",
        "views/standard_cv_views_search.xml",
        "views/standard_cv_views_reporting.xml",
        "views/standard_cv_views_graph.xml",
        "views/standard_cv_views_pivot.xml",
        "views/standard_cv_views_calendar.xml",
"report/standard_cv_report_pdf.xml",
        "report/standard_cv_report_template.xml",

    ]
}
