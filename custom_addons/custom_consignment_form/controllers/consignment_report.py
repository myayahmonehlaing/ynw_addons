from datetime import datetime, time
from odoo import http
from odoo.http import request
import io
import xlsxwriter


class ConsignmentReportController(http.Controller):

    @http.route('/consignment/report/xlsx', type='http', auth='user')
    def export_xlsx(self, **kwargs):
        date_str = kwargs.get('order_date')
        if not date_str:
            return request.not_found()

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        end = datetime.combine(date_obj, time.max)

        orders = request.env['consignment.order'].search([
            ('date_order', '<=', end),
        ])

        product_customer_qty = {}
        customer_names = set()

        for order in orders:
            customer = order.partner_id.name
            customer_names.add(customer)
            for line in order.order_line_ids:
                product = line.product_id.name
                if product not in product_customer_qty:
                    product_customer_qty[product] = {}
                remaining = line.remaining_qty_at_date(date_str)
                product_customer_qty[product][customer] = (
                    product_customer_qty[product].get(customer, 0.0) + remaining
                )

        sorted_customers = sorted(customer_names)
        sorted_products = sorted(product_customer_qty.keys())

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Consignment Report")


        sheet.write(0, 1, date_obj.strftime('%m/%d/%Y'))


        sheet.write(1, 0, 'Product')
        for col, cust in enumerate(sorted_customers, start=1):
            sheet.write(1, col, cust)

        row = 2
        for product in sorted_products:
            sheet.write(row, 0, product)
            for col, cust in enumerate(sorted_customers, start=1):
                qty = product_customer_qty[product].get(cust, 0.0)
                sheet.write(row, col, qty)
            row += 1

        workbook.close()
        output.seek(0)
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=consignment_report_%s.xlsx' % date_str)
            ]
        )
