from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    consignment_warehouse_id = fields.Many2one(
        related='company_id.consignment_warehouse_id',
        string='Consignment Warehouse',
        readonly=False
    )
