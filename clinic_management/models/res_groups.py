from odoo import models, fields

class ResGroups(models.Model):
    _inherit = 'res.groups'

    sequence = fields.Integer(string="Sequence", default=10)
