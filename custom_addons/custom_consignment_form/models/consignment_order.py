from odoo import models, fields, api
from odoo.exceptions import UserError


class ConsignmentOrder(models.Model):
    _name = 'consignment.order'
    _description = 'Consignment Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_order = fields.Datetime(string='Date', default=fields.Datetime.now)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type', domain=[('code', '=', 'internal')])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True,
                                 tracking=True)
    order_line_ids = fields.One2many('consignment.order.line', 'order_id', string='Order Lines')
    optional_line_ids = fields.One2many('consignment.order.line', 'optional_order_id', string='Optional Products')
    note = fields.Text(string='Notes')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    picking_ids = fields.One2many('stock.picking', 'origin_consignment_id', string='Transfers')
    picking_count = fields.Integer(string="Transfers Count", compute="_compute_picking_count")

    sale_order_ids = fields.One2many('sale.order', 'consignment_id', string="Sale Orders")
    sale_order_count = fields.Integer(string='Sale Order Count', compute="_compute_sale_order_count")

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    @api.depends('order_line_ids.price_subtotal', 'optional_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.order_line_ids.mapped('price_subtotal')) + \
                                 sum(order.optional_line_ids.mapped('price_subtotal'))

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('consignment.order') or 'New'
        if 'company_id' not in vals:
            vals['company_id'] = self.env.company.id
        return super().create(vals)

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_confirm(self):
        self.ensure_one()
        if not self.picking_type_id:
            raise UserError("Please select an Operation Type before confirming the order.")

        warehouse = self.company_id.consignment_warehouse_id
        if not warehouse:
            raise UserError(
                "Please configure a Consignment Warehouse for company %s in Sales Settings." % self.company_id.name)

        destination_location = warehouse.lot_stock_id
        if not destination_location:
            raise UserError("The selected warehouse does not have a destination location.")

        self.write({'state': 'confirmed'})

        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'origin': self.name,
            'scheduled_date': self.date_order,
            'origin_consignment_id': self.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': destination_location.id,
            'move_ids_without_package': [
                (0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.picking_type_id.default_location_src_id.id,
                    'location_dest_id': destination_location.id,
                }) for line in self.order_line_ids
            ],
        })

        picking.action_confirm()

    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        sale_orders = self.sale_order_ids
        if len(sale_orders) > 1:
            action['domain'] = [('id', 'in', sale_orders.ids)]
        elif len(sale_orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = sale_orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def open_picking_view(self):
        self.ensure_one()
        result = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        if len(self.picking_ids) > 1:
            result['domain'] = [('id', 'in', self.picking_ids.ids)]
        elif len(self.picking_ids) == 1:
            result['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            result['res_id'] = self.picking_ids.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        result['context'] = {'create': False}
        return result

    @api.onchange('company_id')
    def _onchange_company_id(self):
        # Filter order_line_ids and optional_line_ids to current company
        if self.company_id:
            lines = self.order_line_ids.filtered(lambda l: l.company_id == self.company_id)
            optional_lines = self.optional_line_ids.filtered(lambda l: l.company_id == self.company_id)
            self.order_line_ids = [(6, 0, lines.ids)]
            self.optional_line_ids = [(6, 0, optional_lines.ids)]

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        if self.pricelist_id:
            self.currency_id = self.pricelist_id.currency_id

