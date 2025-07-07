from odoo import models, fields, api
from odoo.exceptions import UserError

class PaymentWizard(models.TransientModel):
    _name = "payment.wizard"
    _description = "Payment Confirmation Wizard"

    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    payment_method = fields.Selection([
        ('manual', 'Manual Payment'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit Card')
    ], string="Payment Method", required=True)
    recipient_bank_account = fields.Char(string="Recipient Bank Account")
    payment_amount = fields.Float(string="Amount", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.today)
    memo = fields.Char(string="Memo")
    sequence_number = fields.Char(string="Sequence Number")

    def action_confirm_payment(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if sale_order.payment_status == 'paid':
            raise UserError("This order is already paid.")

        # Create draft invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': sale_order.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': sale_order.name,
                'quantity': 1,
                'price_unit': self.payment_amount
            })],
        })

        # Process payment
        payment = self.env['account.payment'].create({
            'amount': self.payment_amount,
            'currency_id': self.currency_id.id,
            'payment_type': 'inbound',
            'partner_id': sale_order.partner_id.id,
            'journal_id': self.journal_id.id,
            'payment_method_line_id': self.journal_id.inbound_payment_method_line_ids[:1].id,
            'date': self.payment_date,  # Use `date` instead of `payment_date`
            'memo': self.memo,
        })

        payment.action_post()

        # Mark invoice as paid & update sale order
        invoice.action_post()
        sale_order.payment_status = 'paid'

        return {'type': 'ir.actions.act_window_close'}
