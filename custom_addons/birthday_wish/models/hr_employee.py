from odoo import models, fields, api
from datetime import datetime


class Employee(models.Model):
    _inherit = 'hr.employee'

    def check_and_notify_birthdays(self):
        today = datetime.today().strftime('%m-%d')
        birthday_employees = self.search([])

        for emp in birthday_employees:
            if emp.birthday and emp.birthday.strftime('%m-%d') == today:
                # Create activity for birthday employee
                if emp.user_id:
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get_id('hr.employee'),
                        'res_id': emp.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': '🎉 Happy Birthday!',
                        'note': 'It\'s your birthday today! Enjoy your special day!',
                        'user_id': emp.user_id.id,
                        'date_deadline': fields.Date.today(),
                    })

                # Post message in chatter visible to others
                followers = self.search([('id', '!=', emp.id)])
                for f in followers:
                    if f.user_id:
                        emp.message_post(
                            body=f"🎂 Today is {emp.name}'s birthday! Wish them a Happy Birthday! 🎈",
                            message_type='notification',
                            subtype_xmlid='mail.mt_note',
                            partner_ids=[f.user_id.partner_id.id],
                        )
