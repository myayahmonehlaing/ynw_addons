# from odoo import models, fields, api
# from odoo.exceptions import UserError
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     fixed_discount = fields.Monetary(string='Fixed Discount', currency_field='currency_id')
#
#     @api.depends('order_line.price_subtotal', 'fixed_discount', 'currency_id', 'company_id')
#     def _compute_amount(self):
#         AccountTax = self.env['account.tax']
#         for order in self:
#             order_lines = order.order_line.filtered(lambda l: not l.display_type)
#             base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
#             AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
#             AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
#             tax_totals = AccountTax._get_tax_totals_summary(
#                 base_lines=base_lines,
#                 currency=order.currency_id or order.company_id.currency_id,
#                 company=order.company_id,
#             )
#             discount = order.fixed_discount or 0.0
#             order.amount_untaxed = tax_totals['base_amount_currency']
#             order.amount_tax = tax_totals['tax_amount_currency']
#             order.amount_total = max(tax_totals['total_amount_currency'] - discount, 0.0)
#
#
#
#     # def _prepare_invoice(self):
#     #     invoice_vals = super()._prepare_invoice()
#     #     invoice_vals['fixed_discount'] = self.fixed_discount or 0.0
#     #     return invoice_vals
#
#
#
#
#
#
#
#
#
#
#
#
#
#
