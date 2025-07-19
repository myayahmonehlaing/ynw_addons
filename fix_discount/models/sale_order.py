from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total', 'order_line.price_subtotal', 'order_line.price_tax', 'order_line.fixdis')
    def _compute_amount(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line if not line.display_type)
            amount_tax = sum(line.price_tax for line in order.order_line if not line.display_type)
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': order.currency_id.round(amount_untaxed + amount_tax),
            })

