from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_verified = fields.Boolean(string="Verified")
