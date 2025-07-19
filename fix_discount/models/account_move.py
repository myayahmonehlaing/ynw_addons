from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fixdis = fields.Float(string="FixDis", digits='Product Price')
