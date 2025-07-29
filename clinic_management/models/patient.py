from odoo import models, fields, api


class ClinicPatient(models.Model):
    _name = 'clinic.patient'
    _description = 'Clinic Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}

    _rec_name = 'name'
    name = fields.Char(string='Name', required=True, tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', tracking=True)
    dob = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Text(string='Address', tracking=True)
    blood_type = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'), ('o+', 'O+'), ('o-', 'O-')
    ], string='Blood Type', tracking=True)
    image = fields.Binary(string='Image')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, tracking=True)
    skin_type = fields.Selection([
        ('oily', 'Oily'),
        ('dry', 'Dry'),
        ('combination', 'Combination'),
        ('normal', 'Normal'),
        ('sensitive', 'Sensitive')
    ], string="Skin Type", tracking=True)
    allergies = fields.Text(string='Allergies', tracking=True)
    treatment_ids = fields.One2many(
        'clinic.treatment',
        'patient_id',
        string='Previous Treatments', tracking=True
    )
    appointment_ids = fields.One2many(
        'clinic.appointment',
        'patient_id',
        string='Appointments'
    )
    treatment_count = fields.Integer(string="Treatments", compute="_compute_counts")
    appointment_count = fields.Integer(string="Appointments", compute="_compute_counts")

    @api.depends('treatment_ids', 'appointment_ids')
    def _compute_counts(self):
        for rec in self:
            rec.treatment_count = len(rec.treatment_ids)
            rec.appointment_count = len(rec.appointment_ids)

    @api.model
    def create(self, vals):
        image_data = vals.get('image')
        partner = self.env['res.partner'].create({
            'name': vals.get('name'),
            'phone': vals.get('phone'),
            'email': vals.get('email'),
            'image_1920': image_data if image_data else False,
        })
        vals['partner_id'] = partner.id
        return super().create(vals)

    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                today = fields.Date.today()
                rec.age = today.year - rec.dob.year - ((today.month, today.day) < (rec.dob.month, rec.dob.day))
            else:
                rec.age = 0

    def action_create_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Appointment',
            'res_model': 'clinic.appointment',
            'view_mode': 'calendar,list,form',
            'target': 'current',
            'context': {
                'default_patient_id': self.id,
            }
        }

    def action_view_treatments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Treatments',
            'res_model': 'clinic.treatment',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
        }

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'clinic.appointment',
            'view_mode': 'calendar,list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
        }
