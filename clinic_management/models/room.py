from odoo import models, fields

class ClinicRoom(models.Model):
    _name = 'clinic.room'
    _description = 'Clinic Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Room Number', required=True, tracking=True)
    type = fields.Selection([
        ('general', 'General'),
        ('laser', 'Laser'),
    ], string='Room Type',tracking=True)
    is_occupied = fields.Boolean(string='Is Occupied')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)