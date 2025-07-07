from odoo import models, fields

class SalePrepayment(models.Model):
    _name = 'sale.prepayment'
    _description = 'Sale Order Prepayment'

    sale_order_id = fields.Many2one('sale.order', required=True, ondelete='cascade')
    amount = fields.Monetary(required=True)
    payment_date = fields.Date(required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other')
    ], required=True)
    note = fields.Char()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
