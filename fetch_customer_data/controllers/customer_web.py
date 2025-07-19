from odoo import http
from odoo.http import request

class CustomerWeb(http.Controller):

    @http.route('/customer/view', type='http', auth='user', website=True)
    def customer_view(self, **kw):
        partners = request.env['res.partner'].sudo().search([('customer_rank', '>', 0)])
        customers = [{
            'id': p.id,
            'name': p.name,
            'email': p.email,
            'phone': p.phone,
            'image': f"data:image/png;base64,{p.image_128.decode()}" if p.image_128 else False,
        } for p in partners]

        return request.render('fetch_customer_data.customer_template', {
            'customers': customers
        })
