from odoo import models, fields

class SalePrepaymentWizard(models.TransientModel):
    _name = 'sale.prepayment.wizard'
    _description = 'Sale Prepayment Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)
    amount = fields.Monetary(required=True)
    payment_date = fields.Date(required=True, default=fields.Date.today)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other')
    ], required=True)
    note = fields.Char()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    def record_prepayment(self):
        self.env['sale.prepayment'].create({
            'sale_order_id': self.sale_order_id.id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_method': self.payment_method,
            'note': self.note,
            'currency_id': self.currency_id.id,
        })
