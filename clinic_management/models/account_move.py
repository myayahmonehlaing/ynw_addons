from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    treatment_id = fields.Many2one('clinic.treatment', string='Treatment')
