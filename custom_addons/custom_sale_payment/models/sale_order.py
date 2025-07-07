from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], string="Payment Status", default="unpaid")

    def action_pay_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm Payment',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_amount': self.amount_total,
                'default_currency_id': self.currency_id.id,
            }
        }
class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_method = fields.Selection([
        ('manual', 'Manual Payment'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit Card')
    ], string="Payment Method")



