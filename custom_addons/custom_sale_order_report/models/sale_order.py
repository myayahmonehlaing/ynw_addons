from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_type_id = fields.Many2one(
        'stock.picking.type',
        string="Delivery Type"
    )
