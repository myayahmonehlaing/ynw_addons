from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, time


class ConsignmentReportWizard(models.TransientModel):
    _name = 'consignment.report.wizard'
    _description = 'Consignment Report Wizard'

    order_date = fields.Date(string='Order Date', required=True, default=fields.Date.context_today)

    def action_export_excel(self):
        url = '/consignment/report/xlsx?order_date=%s' % self.order_date
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    def action_export_pdf(self):
        if not self.order_date:
            raise UserError("Please select a date.")

        data = {
            'order_date': self.order_date.strftime('%Y-%m-%d'),
        }

        return self.env.ref('custom_consignment_form.action_report_consignment_pdf').report_action(self, data=data)

    def action_open_pivot(self):
        if not self.order_date:
            raise UserError("Please select a date.")
        self.env['consignment.order.line'].search([]).write({'filter_date': self.order_date})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.order.line',
            'name': 'Consignment Pivot',
            'view_mode': 'pivot',
            'target': 'current',
            'context': {
                'search_default_groupby_product_id': 1,
                'search_default_groupby_partner_id': 1,
            },
        }
