#coding: utf-8

from odoo import _, fields, models


class crm_check_list(models.Model):
    _inherit = 'crm.check.list'

    description = fields.Char('Descripción', default="")
    days_to_complete = fields.Integer('Días para completar', default=0)