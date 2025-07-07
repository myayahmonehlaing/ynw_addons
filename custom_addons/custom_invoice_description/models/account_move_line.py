from odoo import models, fields, api
import re


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_clean_name(self):
        self.ensure_one()
        return re.sub(r'^\[.*?\]\s*', '', self.name or '')
