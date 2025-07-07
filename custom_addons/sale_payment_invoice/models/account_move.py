# from odoo import models,fields
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     sale_order_id = fields.Many2one('sale.order', string="Sales Order")
#
#     def action_post(self):
#         res = super().action_post()
#         for move in self:
#             if move.move_type == 'out_invoice' and move.sale_order_id:
#                 sale_order = move.sale_order_id
#                 for payment in sale_order.payment_ids.filtered(lambda p: p.state == 'posted' and p.partner_id == move.partner_id):
#                     payment_lines = payment.line_ids.filtered(
#                         lambda l: l.account_id == move.partner_id.property_account_receivable_id and not l.reconciled
#                     )
#                     invoice_lines = move.line_ids.filtered(
#                         lambda l: l.account_id == move.partner_id.property_account_receivable_id and not l.reconciled
#                     )
#                     if payment_lines and invoice_lines:
#                         (payment_lines + invoice_lines).reconcile()
#         return res


# from odoo import models
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     def action_post(self):
#         res = super().action_post()
#         for move in self:
#             if move.move_type == 'out_invoice' and move.partner_id:
#                 # Try linking via invoice_origin or sale lines
#                 sale_orders = self.env['sale.order']
#                 if move.invoice_origin:
#                     sale_orders = self.env['sale.order'].search([('name', '=', move.invoice_origin)])
#                 if not sale_orders and move.invoice_line_ids:
#                     sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
#                 for sale_order in sale_orders:
#                     for payment in sale_order.payment_ids.filtered(
#                             lambda p: p.state == 'posted' and p.partner_id == move.partner_id):
#                         account = move.partner_id.property_account_receivable_id
#                         payment_lines = payment.line_ids.filtered(
#                             lambda l: l.account_id == account and not l.reconciled)
#                         invoice_lines = move.line_ids.filtered(lambda l: l.account_id == account and not l.reconciled)
#                         (payment_lines + invoice_lines).reconcile()
#         return res


from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)
        # Optional: put a log to verify the invoice_origin
        _logger.info("Invoice created with origin: %s", move.invoice_origin)
        return move

    def action_post(self):
        res = super().action_post()

        for move in self:
            if move.move_type == 'out_invoice' and move.invoice_origin:
                sale_order = self.env['sale.order'].search([
                    ('name', '=', move.invoice_origin)
                ], limit=1)

                if sale_order and sale_order.payment_ids:
                    account = move.partner_id.property_account_receivable_id

                    payment_lines = sale_order.payment_ids.mapped('move_id.line_ids').filtered(
                        lambda l: l.account_id == account and not l.reconciled and l.credit > 0
                    )

                    invoice_lines = move.line_ids.filtered(
                        lambda l: l.account_id == account and not l.reconciled and l.debit > 0
                    )

                    lines_to_reconcile = payment_lines + invoice_lines
                    if lines_to_reconcile:
                        _logger.info("Reconciling payment lines and invoice lines for move %s", move.name)
                        lines_to_reconcile.reconcile()

        return res







