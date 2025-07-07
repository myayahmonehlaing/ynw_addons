from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fixdis = fields.Float(string="Fix Discount", default=0.0)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'fixdis')
    def _compute_amount(self):
        for line in self:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit = max(price_unit - line.fixdis, 0.0)

            taxes = line.tax_id.compute_all(
                price_unit,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })



