from odoo import fields, models, _, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type_id = fields.Many2one('sale.order.type', string='Order Type')
    sequence_id = fields.Many2one('ir.sequence', related='order_type_id.sequence_id', string='Sequence', store=True,
                                  readonly=False)
    warehouse_id = fields.Many2one('stock.warehouse', related='order_type_id.warehouse_id', string='Warehouse',
                                   store=True, readonly=False)
    journal_id = fields.Many2one('account.journal', related='order_type_id.journal_id', string='Journal', store=True,
                                 readonly=False)

    # Used to store previous sequence names for order types
    _previous_order_type_sequences = {}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order_type_id = vals.get('order_type_id')
            name = vals.get('name', '/')
            if order_type_id and name in (False, '/', ''):
                order_type = self.env['sale.order.type'].browse(order_type_id)
                if order_type.sequence_id:
                    sequence_code = order_type.sequence_id.next_by_id()
                    vals['name'] = sequence_code
                    self._previous_order_type_sequences[order_type_id] = sequence_code
        return super().create(vals_list)

    def write(self, vals):
        for order in self:
            if order.state != 'draft':
                continue

            new_order_type_id = vals.get('order_type_id')
            current_order_type_id = order.order_type_id.id

            if new_order_type_id and new_order_type_id != current_order_type_id:
                # Store current name in the cache for current order type
                if current_order_type_id and order.name not in (False, '/', ''):
                    self._previous_order_type_sequences[current_order_type_id] = order.name

                if new_order_type_id in self._previous_order_type_sequences:
                    # Restore old sequence name if already used
                    vals['name'] = self._previous_order_type_sequences[new_order_type_id]
                else:
                    # Generate new if first time selected
                    new_order_type = self.env['sale.order.type'].browse(new_order_type_id)
                    if new_order_type.sequence_id:
                        new_sequence = new_order_type.sequence_id.next_by_id()
                        vals['name'] = new_sequence
                        self._previous_order_type_sequences[new_order_type_id] = new_sequence

        return super().write(vals)

    def action_confirm(self):
        # Confirm does not change sequence
        return super().action_confirm()

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['order_type_id'] = self.order_type_id.id
        return invoice_vals

    # def action_open_payment_form(self):
    #     self.ensure_one()
    #     # Step 1: Create the invoice (if not yet)
    #     invoice = self._create_invoices()
    #
    #     # Optional: Post it (if in draft)
    #     if invoice.state == 'draft':
    #         invoice.action_post()
    #
    #     # Step 2: Open register payment wizard
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Register Payment',
    #         'res_model': 'account.payment.register',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'active_model': 'account.move',
    #             'active_ids': [invoice.id],
    #         }
    #     }
    #
    # def action_create_invoice(self):
    #     self.ensure_one()
    #     invoice = self._create_invoices()
    #     invoice.action_post()
    #     return {
    #         'name': _('Invoice'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'form',
    #         'res_id': invoice.id,
    #         'target': 'current',
    #     }

#     def pay_now(self):
#         self.ensure_one()
#         if not any(line.qty_to_invoice > 0 for line in self.order_line):
#             raise UserError(
#                 _("Nothing to invoice. Make sure products use 'Ordered Quantities' or 'Prepaid' invoicing."))
#
#         return {
#             'type': 'ir.actions.act_window',
#             'name': _('Create Invoice'),
#             'res_model': 'sale.advance.payment.inv',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'active_model': 'sale.order',
#                 'active_ids': self.ids,
#                 'default_advance_payment_method': 'delivered',
#                 'custom_pay_now': True,  # flag to trigger auto pay in wizard
#             },
#         }
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     def action_post(self):
#         res = super().action_post()
#
#         invoices_to_pay = self.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted' and inv.amount_residual > 0)
#
#         for invoice in invoices_to_pay:
#             journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
#             if not journal:
#                 continue
#
#             payment_register = self.env['account.payment.register'].with_context(
#                 active_model='account.move',
#                 active_ids=invoice.ids,
#             ).create({
#                 'payment_date': fields.Date.today(),
#                 'journal_id': journal.id,
#                 'amount': invoice.amount_residual,
#             })
#             payment_register.action_create_payments()
#
#         return res

# def pay_now(self):
#     self.ensure_one()
#     invoice = self._create_invoices()
#     invoice.action_post()
#     return invoice.action_register_payment()

#     def pay_now(self):
#         self.ensure_one()
#         # Just an example to open the original payment popup if invoice exists, else show some message
#         invoices = self.invoice_ids.filtered(lambda inv: inv.state in ['draft', 'posted'])
#         if not invoices:
#             return {
#                 'type': 'ir.actions.act_window',
#                 'name': 'Register Payment',
#                 'res_model': 'account.payment',
#                 'view_mode': 'form',
#                 'target': 'new',
#                 'context': {
#                     'default_partner_type': 'customer',
#                     'default_payment_type': 'inbound',
#                     'default_partner_id': self.partner_id.id,
#                     'default_amount': self.amount_total,
#                     'default_journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
#                     'default_payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
#                     'default_communication': self.name,
#                 },
#             }
#         else:
#             return super(SaleOrder, self).action_payment_register()
#
#
#
# class AccountPaymentRegister(models.TransientModel):
#     _inherit = 'account.payment.register'
#
#     def action_create_payments(self):
#         payments = super().action_create_payments()
#         return {'type': 'ir.actions.act_window_close'}
