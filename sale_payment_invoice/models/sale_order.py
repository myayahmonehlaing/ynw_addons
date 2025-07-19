from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_ids = fields.Many2many('account.payment', compute='_compute_payments', string='Payments')
    payment_count = fields.Integer(compute='_compute_payments', string='Payments', store=True)

    @api.depends('payment_ids')
    def _compute_payments(self):
        for order in self:
            payments = self.env['account.payment'].search([('sale_order_ids', 'in', order.id)])
            order.payment_ids = payments
            order.payment_count = len(payments)

    def action_open_payment_wizard(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'sale.payment.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'active_model': 'sale.order',
                'active_id': self.id,
                'default_memo': self.name,
            }
        }

    def action_view_payments(self):
        self.ensure_one()
        payment_ids = self.payment_ids.ids

        if not payment_ids:
            return {'type': 'ir.actions.act_window_close'}

        if len(payment_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Customer Payment'),
                'res_model': 'account.payment',
                'res_id': payment_ids[0],
                'view_mode': 'form',
                'view_id': self.env.ref('account.view_account_payment_form').id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Customer Payments'),
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payment_ids)],
                'context': {'create': False},
            }

    # def action_view_payments(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_payments")
    #     action['domain'] = [('sale_order_ids', 'in', self.ids)]
    #     action['context'] = {'create': False}
    #     return action

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['invoice_origin'] = self.name  # Ensure linkage
        return invoice_vals

