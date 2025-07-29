from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    usage_note = fields.Char(string="Usage Note")
