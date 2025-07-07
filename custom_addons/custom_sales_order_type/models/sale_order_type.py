from odoo import models, fields


class SaleOrderType(models.Model):
    _name = 'sale.order.type'
    _description = 'Sale Order Type'

    name = fields.Char(string='Order Type', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Order Sequence')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    journal_id = fields.Many2one('account.journal', string='Sales Journal')
