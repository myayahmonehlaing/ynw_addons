from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    consignment_id = fields.Many2one('consignment.order', string="Consignment")

    @api.onchange('consignment_id')
    def _onchange_consignment_id(self):
        if self.consignment_id:
            self.partner_id = self.consignment_id.partner_id
            self.order_line = [(5, 0, 0)]  # Clear existing order lines

            lines = []
            for line in self.consignment_id.order_line_ids:
                remaining_qty = line.product_uom_qty - line.sold_qty
                if remaining_qty > 0:
                    lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': remaining_qty,
                        'price_unit': line.price_unit,
                        'product_uom': line.product_id.uom_id.id,
                    }))
            self.order_line = lines

            warehouse = self.env.company.consignment_warehouse_id
            if warehouse:
                self.warehouse_id = warehouse.id

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.consignment_id:
                for so_line in order.order_line:
                    consignment_line = order.consignment_id.order_line_ids.filtered(
                        lambda l: l.product_id == so_line.product_id)
                    if consignment_line:
                        consignment_line.sold_qty += so_line.product_uom_qty
        return res
