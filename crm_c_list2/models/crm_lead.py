# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    custom_task_ids = fields.One2many('project.task', 'custom_crm_lead_id')

    def action_view_task(self):
        action = self.env.ref('project.action_view_task').sudo().read()[0]
        action['domain'] = [('custom_crm_lead_id', 'in', self.ids)]
        return action

    @api.model
    def create(self, vals):
        """
            Al crear una nueva oportunidad genera la lista de tareas a realizar
            en función de la configuración de la oportunidad inicial
        """
        res = super(CrmLead, self).create(vals)
        clist = self.env['crm.check.list'].sudo().search([('crm_stage_st_id', '=', res.stage_id.id)], order='sequence desc')
        for check in clist:
            data = {
                'company_id': res.company_id.id,
                'name': check.name,
                'user_id': res.user_id.id,
                'date_deadline': fields.Datetime.now() + timedelta(days=check.days_to_complete),
                'partner_id': res.partner_id.id,
                'description': check.description,
                'date_assign': fields.date.today(),
                'custom_crm_lead_id': res.id,
                'stage_id': False,
                'project_privacy_visibility': 'portal',
                'allowed_user_ids': [(6, 0, [res.user_id.id])],
            }
            self.env['project.task'].sudo().create(data)
        return res

    @api.onchange('stage_id')
    def on_change_stage(self):
        """
            Al cambiar de etapa una oportunidad, se le genera una lista de tareas a realizar
            en función de la configuración de la etapa a la que pasa. Se filtran las tareas
            ya existentes y en estado 'en proceso' para que no se vuelvan a generar
        """
        tasks = self.env['project.task'].sudo().search([('custom_crm_lead_id', '=', self._origin.id), ('kanban_state', '=', 'normal')]).mapped('name')
        clist = self.env['crm.check.list'].sudo().search([('crm_stage_st_id', '=', self.stage_id.id)], order='sequence desc')
        history = self.check_list_history_ids.filtered(lambda x: x.check_list_id.id in clist.ids).mapped('check_list_id.name')
        for check in clist:
            if check.name not in tasks and (check.name not in history or check.should_be_reset):
                self.env['project.task'].sudo().create({
                    'company_id': self.company_id.id,
                    'name': check.name,
                    'user_id': self.user_id.id,
                    'date_deadline': fields.Datetime.now() + timedelta(days=check.days_to_complete),
                    'partner_id': self.partner_id.id,
                    'description': check.description,
                    'date_assign': fields.date.today(), 
                    'custom_crm_lead_id': self._origin.id,
                    'project_privacy_visibility': 'portal',
                    'allowed_user_ids': [(6, 0, [self.user_id.id])],
                })
