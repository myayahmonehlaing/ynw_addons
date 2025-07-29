from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    usage_note = fields.Char(string="Description")

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res['usage_note'] = self.usage_note  # keep the note in invoice line
        return res
