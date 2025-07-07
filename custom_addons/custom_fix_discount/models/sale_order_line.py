from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fixed_discount = fields.Monetary(string='Fixed Discount', currency_field='currency_id')

    @api.model
    def _prepare_base_line_for_taxes_computation(self):
        base_line = super()._prepare_base_line_for_taxes_computation()
        fixed_discount = self.fixed_discount or 0.0
        discount = self.discount or 0.0

        price_unit_after_discount = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        total_price = price_unit_after_discount * self.product_uom_qty
        total_price_after_fixed_discount = max(total_price - fixed_discount, 0.0)

        unit_price_for_tax = total_price_after_fixed_discount / self.product_uom_qty if self.product_uom_qty else 0.0
        base_line['price_unit'] = unit_price_for_tax
        base_line['discount'] = 0.0
        return base_line

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'fixed_discount')
    def _compute_amount(self):
        for line in self:
            base_line = line._prepare_base_line_for_taxes_computation()
            self.env['account.tax']._add_tax_details_in_base_line(base_line, line.company_id)
            line.price_subtotal = base_line['tax_details']['raw_total_excluded_currency']
            line.price_total = base_line['tax_details']['raw_total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res['fixed_discount'] = self.fixed_discount or 0.0
        return res


