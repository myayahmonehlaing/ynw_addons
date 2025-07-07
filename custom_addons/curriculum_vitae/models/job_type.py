from odoo import models,fields

class JobType(models.Model):
    _name="job.type"
    _description="Job Type"
    _table="job_type"

    name=fields.Char(string="Job Type", required=True)
    description=fields.Text(string="Description")
