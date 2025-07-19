from odoo import http
from odoo.http import request

class CustomerAPIController(http.Controller):

    @http.route('/api/customers', type='json', auth='none', csrf=False, methods=['POST'])
    def get_customers(self, **kwargs):
        token = request.httprequest.headers.get('Authorization')
        valid_token = request.env['ir.config_parameter'].sudo().get_param('customer_api.token')

        if token != f"Bearer {valid_token}":
            return {
                'error': 'Unauthorized',
                'status': 401
            }

        partners = request.env['res.partner'].sudo().search([('customer_rank', '>', 0)])
        customers = [{
            'id': p.id,
            'name': p.name,
            'email': p.email,
            'phone': p.phone,
            'image': f"data:image/png;base64,{p.image_128.decode()}" if p.image_128 else False,
        } for p in partners]

        return {
            'status': 200,
            'data': customers
        }
