from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SalePaymentWizard(models.TransientModel):
    _name = 'sale.payment.wizard'
    _description = 'Sale Payment Wizard'

    sale_id = fields.Many2one('sale.order', string="Sale Order", required=True, readonly=True)
    journal_id = fields.Many2one('account.journal', required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
    recipient_bank_account_id = fields.Many2one('res.partner.bank', string='Recipient Bank Account')
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency')
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today)
    communication = fields.Char(string='Memo')
    writeoff_label = fields.Char(string='Label', default="Write-Off")
    writeoff_account_id = fields.Many2one('account.account', string='Write-Off Account')
    payment_difference = fields.Monetary(string='Payment Difference', compute='_compute_difference', currency_field='currency_id', store=True)
    payment_difference_handling = fields.Selection([
        ('open', 'Keep open'),
        ('reconcile', 'Mark as fully paid')
    ], string='Payment Difference Handling', default='open', required=True)

    @api.depends('amount', 'sale_id', 'currency_id')
    def _compute_difference(self):
        for rec in self:
            if rec.sale_id and rec.currency_id:
                rec.payment_difference = rec.sale_id.amount_total - rec.amount
            else:
                rec.payment_difference = 0.0

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            sale_order = self.env['sale.order'].browse(active_id)
            res.update({
                'sale_id': sale_order.id,
                'amount': sale_order.amount_total,
                'communication': sale_order.name,
            })
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            if not journal:
                raise UserError(_("No bank journal found."))
            res['journal_id'] = journal.id
            res['payment_method_id'] = journal.inbound_payment_method_line_ids[:1].payment_method_id.id
            res['currency_id'] = sale_order.currency_id.id or journal.currency_id.id or journal.company_id.currency_id.id
            res['writeoff_account_id'] = self.env['account.account'].search([('account_type', '=', 'other')], limit=1).id
        return res

    def create_payment(self):
        self.ensure_one()

        payment_method_line = self.journal_id.inbound_payment_method_line_ids[:1]
        if not payment_method_line:
            raise UserError(_("Selected journal has no inbound payment method lines."))

        payment_vals = {
            'partner_id': self.sale_id.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'journal_id': self.journal_id.id,
            'payment_method_line_id': payment_method_line.id,
            'date': self.payment_date,
            'payment_reference': self.communication or self.sale_id.name,
            'sale_order_ids': [(4, self.sale_id.id)],
            'destination_account_id': self.sale_id.partner_id.property_account_receivable_id.id,
        }

        if self.payment_difference and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = [{
                'name': self.writeoff_label or 'Write-Off',
                'amount': -self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }]

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # _logger.info("Payment created: %s", payment.name)
        #
        # # ✅ Try to reconcile immediately with any posted invoice
        # open_invoices = self.env['account.move'].search([
        #     ('partner_id', '=', self.sale_id.partner_id.id),
        #     ('move_type', '=', 'out_invoice'),
        #     ('state', '=', 'posted'),
        #     ('payment_state', '!=', 'paid'),
        #     ('invoice_origin', '=', self.sale_id.name),  # ← very important!
        # ])
        #
        # account = self.sale_id.partner_id.property_account_receivable_id
        #
        # for invoice in open_invoices:
        #     payment_lines = payment.move_id.line_ids.filtered(lambda l: l.account_id == account and not l.reconciled and l.credit > 0)
        #     invoice_lines = invoice.line_ids.filtered(lambda l: l.account_id == account and not l.reconciled and l.debit > 0)
        #
        #     to_reconcile = payment_lines + invoice_lines
        #     if to_reconcile:
        #         to_reconcile.reconcile()

        # ✅ Link payment to SO so smart button works
        self.sale_id.payment_ids = [(4, payment.id)]
        self.sale_id._compute_payments()

        return {'type': 'ir.actions.act_window_close'}

