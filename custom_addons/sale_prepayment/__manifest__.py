{
    "name": "Sale Prepayment",
    "version": "1.0",
    "depends": ["sale", "account"],
    "author": "Custom",
    "category": "Sales",
    "description": "Register payments before invoice in sale orders.",
    "data": [
        "views/sale_order_views.xml",
        "views/prepayment_views.xml",
        "wizard/prepayment_wizard_view.xml"
    ],
    "installable": True,
    "application": False
}
