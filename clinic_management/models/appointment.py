from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz


class ClinicAppointment(models.Model):
    _name = 'clinic.appointment'
    _description = 'Clinic Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='Appointment', default='New', required=True, copy=False, readonly=True, tracking=True)
    patient_id = fields.Many2one('clinic.patient', string='Patient', store=True, required=True, tracking=True)
    reason = fields.Char(string='Reason for Visit', tracking=True)
    # doctor_id = fields.Many2one('hr.employee', string='Doctor', store=True, required=True,
    #                             domain="[('is_doctor_position', '=', True)]", tracking=True)
    allowed_doctor_ids = fields.Many2many(
        'hr.employee',
        compute="_compute_allowed_doctor_ids",
        string="Allowed Doctors"
    )

    doctor_id = fields.Many2one(
        'hr.employee',
        string='Doctor',
        domain="[('id', 'in', allowed_doctor_ids)]",
        store=True,
        required=True,
        tracking=True
    )

    # date = fields.Datetime(string='Appointment Date', required=True, tracking=True)
    date_start = fields.Datetime(string='Start Time', required=True, tracking=True)
    date_end = fields.Datetime(string='End Time', required=True, tracking=True)
    # Add at the top or near 'state'
    concern_type = fields.Selection([
        # ('dull_skin', 'Dull and Tired-Looking Skin'),
        ('dehydrated_skin', 'Dehydrated Skin'),
        # ('mild_acne', 'Mild Acne'),
        ('severe_acne', 'Severe Acne'),
        ('acne_scars', 'Acne Scars'),
        # ('pigmentation', 'Pigmentation / Melasma'),
        # ('uneven_skin', 'Uneven Skin Tone'),
        ('wrinkles', 'Wrinkles and Fine Lines'),
        ('large_pores', 'Large Pores'),
        ('oily_skin', 'Oily Skin'),
        ('sensitive_skin', 'Sensitive Skin'),
        ('dark_spots', 'Dark Spots / Age Spots'),
        ('redness', 'Skin Redness / Rosacea'),
        ('dry_skin', 'Dry and Flaky Skin'),
        # ('laser_hair_removal', 'Laser Hair Removal'),
        ('stretch_marks', 'Stretch Marks'),
        # ('tattoo_removal', 'Tattoo Removal'),
        # ('tightening', 'Skin Tightening'),
        ('detox', 'Detox & Skin Congestion'),
        # ('maintenance', 'Monthly Facial Maintenance'),
    ], string='Concern Type', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('consulted', 'Consulted'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    room_id = fields.Many2one('clinic.room', string="Room", tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', store=True,
                                  tracking=True)

    @api.depends('concern_type')
    def _compute_allowed_doctor_ids(self):
        concern_to_doctor_type = {
            'dehydrated_skin': 'Aesthetic Doctor',
            'severe_acne': 'Cosmetic Dermatologist',
            'acne_scars': 'Laser Specialist Doctor',
            'wrinkles': 'Cosmetic Dermatologist',
            'large_pores': 'Laser Specialist Doctor',
            'oily_skin': 'General Dermatologist',
            'sensitive_skin': 'Aesthetic Doctor',
            'dark_spots': 'Cosmetic Dermatologist',
            'redness': 'General Dermatologist',
            'dry_skin': 'Aesthetic Doctor',
            'stretch_marks': 'Laser Specialist Doctor',
            'detox': 'General Dermatologist',
        }

        for rec in self:
            domain = [('is_doctor_position', '=', True)]
            if rec.concern_type:
                target_type = concern_to_doctor_type.get(rec.concern_type)
                if target_type:
                    domain.append(('doctor_type.name', '=', target_type))
            rec.allowed_doctor_ids = self.env['hr.employee'].search(domain)

    @api.constrains('room_id', 'date_start', 'date_end')
    def _check_room_availability(self):
        for rec in self:
            if not rec.room_id:
                continue
            overlapping = self.search([
                ('id', '!=', rec.id),
                ('room_id', '=', rec.room_id.id),
                ('state', 'in', ['confirmed', 'consulted']),
                ('date_start', '<', rec.date_end),
                ('date_end', '>', rec.date_start)
            ])
            if overlapping:
                raise ValidationError("⛔ This room is already occupied during the selected time.")

    def _to_user_tz(self, dt):
        """Convert UTC datetime to user's timezone."""
        user_tz = self.env.context.get('tz') or 'UTC'
        local_tz = pytz.timezone(user_tz)
        return pytz.utc.localize(dt).astimezone(local_tz).strftime('%Y-%m-%d %H:%M')

    @api.constrains('doctor_id', 'date_start', 'date_end', 'state')
    def _check_doctor_availability(self):
        for appointment in self:
            if appointment.state not in ('confirmed', 'consulted'):
                continue

            overlaps = self.search([
                ('id', '!=', appointment.id),
                ('doctor_id', '=', appointment.doctor_id.id),
                ('state', 'in', ('confirmed', 'consulted')),
                ('date_start', '<', appointment.date_end),
                ('date_end', '>', appointment.date_start),
            ])
            if overlaps:
                conflict = overlaps[0]
                start_local = self._to_user_tz(conflict.date_start)
                end_local = self._to_user_tz(conflict.date_end)
                raise UserError(_(
                    "⛔ Doctor '%s' already has a confirmed or consulted appointment:\n\n"
                    "🕒 %s ➡ %s \n\n"
                    "✅ Please schedule after %s."
                ) % (
                                    conflict.doctor_id.name,
                                    start_local,
                                    end_local,
                                    end_local,
                                ))

    def _set_room_occupied(self, occupied):
        for appointment in self:
            if appointment.room_id:
                appointment.room_id.is_occupied = occupied

    def action_confirm(self):
        for appointment in self:
            appointment._check_doctor_availability()
            appointment._check_room_availability()
            appointment._set_room_occupied(True)
            appointment.state = 'confirmed'

    def action_consult(self):
        for appointment in self:
            appointment._set_room_occupied(True)
            appointment.state = 'consulted'

    def action_done(self):
        for appointment in self:
            appointment._set_room_occupied(False)
            appointment.state = 'done'

    def action_cancel(self):
        for appointment in self:
            appointment._set_room_occupied(False)
            appointment.state = 'cancelled'

    def action_draft(self):
        for appointment in self:
            appointment._set_room_occupied(False)
            appointment.state = 'draft'

    def action_create_treatment(self):
        return {
            'name': 'Create Treatment',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.treatment',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_appointment_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                # Add more default fields if needed
            }
        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('clinic.appointment') or 'New'
        return super().create(vals)

    room_id = fields.Many2one('clinic.room', string='Room', domain="[('is_occupied', '=', False)]")
    # prescription_id = fields.Many2one('clinic.prescription', string='Prescription')
    # treatment_id = fields.Many2one('clinic.treatment', string='Treatment')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        # These context keys come from calendar click
        date_start = self.env.context.get('default_date_start')
        date_end = self.env.context.get('default_date_end')

        if date_start:
            res['date_start'] = date_start
        if date_end:
            res['date_end'] = date_end

        return res
