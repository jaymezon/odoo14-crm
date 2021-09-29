# -*- coding: utf-8 -*-

from odoo import models, fields, api


# TODO: este modelo corrige funcionalidad de un wizard
# sería ideal que esté dentro del directorio 'wizards'
class CrmLeadTaskWizard(models.TransientModel):
    _inherit = 'crm.lead.task.wizard'

    project_id = fields.Many2one(required=False)

    def create_task(self):
        """
            Corrige un error del módulo 'crm_opportunity_task', la tarea creada no
            daba permisos de visualización a los usuarios normales ni al usuario que crea.
            Estas no se mostraban en la pantalla de tareas
        """
        task_object = self.env['project.task']
        lead_id = self.env['crm.lead'].browse(
            self.env.context.get('active_id'))
        for rec in self:
            task_vals = {
                'project_id': rec.project_id.id,
                'company_id': rec.company_id.id,
                'name': rec.name,
                'user_id': rec.user_id.id,
                'date_deadline': rec.date_deadline,
                'tag_ids': [(6, 0, rec.tag_ids.ids)],
                'partner_id': rec.partner_id.id,
                'description': rec.description,
                'date_assign': rec.date_assign,
                'stage_id': False,
                'project_privacy_visibility': 'portal',
                'allowed_user_ids': [(6, 0, [rec.user_id.id])],
            }
            task_id = task_object.create(task_vals)
            task_id.custom_crm_lead_id = lead_id.id
            lead_id.custom_task_ids = [(4, t.id) for t in task_id]
        return lead_id.action_view_task()