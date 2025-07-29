from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    clinic_access_level = fields.Selection(
        selection=lambda self: [
            ('accountant', 'Clinic Accountant'),
            ('pharmacist', 'Clinic Pharmacist'),
            ('receptionist', 'Clinic Receptionist'),
            ('doctor', 'Clinic Doctor'),
            ('manager', 'Clinic Manager'),
        ],
        string='Clinic Access Level'
    )

    @api.model
    def create(self, vals):
        user = super().create(vals)
        user._update_clinic_groups()
        return user

    def write(self, vals):
        res = super().write(vals)
        if 'clinic_access_level' in vals:
            self._update_clinic_groups()
        return res

    def _update_clinic_groups(self):
        self.ensure_one()
        group_map = {
            'accountant': 'clinic_management.group_clinic_accountant',
            'pharmacist': 'clinic_management.group_clinic_pharmacist',
            'receptionist': 'clinic_management.group_clinic_receptionist',
            'doctor': 'clinic_management.group_clinic_doctor',
            'manager': 'clinic_management.group_clinic_manager',
        }

        group_ids = [
            self.env.ref(xml_id).id for xml_id in group_map.values()
        ]
        clinic_groups = self.env['res.groups'].browse(group_ids)
        self.groups_id -= clinic_groups

        if self.clinic_access_level:
            group_id = self.env.ref(group_map[self.clinic_access_level])
            self.groups_id += group_id
