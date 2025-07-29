from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    usage_note = fields.Char(string="Description")
