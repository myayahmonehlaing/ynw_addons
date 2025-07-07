from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    order_type_id = fields.Many2one('sale.order.type', string='Order Type')