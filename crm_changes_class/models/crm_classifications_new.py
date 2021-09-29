from odoo import api, fields, models

COMPANY_SELECTION = [
    ('ceo', 'CEO'),
    ('manager', 'Manager'),
    ('employee', 'Employee'),
    ('other', 'Others')
]
COMMUNITY_SELECTION = [
    ('leader', 'Leader'),
    ('vice', 'Vice Leader'),
    ('member', 'member'),
    ('speaker', 'Speaker'),
    ('other', 'Others')
]
SCHOOL_SELECTION = [
    ('head', 'Headmaster'),
    ('teacher', 'Teacher'),
    ('council', 'Student Council'),
    ('student', 'Student'),
    ('other', 'Others')
]
COLLAGE_SELECTION = [
    ('rector', 'Rector'),
    ('lecture', 'Lecturer'),
    ('student', 'Collage Student'),
    ('other', 'Others')
]


class ExampleCode(models.Model):
    _name = 'example.code'
    event_list = fields.Selection(string='Event Type', selection=[
        ('company', 'Company Event'),
        ('commu', 'Community Event'),
        ('school', 'School Event'),
        ('collage', 'Collage Event')
    ])

    position_company = fields.Selection(string='Company Position', selection=COMPANY_SELECTION)
    position_community = fields.Selection(string='Company Position', selection=COMMUNITY_SELECTION)
    position_school = fields.Selection(string='Company Position', selection=SCHOOL_SELECTION)
    position_collage = fields.Selection(string='Company Position', selection=COLLAGE_SELECTION)
    position = fields.Selection(string="Position",
                                selection=COMPANY_SELECTION + COMMUNITY_SELECTION + SCHOOL_SELECTION + COLLAGE_SELECTION,
                                compute='_compute_position', store=True)

    @api.depends('position', 'position_company', 'position_community', 'position_school', 'position_collage')
    def _compute_position(self):
        for rec in self:
            if rec.event_list == 'company':
                rec.position = rec.position_company
            elif rec.event_list == 'commu':
                rec.position = rec.position_community
            elif rec.event_list == 'school':
                rec.position = rec.position_school
            elif rec.event_list == 'collage':
                rec.position = rec.position_collage
            else:
                rec.position = False

# field = expected_revenue
# model = crm.lead

# model = crm.lead2opportunity.partner
# crm.lead2opportunity.partner.mass
# field = disable crate a new customer
#5668989
# model = mail.activity
# field = field.note('mail.activity.note', 'Note')