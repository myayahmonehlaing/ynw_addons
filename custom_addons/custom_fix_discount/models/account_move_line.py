from odoo import models, fields, api, _
from odoo.tools import frozendict

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fixed_discount = fields.Monetary(string='Fixed Discount', currency_field='currency_id')

    @api.depends('quantity', 'price_unit', 'discount', 'fixed_discount', 'tax_ids')
    def _compute_totals(self):
        for line in self:
            quantity = line.quantity or 1.0
            discount_pct = (line.discount or 0.0) / 100.0
            fixed_discount = line.fixed_discount or 0.0
            effective_price_unit = line.price_unit * (1 - discount_pct)
            total_price = effective_price_unit * quantity
            total_price_after_fixed = max(total_price - fixed_discount, 0.0)
            adjusted_price_unit = total_price_after_fixed / quantity if quantity else 0.0

            taxes = line.tax_ids.compute_all(
                adjusted_price_unit, quantity=quantity,
                product=line.product_id, partner=line.partner_id
            )

            line.price_subtotal = taxes['total_excluded']
            line.price_total = taxes['total_included']

    @api.depends('account_id', 'company_id', 'discount', 'fixed_discount', 'price_unit', 'quantity', 'currency_rate')
    def _compute_discount_allocation_needed(self):
        for line in self:
            line.discount_allocation_dirty = True
            discount_allocation_account = line.move_id._get_discount_allocation_account()

            if (not
                    not discount_allocation_account
                    or line.display_type != 'product'
                    or (
                    line.currency_id.is_zero(line.discount)
                    and line.currency_id.is_zero(line.fixed_discount)
            )
            ):
                line.discount_allocation_needed = False
                continue

            # Calculate percentage discount
            percent_discount_currency = line.currency_id.round(
                line.move_id.direction_sign * line.quantity * line.price_unit * (line.discount or 0.0) / 100.0
            )

            # Calculate fixed discount
            fixed_discount_currency = line.currency_id.round(
                line.move_id.direction_sign * (line.fixed_discount or 0.0)
            )

            # Total discount (both)
            total_discount_currency = percent_discount_currency + fixed_discount_currency

            discount_allocation_needed = {}

            # Decrease from line's account
            discount_allocation_needed_vals = discount_allocation_needed.setdefault(
                frozendict({
                    'account_id': line.account_id.id,
                    'move_id': line.move_id.id,
                    'currency_rate': line.currency_rate,
                }),
                {
                    'display_type': 'discount',
                    'name': _("Discount"),
                    'amount_currency': 0.0,
                },
            )
            discount_allocation_needed_vals['amount_currency'] += total_discount_currency

            # Increase to discount account
            discount_allocation_needed_vals = discount_allocation_needed.setdefault(
                frozendict({
                    'move_id': line.move_id.id,
                    'account_id': discount_allocation_account.id,
                    'currency_rate': line.currency_rate,
                }),
                {
                    'display_type': 'discount',
                    'name': _("Discount"),
                    'amount_currency': 0.0,
                },
            )
            discount_allocation_needed_vals['amount_currency'] -= total_discount_currency

            line.discount_allocation_needed = {
                k: frozendict(v) for k, v in discount_allocation_needed.items()
            }

