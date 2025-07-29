from odoo import models, fields, api
from odoo.exceptions import UserError


class ClinicTreatment(models.Model):
    _name = 'clinic.treatment'
    _description = 'Clinic Treatment'
    _order = 'date_start desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', default='New', required=True, readonly=True, copy=False)

    appointment_id = fields.Many2one(
        'clinic.appointment',
        string='Related Appointment',
        domain="[('state', 'in', ['consulted'])]"  # ✅ Only show valid states
    )
    patient_id = fields.Many2one('clinic.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hr.employee', string='Doctor', required=True, tracking=True)
    date_start = fields.Datetime(string='Start Time', required=True, tracking=True)
    date_end = fields.Datetime(string='End Time', required=True, tracking=True)
    room_id = fields.Many2one('clinic.room', string="Room", tracking=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True,
                                   default=lambda self: self.env['product.pricelist'].search([], limit=1))
    currency_id = fields.Many2one(
        'res.currency',
        related='pricelist_id.currency_id',
        string='Currency',
        readonly=True
    )

    line_ids = fields.One2many('clinic.treatment.line', 'treatment_id', string='Treatment Lines')

    amount_total = fields.Float(string='Total', compute='_compute_amount_total', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    # Related records
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    picking_id = fields.Many2one('stock.picking', string="Delivery", readonly=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    # Count fields for smart buttons
    sale_order_count = fields.Integer(compute="_compute_counts", string="Sale Orders")
    delivery_count = fields.Integer(compute="_compute_counts", string="Deliveries")
    invoice_count = fields.Integer(compute="_compute_counts", string="Invoices")

    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one(
        related='product_id.categ_id',
        string='Product Category',
        store=True
    )

    @api.depends('line_ids.product_id')
    def _compute_main_product(self):
        for treatment in self:
            first_product = treatment.line_ids[:1].mapped('product_id')
            treatment.product_id = first_product.id if first_product else False
            treatment.product_categ_id = first_product.categ_id.id if first_product else False

    @api.depends('sale_order_id', 'picking_id', 'invoice_id')
    def _compute_counts(self):
        for rec in self:
            rec.sale_order_count = 1 if rec.sale_order_id else 0
            rec.delivery_count = 1 if rec.picking_id else 0
            rec.invoice_count = 1 if rec.invoice_id else 0

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

            if rec.appointment_id and rec.appointment_id.state != 'done':
                rec.appointment_id.action_done()
            # Create Sale Order if not exists
            if not rec.sale_order_id:
                order_vals = {
                    'partner_id': rec.patient_id.partner_id.id,
                    'pricelist_id': rec.pricelist_id.id,
                    'order_line': [(0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'price_unit': line.price,
                        'usage_note': line.usage_note,
                    }) for line in rec.line_ids],
                }
                sale_order = self.env['sale.order'].create(order_vals)
                sale_order.action_confirm()
                rec.sale_order_id = sale_order.id
                # Assign picking
                if sale_order.picking_ids:
                    rec.picking_id = sale_order.picking_ids[0].id

    def action_create_invoice(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError("Please confirm the treatment first.")
        if self.invoice_id:
            raise UserError("Invoice already created.")

        invoice = self.sale_order_id._create_invoices()
        self.invoice_id = invoice.id

        self.action_done()

        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_view_invoices(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError("No invoice found.")
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }

    def action_view_sale_orders(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError("No sale order found.")
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }

    def action_view_deliveries(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError("No delivery found.")
        return {
            'name': 'Delivery',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
        }

    def action_done(self):
        self.state = 'done'
        if self.appointment_id:
            self.appointment_id.action_done()

    def action_cancel(self):
        self.state = 'cancelled'

    def action_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('clinic.treatment') or 'New'
        return super().create(vals)

    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
            self.doctor_id = self.appointment_id.doctor_id
            self.date_start = self.appointment_id.date_start
            self.date_end = self.appointment_id.date_end
            self.room_id = self.appointment_id.room_id.id

    @api.onchange('treatment_product_id')
    def _onchange_treatment_product(self):
        if self.treatment_product_id:
            self.line_ids = [(5, 0, 0)]
            BoM = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', self.treatment_product_id.product_tmpl_id.id),
                ('type', 'in', ['phantom', 'normal']),
            ], limit=1)
            if BoM:
                lines = []
                for bom_line in BoM.bom_line_ids:
                    lines.append((0, 0, {
                        'product_id': bom_line.product_id.id,
                        'name': bom_line.product_id.name,
                        'product_uom_id': bom_line.product_uom_id.id,
                        'quantity': bom_line.product_qty,
                        'price': bom_line.product_id.list_price,
                        'usage_note': bom_line.usage_note,
                    }))
                self.line_ids = lines

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))


class ClinicTreatmentLine(models.Model):
    _name = 'clinic.treatment.line'
    _description = 'Treatment Line'

    category_id = fields.Many2one(related='product_id.categ_id', store=True, string='Category')
    treatment_id = fields.Many2one('clinic.treatment', string='Treatment', required=True, ondelete='cascade')
    name = fields.Char(string='Description')
    product_id = fields.Many2one('product.product', string='Treatment')

    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    quantity = fields.Float(string='Quantity', default=1.0)
    price = fields.Float(string='Price')
    usage_note = fields.Char(string="Description")
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id', store=True, readonly=False,
                                  required=True)

    @api.depends('treatment_id.currency_id')
    def _compute_currency_id(self):
        for line in self:
            line.currency_id = line.treatment_id.currency_id or self.env.company.currency_id

    subtotal = fields.Monetary(string='Amount', compute='_compute_subtotal', store=True, currency_field='currency_id')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.product_uom_id = self.product_id.uom_id
            self.price = self.product_id.list_price

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.price * line.quantity


