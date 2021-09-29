# -*- coding: utf-8 -*-
{
    "name": "CRM Check List - Task Connector",
    "version": "1.0",
    "category": "Sales",
    "author": "Mobilize (JLQC)",    
    "application": True,
    "installable": True,
    "depends": [ "crm", "project", "crm_checklist", "crm_opportunity_task" ],
    "data": [        
        "views/crm_check_list.xml",
        "views/crm_lead_task_wizard_view.xml",
        "views/crm_lead.xml",
        "views/crm_stage.xml",
        "views/project_task.xml",
    ],
    "summary": "Connecta los módulos 'crm_checklist' y 'crm_opportunity_task'",
    "description": """
        Connecta los módulos 'crm_checklist' y 'crm_opportunity_task'
    """
}