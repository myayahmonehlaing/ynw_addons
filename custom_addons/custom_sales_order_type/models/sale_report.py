from odoo import models, fields

class SaleReport(models.Model):
    _inherit = 'sale.report'

    order_type_id = fields.Many2one('sale.order.type', string='Order Type', readonly=True)

    def _select_sale(self):
        select_ = super()._select_sale()
        select_ += ", s.order_type_id AS order_type_id"
        return select_

    def _group_by_sale(self):
        group_by = super()._group_by_sale()
        group_by += ", s.order_type_id"
        return group_by
