from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    bom_count = fields.Integer(
        string='BoM Count',
        compute='_compute_bom_count',
        store=True
    )

    @api.depends()
    def _compute_bom_count(self):
        for product in self:
            product.bom_count = self.env['mrp.bom'].search_count([
                ('product_tmpl_id', '=', product.product_tmpl_id.id)
            ])

