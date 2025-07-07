from odoo import models, fields, api


class ConsignmentOrderLine(models.Model):
    _name = 'consignment.order.line'
    _description = 'Consignment Order Line'

    partner_id = fields.Many2one('res.partner', string="Customer", related='order_id.partner_id', store=True)
    order_date = fields.Datetime(string="Order Date", related='order_id.date_order', store=True)
    filter_date = fields.Date(string='Filter Date', store=True)

    remaining_qty_at_filter_date = fields.Float(
        string='Remaining Qty',
        compute='_compute_remaining_qty_at_filter_date',
        store=True,
    )
    order_id = fields.Many2one('consignment.order', string='Order Reference', ondelete='cascade')
    optional_order_id = fields.Many2one('consignment.order', string='Optional Order Ref', ondelete='cascade')

    company_id = fields.Many2one('res.company', string='Company', related='order_id.company_id', store=True,
                                 readonly=True)

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='order_id.pricelist_id.currency_id',
        store=True,
        readonly=True
    )

    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id'
    )

    sold_qty = fields.Float(string="Sold Qty", default=0.0)
    remaining_qty = fields.Float(string="Remain Qty", compute="_compute_remaining_qty", store=True)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    @api.depends('product_uom_qty', 'sold_qty')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.product_uom_qty - line.sold_qty

    @api.onchange('product_id', 'order_id.currency_id', 'optional_order_id.currency_id')
    def _onchange_product_id(self):
        for line in self:
            order = line.order_id or line.optional_order_id
            if order and line.product_id:
                base_price = line.product_id.list_price
                order_currency = order.currency_id or self.env.company.currency_id
                company_currency = self.env.company.currency_id
                price = company_currency._convert(
                    base_price,
                    order_currency,
                    self.env.company,
                    fields.Date.today()
                )

                line.price_unit = price

    @api.model
    def create(self, vals):
        if 'order_id' in vals and not vals.get('company_id'):
            order = self.env['consignment.order'].browse(vals['order_id'])
            vals['company_id'] = order.company_id.id
        return super().create(vals)

    def sold_qty_up_to_date(self, date_str):
        self.ensure_one()
        SaleOrderLine = self.env['sale.order.line']
        domain = [
            ('order_id.partner_id', '=', self.order_id.partner_id.id),
            ('product_id', '=', self.product_id.id),
            ('order_id.date_order', '<=', date_str + ' 23:59:59'),
            ('order_id.state', 'in', ['sale', 'done'])
        ]
        sold_lines = SaleOrderLine.search(domain)
        return sum(sold_lines.mapped('product_uom_qty'))

    def remaining_qty_at_date(self, date_str):
        self.ensure_one()
        sold_qty = self.sold_qty_up_to_date(date_str)
        return max(self.product_uom_qty - sold_qty, 0)

    @api.depends('filter_date', 'product_uom_qty', 'order_id.partner_id', 'product_id')
    def _compute_remaining_qty_at_filter_date(self):
        for line in self:
            date_str = line.filter_date.strftime('%Y-%m-%d') if line.filter_date else fields.Date.today().strftime(
                '%Y-%m-%d')
            sold_lines = self.env['sale.order.line'].search([
                ('order_id.partner_id', '=', line.order_id.partner_id.id),
                ('product_id', '=', line.product_id.id),
                ('order_id.date_order', '<=', date_str + ' 23:59:59'),
                ('order_id.state', 'in', ['sale', 'done']),
            ])
            sold_qty = sum(sold_lines.mapped('product_uom_qty'))
            line.remaining_qty_at_filter_date = max(line.product_uom_qty - sold_qty, 0)
