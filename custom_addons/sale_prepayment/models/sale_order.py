from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prepayment_ids = fields.One2many('sale.prepayment', 'sale_order_id', string='Prepayments')

    def action_open_prepayment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Prepayment',
            'res_model': 'sale.prepayment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }
