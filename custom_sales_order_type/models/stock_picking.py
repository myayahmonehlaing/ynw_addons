from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    order_type_id = fields.Many2one('sale.order.type', string="Order Type", compute='_compute_order_type', store=True)

    @api.depends('group_id')
    def _compute_order_type(self):
        for picking in self:
            sale_order = self.env['sale.order'].search([('procurement_group_id', '=', picking.group_id.id)], limit=1) if picking.group_id else False
            picking.order_type_id = sale_order.order_type_id if sale_order else False
