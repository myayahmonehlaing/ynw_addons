from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    consignment_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Consignment Warehouse'
    )