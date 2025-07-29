from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_treatment_product = fields.Boolean(string='Is Treatment Product')
