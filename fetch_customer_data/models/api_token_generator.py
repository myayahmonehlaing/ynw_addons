from odoo import models, api
import secrets


class APITokenAutoCreate(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _register_hook(self):
        param = self.env['ir.config_parameter'].sudo()
        if not param.get_param('customer_api.token'):
            token = secrets.token_hex(16)
            param.set_param('customer_api.token', token)
