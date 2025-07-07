from odoo import models,fields


class StandardCV(models.Model):
    _name="standard.cv"
    _description="Standard CV"
    _table="standard_cv"

    name=fields.Char(string="Career Name",required=True)

    image = fields.Binary(string="Career Image")
    apply_job = fields.Char(string="Apply Job")
    salary = fields.Integer(string="Expect Salary")
    dob = fields.Date(string="Date of Birth")
    nrc = fields.Char(string="NRC")
    nationality = fields.Char(string="Nationality")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Char(string="Address")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    marital = fields.Selection([('single', 'Single'), ('married', 'Married')], string="Marital Status")
    objective = fields.Text(string="Career Objectives")
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)