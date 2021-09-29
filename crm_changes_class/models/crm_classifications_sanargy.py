from odoo import _, api, fields, models


# class CrmLead2opportunityPartner(models.TransientModel):
#     _inherit = "crm.lead2opportunity.partner"
# model = crm.lead2opportunity.partner
# crm.lead2opportunity.partner.mass
#     warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse',related='product_tmpl_id.warehouse_ids', store=True)

# class CrmLead2opportunityPartner(models.TransientModel):
#     _inherit = "crm.lead2opportunity.partner"
#
#     action = fields.Selection(selection=[
#         # ('create', 'Create a new customer'),
#         ('exist', 'Link to an existing customer'),
#         ('nothing', 'Do not link to a customer')
#     ], string='Actions', store=True, default='', required=True, readonly=False)


class CrmStage(models.Model):
    _inherit = "crm.stage"

    channels = fields.Char(string='Channels')


class CrmClassification(models.Model):
    _inherit = "crm.lead"
    _rec_name = 'channels'

    target_volume = fields.Integer(string='Target Volume', store=True)
    # expected_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True)

    @api.depends('target_volume', 'probability')
    def _compute_prorated_revenue(self):
        for lead in self:
            lead.prorated_revenue = round((lead.target_volume or 0.0) * (lead.probability or 0) / 100.0, 2)

    def _get_rainbowman_message(self):
        message = False
        if self.user_id and self.team_id and self.target_volume:
            self.flush()  # flush fields to make sure DB is up to date
            query = """
                SELECT
                    SUM(CASE WHEN user_id = %(user_id)s THEN 1 ELSE 0 END) as total_won,
                    MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND user_id = %(user_id)s THEN target_volume ELSE 0 END) as max_user_30,
                    MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND user_id = %(user_id)s THEN target_volume ELSE 0 END) as max_user_7,
                    MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND team_id = %(team_id)s THEN target_volume ELSE 0 END) as max_team_30,
                    MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND team_id = %(team_id)s THEN target_volume ELSE 0 END) as max_team_7
                FROM crm_lead
                WHERE
                    type = 'opportunity'
                AND
                    active = True
                AND
                    probability = 100
                AND
                    DATE_TRUNC('year', date_closed) = DATE_TRUNC('year', CURRENT_DATE)
                AND
                    (user_id = %(user_id)s OR team_id = %(team_id)s)
            """
            self.env.cr.execute(query, {'user_id': self.user_id.id,
                                        'team_id': self.team_id.id})
            query_result = self.env.cr.dictfetchone()

            if query_result['total_won'] == 1:
                message = _('Go, go, go! Congrats for your first deal.')
            elif query_result['max_team_30'] == self.target_volume:
                message = _('Boom! Team record for the past 30 days.')
            elif query_result['max_team_7'] == self.target_volume:
                message = _('Yeah! Deal of the last 7 days for the team.')
            elif query_result['max_user_30'] == self.target_volume:
                message = _('You just beat your personal record for the past 30 days.')
            elif query_result['max_user_7'] == self.target_volume:
                message = _('You just beat your personal record for the past 7 days.')
        return message

    channels = fields.Many2one(
        'crm.stage', string='Channels', index=True, tracking=True, store=True,
        copy=False, ondelete='restrict',
        domain="['|', ('channels', '=', 'channels'), ('team_id', '=', team_id)]")

    # expected_revenue = fields.Char(string='Target Volume', store=True)
    gps_location = fields.Char(string="GPS Location", store=True)
    classifications = fields.Many2one("crm.tag", string='Tones Classification', store=True)  # "crm.tag" 5668989 inoro
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'female'),
        ('corporate', 'corporate'),
        ('other', 'other')
    ], string='Gender', store=True, default='', readonly=False)
    regions = fields.Selection(selection=[
        ('east_territory', 'East Territory'),
        ('west_territory', 'West Territory')
    ], string='Regions', store=True, default='', required=True, readonly=False)
    east_subterritory_embu_tharaka = fields.Selection([
        ('embu', 'Embu'),
        ('gachuriri', 'Gachuriri'),
        ('gikuru', 'Gikuru'),
        ('gitaru', 'Gitaru'),
        ('ishiara', 'Ishiara'),
        ('kanyuambora', 'Kanyuambora'),
        ('karaba', 'Karaba'),
        ('karurumo', 'Karurumo'),
        ('kathangariri', 'Kathangariri'),
        ('kiritiri', 'Kiritiri'),
        ('makima', 'Makima'),
        ('makutano', 'Makutano'),
        ('mbondoni', 'Mbondoni'),
        ('muraru', 'Muraru'),
        ('mutuobare', 'Mutuobare'),
        ('mwanyani', 'Mwanyani'),
        ('nthingini', 'Nthingini'),
        ('nthingini', 'Nthingini'),
        ('runyenjes', 'Runyenjes'),
        ('tharaka', 'Tharaka'),
        ('ugweri', 'Ugweri')
    ], string='Embu - Tharaka, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_kiambu_muranga = fields.Selection([
        ('juja', 'Juja'),
        ('kiambu', 'Kiambu Town'),
        ('muranga', 'Muranga'),
        ('nairobi', 'Nairobi'),
        ('ngoliba', 'Ngoliba'),
        ('ruiru', 'Ruiru'),
        ('soko', 'Soko Mjinga'),
        ('thika', 'Thika')
    ], string='Kiambu - Muranga, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_kilifi_malindi = fields.Selection([
        ('bamba', 'Bamba'),
        ('garsen', 'Garsen'),
        ('kaloleni', 'Kaloleni'),
        ('kilifi', 'Kilifi'),
        ('malindi', 'Malindi'),
        ('mpeketoni', 'Mpeketoni'),
        ('mtwapa', 'Mtwapa')
    ], string='Kilifi - Malindi, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_kirinyagab_muranga = fields.Selection([
        ('kagio', 'Kagio'),
        ('kamuchege', 'Kamuchege'),
        ('kandongu', 'Kandongu'),
        ('karii', 'Karii'),
        ('kasseveni', 'Kasseveni'),
        ('kenol', 'Kenol'),
        ('kiamuciri', 'Kiamuciri'),
        ('kiburu', 'Kiburu'),
        ('kimbimbi', 'Kimbimbi'),
        ('kimicha', 'Kimicha'),
        ('kiriko', 'Kiriko'),
        ('kutus', 'Kutus'),
        ('mahiga', 'Mahiga - Ini'),
        ('mukuyu', 'Mukuyu'),
        ('mururi', 'Mururi'),
        ('mutithi', 'Mutithi'),
        ('mwea', 'Mwea'),
        ('ngariama', 'Ngariama'),
        ('sagana', 'Sagana'),
        ('wanguru', 'Wanguru')
    ], string='Kirinyagab- Muranga, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_machakos = fields.Selection([
        ('ekalakala', 'Ekalakala'),
        ('kabaa', 'Kabaa'),
        ('kaewa', 'Kaewa'),
        ('kakuyuni', 'Kakuyuni'),
        ('kithimani', 'Kithimani'),
        ('kithyoko', 'Kithyoko'),
        ('machakos', 'Machakos'),
        ('machakos', 'Machakos'),
        ('masii', 'Masii'),
        ('masinga', 'Masinga'),
        ('matuu', 'Matuu'),
        ('sofia', 'Sofia'),
        ('wamunyu', 'Wamunyu')
    ], string='Machakos, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_nyeri = fields.Selection([
        ('endarasha', 'Endarasha'),
        ('kanyagia', 'Kanyagia'),
        ('karatina', 'Karatina'),
        ('kiawara', 'Kiawara'),
        ('mukurweini', 'Mukurweini'),
        ('munyu', 'Munyu'),
        ('mweiga', 'Mweiga'),
        ('narumoru', 'Narumoru'),
        ('nyeri', 'Nyeri')
    ], string='Nyeri, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_oloitoktok_emali = fields.Selection([
        ('challa', 'Challa'),
        ('emali', 'Emali'),
        ('entarara', 'Entarara'),
        ('illasit', 'Illasit'),
        ('isinet', 'Isinet'),
        ('kibwezi', 'Kibwezi'),
        ('kimama', 'Kimama'),
        ('makindu', 'Makindu'),
        ('mashuuru', 'Mashuuru'),
        ('masimba', 'Masimba'),
        ('namelok', 'Namelok'),
        ('njukini', 'Njukini'),
        ('oloitoktok', 'Oloitoktok'),
        ('out_of_territory_sinya', 'Out of territory - Isinya'),
        ('rombo', 'Rombo'),
        ('selengei', 'Selengei'),
        ('taveta', 'Taveta'),
        ('wundanyi', 'Wundanyi')
    ], string='Oloitoktok - Emali, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_laikipia = fields.Selection([
        ('karandi', 'Karandi'),
        ('kiamariga', 'Kiamariga'),
        ('kinamba', 'Kinamba'),
        ('muhotetu', 'Muhotetu'),
        ('nanyuki', 'Nanyuki'),
        ('narumoru', 'Narumoru'),
        ('out_of_territory_isiolo', 'Out of territory - Isiolo'),
        ('out_of_territory_subukia', 'Out of territory - Subukia'),
        ('pesi', 'Pesi'),
        ('rumuruti', 'Rumuruti'),
        ('sipili', 'Sipili'),
        ('tandare', 'Tandare'),
        ('timau', 'Timau'),
        ('wiyumiririe', 'Wiyumiririe')
    ], string='Laikipia, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_tala_kangundo_isinya = fields.Selection([
        ('joska', 'Joska'),
        ('kagemi', 'Kagemi'),
        ('kamulu', 'Kamulu'),
        ('kangundo', 'Kangundo'),
        ('kayatta', 'Kayatta'),
        ('kinanie', 'Kinanie'),
        ('kitengela', 'Kitengela'),
        ('ol_donyo_sabuk', 'Ol Donyo Sabuk'),
        ('ruai', 'Ruai'),
        ('tala', 'Tala')
    ], string='Tala - Kangundo - Isinya, East sub-territory', store=True, default='', readonly=False)
    east_subterritory_timau_meru_isiolo = fields.Selection([
        ('chaaria', 'Chaaria'),
        ('ex_lewa', 'Ex - Lewa'),
        ('gitimene', 'Gitimene'),
        ('isiolo', 'Isiolo'),
        ('kianjai', 'Kianjai'),
        ('kibirichia', 'Kibirichia'),
        ('kiirua', 'Kiirua'),
        ('kithaku', 'Kithaku'),
        ('kithirune', 'Kithirune'),
        ('maili_saba', 'Maili Saba'),
        ('makandi', 'Makandi'),
        ('mbaaria', 'Mbaaria'),
        ('mbeu', 'Mbeu'),
        ('meru', 'Meru'),
        ('mulika', 'Mulika'),
        ('muriri', 'Muriri'),
        ('muthara', 'Muthara'),
        ('mutunyi', 'Mutunyi'),
        ('nkubu', 'Nkubu'),
        ('ntugi', 'Ntugi'),
        ('subuiga', 'Subuiga'),
        ('timau', 'Timau')
    ], string='Timau - Meru - Isiolo, East sub-territory', store=True, default='', readonly=False)
    west_subterritory_bomet_sotik_litein = fields.Selection([
        ('bomet_town', 'Bomet Town'),
        ('chebirbelek', 'Chebirbelek'),
        ('kamureito', 'Kamureito'),
        ('kapkwen', 'Kapkwen'),
        ('kaplong', 'Kaplong'),
        ('kapsimotwo', 'Kapsimotwo'),
        ('makimenyi', 'Makimenyi'),
        ('ndanai', 'Ndanai'),
        ('ol_mekenyu', 'Ol Mekenyu'),
        ('olenguruone', 'Olenguruone'),
        ('olulunga', 'Olulunga'),
        ('silibwet', 'Silibwet'),
        ('siongiroi', 'Siongiroi'),
        ('sogoo', 'Sogoo'),
        ('sotik', 'Sotik')
    ], string='Bomet Sotik Litein, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_eldama_ravine_londiani_burnt_forest = fields.Selection([
        ('burnt_forest', 'Burnt Forest'),
        ('chagaiya', 'Chagaiya'),
        ('eldama Ravine', 'Eldama Ravine'),
        ('kamara', 'Kamara'),
        ('kamwingi', 'Kamwingi'),
        ('kamwosor', 'Kamwosor'),
        ('kapchorua', 'Kapchorua'),
        ('leltot', 'Leltot'),
        ('londiani', 'Londiani'),
        ('matharu', 'Matharu'),
        ('mlango_moja', 'Mlango Moja'),
        ('muchorwe', 'Muchorwe'),
        ('nyaru', 'Nyaru')
    ], string='Eldama Ravine - Londiani - Burnt Forest, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_eldoret_turbo = fields.Selection([
        ('eldoret', 'Eldoret'),
        ('iten', 'Iten'),
        ('jua_kali', 'Jua Kali'),
        ('kaptagat', 'Kaptagat'),
        ('lessos', 'Lessos'),
        ('likunyani', 'Likunyani'),
        ('matunda', 'Matunda'),
        ('moiben', 'Moiben'),
        ('mois_bridge', 'Mois Bridge'),
        ('sango', 'Sango'),
        ('soy', 'Soy'),
        ('turbo', 'Turbo')
    ], string='Eldoret - Turbo, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_kakamega_kapsabet_vihiga = fields.Selection([
        ('chavakali', 'Chavakali'),
        ('gambogi', 'Gambogi'),
        ('kisumu', 'Kisumu'),
        ('majengo', 'Majengo'),
        ('malava', 'Malava'),
        ('maseno', 'Maseno'),
        ('mumias', 'Mumias')
    ], string='Kakamega - Kapsabet - Vihiga, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_kericho_nandi_ahero = fields.Selection([
        ('ahero', 'Ahero'),
        ('fort Tenan', 'Fort Tenan'),
        ('kapsabet', 'Kapsabet'),
        ('kapsoit', 'Kapsoit'),
        ('kericho', 'Kericho'),
        ('nandi', 'Nandi')
    ], string='Kericho - Nandi - Ahero, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_kisii_nyamira = fields.Selection([
        ('homabay', 'Homabay'),
        ('kisii', 'Kisii'),
        ('mbita', 'Mbita'),
        ('migori', 'Migori'),
        ('ndhiwa', 'Ndhiwa'),
        ('opapo', 'Opapo'),
        ('ranen', 'Ranen'),
        ('uriri', 'Uriri')
    ], string='Kisii - Nyamira, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_kitale_bungoma = fields.Selection([
        ('bungoma', 'Bungoma'),
        ('cherangany', 'Cherangany'),
        ('endebess', 'Endebess'),
        ('iten', 'Iten'),
        ('kachibora', 'Kachibora'),
        ('kamoi', 'Kamoi'),
        ('kapcherop', 'Kapcherop'),
        ('kapenguria', 'Kapenguria'),
        ('kaplamai', 'Kaplamai'),
        ('kaptalamwa', 'Kaptalamwa'),
        ('kapterit', 'Kapterit'),
        ('kiminini', 'Kiminini'),
        ('kipsorwa', 'Kipsorwa'),
        ('kitale', 'Kitale'),
        ('makutano', 'Makutano'),
        ('marakwet', 'Marakwet'),
        ('mois_bridge', 'Mois Bridge'),
        ('sibanga', 'Sibanga'),
        ('webuye', 'Webuye')
    ], string='Kitale - Bungoma, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_molo_njoro = fields.Selection([
        ('elburgon', 'Elburgon'),
        ('kamara', 'Kamara'),
        ('keringet', 'Keringet'),
        ('mau_narok', 'Mau Narok'),
        ('mogotio', 'Mogotio'),
        ('molo', 'Molo'),
        ('nakuru', 'Nakuru'),
        ('ngorika', 'Ngorika'),
        ('njoro', 'Njoro'),
        ('olenguruone', 'Olenguruone'),
        ('rongai', 'Rongai'),
        ('segutoni', 'Segutoni'),
        ('subukia', 'Subukia'),
        ('thika', 'Thika'),
        ('turi', 'Turi')
    ], string='Molo - Njoro, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_naivasha_gilgil = fields.Selection([
        ('gilgil', 'Gilgil'),
        ('kimende', 'Kimende'),
        ('mariagishu', 'Mariagishu'),
        ('nairegie_engare', 'Nairegie Engare'),
        ('naivasha', 'Naivasha'),
        ('narok', 'Narok'),
        ('ndabibi', 'Ndabibi'),
        ('soko_mjinga', 'Soko Mjinga'),
        ('wangige', 'Wangige')
    ], string='Naivasha - Gilgil, west sub-territory', store=True, default='', readonly=False)
    west_subterritory_nyandarua = fields.Selection([
        ('bushi', 'Bushi'),
        ('charagita', 'Charagita'),
        ('dundori', 'Dundori'),
        ('engineer', 'Engineer'),
        ('githambai', 'Githambai'),
        ('gwa_githae', 'Gwa Githae'),
        ('gwa_kiongo', 'Gwa Kiongo'),
        ('karangatha', 'Karangatha'),
        ('kariamu', 'Kariamu'),
        ('kasuku', 'Kasuku'),
        ('kinangop', 'Kinangop'),
        ('matopeni', 'Matopeni'),
        ('munyaka', 'Munyaka'),
        ('mwendandu', 'Mwendandu'),
        ('ndemi', 'Ndemi'),
        ('ndinda', 'Ndinda'),
        ('ndunyu_njeru', 'Ndunyu Njeru'),
        ('njabini', 'Njabini'),
        ('nyahururu', 'Nyahururu'),
        ('ol_kalou', 'Ol Kalou'),
        ('oljororok', 'Oljororok'),
        ('sairinga', 'Sairinga'),
        ('shamata', 'Shamata'),
        ('subuku', 'Subuku'),
        ('tumaini', 'Tumaini'),
        ('wanjohi', 'Wanjohi'),
        ('wiyumiririe', 'Wiyumiririe')
    ], string='Nyandarua, west sub-territory', store=True, default='', readonly=False)
    east_territory = fields.Selection(selection=[
        ('east_subterritory_embu_tharaka', 'Embu Tharaka'),
        ('east_subterritory_kiambu_muranga', 'Kiambu Muranga'),
        ('east_subterritory_kilifi_malindi', 'Kilifi Malindi'),
        ('east_subterritory_kirinyagab_muranga', 'Kirinyagab Muranga'),
        ('east_subterritory_machakos', 'Machakos'),
        ('east_subterritory_nyeri', 'Nyeri'),
        ('east_subterritory_oloitoktok_emali', 'Oloitoktok Emali'),
        ('east_subterritory_laikipia', 'Laikipia'),
        ('east_subterritory_tala_kangundo_isinya', 'Tala Kangundo Isinya'),
        ('east_subterritory_timau_meru_isiolo', 'Timau Meru Isiolo')
    ], string='East Territory', store=True, default='')
    west_territory = fields.Selection(selection=[
        ('west_subterritory_bomet_sotik_litein', 'Bomet Sotik Litein'),
        ('west_subterritory_eldama_ravine_londiani_burnt_forest', 'Eldama Ravine Londiani Burnt Forest'),
        ('west_subterritory_eldoret_turbo', 'Eldoret Turbo'),
        ('west_subterritory_kakamega_kapsabet_vihiga', 'Kakamega Kapsabet Vihiga'),
        ('west_subterritory_kericho_nandi_ahero', 'Kericho Nandi Ahero'),
        ('west_subterritory_kisii_nyamira', 'Kisii Nyamira'),
        ('west_subterritory_kitale_bungoma', 'Kitale Bungoma'),
        ('west_subterritory_molo_njoro', 'Molo Njoro'),
        ('west_subterritory_naivasha_gilgil', 'Naivasha Gilgil'),
        ('west_subterritory_nyandarua', 'Nyandarua')
    ], string='West Territory', store=True, default='', readonly=False)

    @api.onchange('east_territory', 'west_territory', 'regions',
                  'east_subterritory_embu_tharaka', 'east_subterritory_kiambu_muranga',
                  'east_subterritory_kilifi_malindi', 'east_subterritory_kirinyagab_muranga',
                  'east_subterritory_machakos', 'east_subterritory_nyeri',
                  'east_subterritory_oloitoktok_emali', 'east_subterritory_laikipia',
                  'east_subterritory_tala_kangundo_isinya', 'east_subterritory_timau_meru_isiolo',
                  'west_subterritory_bomet_sotik_litein', 'west_subterritory_eldama_ravine_londiani_burnt_forest',
                  'west_subterritory_eldoret_turbo', 'west_subterritory_kakamega_kapsabet_vihiga',
                  'west_subterritory_kericho_nandi_ahero', 'west_subterritory_kisii_nyamira',
                  'west_subterritory_kitale_bungoma', 'west_subterritory_molo_njoro',
                  'west_subterritory_naivasha_gilgil', 'west_subterritory_nyandarua'
                  )
    @api.depends('west_territory', 'east_territory', 'regions')
    @api.model
    def _compute_regions2(self):
        for rec in self:
            # self.ensure_one()
            if rec.regions == 'west_territory':
                if rec.east_territory == self.east_territory:
                    if self.east_territory == 'east_subterritory_embu_tharaka':
                        for item in east_subterritory_embu_tharaka:
                            if item[0] == rec.east_subterritory_embu_tharaka:
                                return item[0]
                        # self.ensure_one()
                        # rec.east_subterritory_embu_tharaka = rec.east_subterritory_embu_tharaka
                        # self.east_territory = True
                    if self.east_territory == 'east_subterritory_kiambu_muranga':
                        self.ensure_one()
                        rec.east_subterritory_kiambu_muranga = rec.east_subterritory_kiambu_muranga
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_kilifi_malindi':
                        self.ensure_one()
                        rec.east_subterritory_kilifi_malindi = rec.east_subterritory_kilifi_malindi
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_kirinyagab_muranga':
                        self.ensure_one()
                        rec.east_subterritory_kirinyagab_muranga = rec.east_subterritory_kirinyagab_muranga
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_machakos':
                        self.ensure_one()
                        rec.east_subterritory_machakos = rec.east_subterritory_machakos
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_nyeri':
                        self.ensure_one()
                        rec.east_subterritory_nyeri = rec.east_subterritory_nyeri
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_oloitoktok_emali':
                        self.ensure_one()
                        rec.east_subterritory_oloitoktok_emali = rec.east_subterritory_oloitoktok_emali
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_laikipia':
                        self.ensure_one()
                        rec.east_subterritory_laikipia = rec.east_subterritory_laikipia
                        self.east_territory = True
                    if self.east_territory == 'east_subterritory_tala_kangundo_isinya':
                        rec.east_subterritory_tala_kangundo_isinya = self.east_subterritory_tala_kangundo_isinya
                        for item in east_subterritory_tala_kangundo_isinya:
                            if item[9]:
                                return dict(east_subterritory_tala_kangundo_isinya)[self.east_territory]
                        # self.ensure_one()
                        # rec.east_subterritory_tala_kangundo_isinya = rec.east_subterritory_tala_kangundo_isinya
                        # self.east_territory = True
                    if self.east_territory == 'east_subterritory_timau_meru_isiolo':
                        var = dict(self._fields['east_subterritory_timau_meru_isiolo'].selection).get(
                            self.east_subterritory_timau_meru_isiolo)
                        for key, value in var:
                            if key[9]:
                                return value[9]
                    else:
                        self.east_territory = False
            else:
                if rec.regions == 'west_territory':
                    if rec.west_territory == self.west_territory:
                        if self.west_territory == 'west_subterritory_bomet_sotik_litein':
                            var = dict(
                                self._fields['west_subterritory_eldama_ravine_londiani_burnt_forest'].selection).get(
                                self.west_subterritory_eldama_ravine_londiani_burnt_forest)
                            for key, value in var:
                                if key[0]:
                                    return value[0]
                        if self.west_territory == 'west_subterritory_eldama_ravine_londiani_burnt_forest':
                            var = dict(
                                self._fields['west_subterritory_eldama_ravine_londiani_burnt_forest'].selection).get(
                                self.west_subterritory_eldama_ravine_londiani_burnt_forest)
                            for key, value in var:
                                if key[1]:
                                    return value[1]
                        if self.west_territory == 'west_subterritory_eldoret_turbo':
                            for item in west_subterritory_eldoret_turbo:
                                if item[2] == self.west_subterritory_eldoret_turbo:
                                    return item[2]
                            # self.ensure_one()
                            # rec.west_subterritory_eldoret_turbo = self.west_subterritory_eldoret_turbo
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_kakamega_kapsabet_vihiga':
                            for item in west_subterritory_kakamega_kapsabet_vihiga:
                                if item[3] == self.west_subterritory_kakamega_kapsabet_vihiga:
                                    return item[3]
                            # self.ensure_one()
                            # rec.west_subterritory_kakamega_kapsabet_vihiga = self.west_subterritory_kakamega_kapsabet_vihiga
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_kericho_nandi_ahero':
                            for item in west_subterritory_kericho_nandi_ahero:
                                if item[4] == self.west_subterritory_kericho_nandi_ahero:
                                    return item[4]
                            # self.ensure_one()
                            # rec.west_subterritory_kericho_nandi_ahero = self.west_subterritory_kericho_nandi_ahero
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_kisii_nyamira':
                            for item in west_subterritory_kisii_nyamira:
                                if item[5] == self.west_subterritory_kisii_nyamira:
                                    return item[5]
                            # self.ensure_one()
                            # rec.west_subterritory_kisii_nyamira = self.west_subterritory_kisii_nyamira
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_kitale_bungoma':
                            for item in west_subterritory_kitale_bungoma:
                                if item[6] == self.west_subterritory_kitale_bungoma:
                                    return item[6]
                            # self.ensure_one()
                            # rec.west_subterritory_kitale_bungoma = self.west_subterritory_kitale_bungoma
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_molo_njoro':
                            for item in west_subterritory_molo_njoro:
                                if item[7] == self.west_subterritory_molo_njoro:
                                    return item[7]
                            # self.ensure_one()
                            # rec.west_subterritory_molo_njoro = self.west_subterritory_molo_njoro
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_naivasha_gilgil':
                            for item in west_subterritory_naivasha_gilgil:
                                if item[8] == self.west_subterritory_naivasha_gilgil:
                                    return item[8]
                            # self.ensure_one()
                            # rec.west_subterritory_naivasha_gilgil = self.west_subterritory_naivasha_gilgil
                            # self.west_territory = True
                        if self.west_territory == 'west_subterritory_nyandarua':
                            for item in west_subterritory_nyandarua:
                                if item[9] == self.west_subterritory_nyandarua:
                                    return item[9]
                            # self.ensure_one()
                            # rec.west_subterritory_nyandarua = self.west_subterritory_nyandarua
                            # self.west_territory = True
                        else:
                            self.west_territory = False

    # @api.onchange('west_territory', 'east_territory', 'regions')
    # @api.depends('west_territory', 'east_territory', 'regions')
    # @api.model
    # def _compute_regions(self):
    #     for rec in self:
    #         if rec.regions == 'east_territory':
    #             rec.east_territory = self.east_territory
    #         else:
    #             if rec.regions == 'west_territory':
    #                 rec.west_territory = self.west_territory
