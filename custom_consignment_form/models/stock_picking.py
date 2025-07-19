from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    origin_consignment_id = fields.Many2one('consignment.order', string='Consignment Order')

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.origin_consignment_id:
                picking.origin_consignment_id.state = 'done'
        return res


