from odoo import models, fields, api


class ClinicDoctorType(models.Model):
    _name = 'clinic.doctor.type'
    _description = 'Doctor Type'

    name = fields.Char(string='Name', required=True)
    treatment_product_ids = fields.Many2many(
        'product.product',
        string='Treatments Best Handled',
        domain=[('has_phantom_bom', '=', True)]
    )


class ClinicDoctor(models.Model):
    _inherit = 'hr.employee'

    doctor_type = fields.Many2one(
        'clinic.doctor.type',
        string='Doctor Type'
    )

    is_doctor_position = fields.Boolean(
        string="Is Doctor Job",
        compute="_compute_is_doctor_position",
        store=True  # ✅ This line is the fix
    )

    @api.depends('job_id.name')
    def _compute_is_doctor_position(self):
        for rec in self:
            rec.is_doctor_position = (rec.job_id.name == "Doctor") if rec.job_id else False
