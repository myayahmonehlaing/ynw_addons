from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    bom_count = fields.Integer(
        string='BoM Count',
        compute='_compute_bom_count',
        store=True
    )

    has_phantom_bom = fields.Boolean(
        string='Has Phantom BoM',
        compute='_compute_has_phantom_bom',
        store=True,
        help="True if product has a phantom (kit) BoM"
    )

    @api.depends('product_tmpl_id')
    def _compute_bom_count(self):
        for product in self:
            product.bom_count = self.env['mrp.bom'].search_count([
                ('product_tmpl_id', '=', product.product_tmpl_id.id)
            ])

    @api.depends('bom_ids.type')
    def _compute_has_phantom_bom(self):
        for product in self:
            product.has_phantom_bom = any(bom.type == 'phantom' for bom in product.bom_ids)
