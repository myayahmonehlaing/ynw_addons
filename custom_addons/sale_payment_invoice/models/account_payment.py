from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
