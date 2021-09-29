# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.onchange('kanban_state')
    def on_change_kanban_state(self):
        """
            Cuando una tarea se marca como 'realizada', la tarea en la oportunidad se marca automáticamente.
            Las busca por nombre por lo que si el nombre de la tarea cambia, esta no se marcará. De igual
            forma si la tarea se marca como 'en proceso' o 'bloqueda' está se desmarcará de la lista
        """
        for rec in self:
            if rec.custom_crm_lead_id:
                if rec.kanban_state == 'done':
                    clist = self.env['crm.check.list'].search([('crm_stage_st_id', '=', rec.custom_crm_lead_id.stage_id.id), ('name', '=', rec.name)])
                    rec.custom_crm_lead_id.write({'check_list_line_ids': [(6, 0, rec.custom_crm_lead_id.check_list_line_ids.ids + clist.ids)]})
                if rec.kanban_state in ['normal', 'blocked']:
                    clist = self.env['crm.check.list'].search([('crm_stage_st_id', '=', rec.custom_crm_lead_id.stage_id.id), ('name', '=', rec.name)])
                    rec.custom_crm_lead_id.write({'check_list_line_ids': [(6, 0, [i for i in rec.custom_crm_lead_id.check_list_line_ids.ids if i not in clist.ids])]})
