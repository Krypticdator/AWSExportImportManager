import requests
import untangle


class EndpointManager(object):
    def __init__(self):
        super().__init__()
        self.ep_url = 'https://eo7sjt6hvj.execute-api.us-west-2.amazonaws.com/prod'

    def get_attributes(self, attribute_type: str):
        API_RESOURCE = '/skillblueprints'
        GET_METHOD = '/get'
        endpoint = self.ep_url + API_RESOURCE + GET_METHOD
        print('retrieving skills...')
        response = requests.post(url=endpoint, json={'type': attribute_type})

        response_json = response.json()
        skills = []
        for skill in response_json['response']:
            skills.append(skill)
        return skills

    def import_skills_from_xml(self):
        API_URL = 'https://eo7sjt6hvj.execute-api.us-west-2.amazonaws.com/prod'
        API_RESOURCE = '/skillblueprints'
        ADD_METHOD = '/add'

        ENDPOINT = API_URL + API_RESOURCE + ADD_METHOD
        obj = untangle.parse('skills.xml')
        for skill in obj.skills.skill:
            name = skill.name.cdata
            stat = skill.stat.cdata
            category = skill.category.cdata
            desc = skill.description.cdata
            chippable = skill.chippable.cdata
            diff = skill.diff_modifier.cdata
            short = skill.short.cdata
            print('adding ' + name + "...")
            response = requests.post(url=ENDPOINT, json={'name': name,
                                                         'stat': stat,
                                                         'type': 'skill',
                                                         'category': category,
                                                         'desc': desc,
                                                         'chippable': chippable,
                                                         'diff': diff,
                                                         'short': short,
                                                         'cost': "1",
                                                         'chip_lvl_cost':'0',
                                                         'tags':None})
            # print(response.json())
            response_json = response.json()
            if response_json['response']['message'] == 'error':
                print('invalid API call')
                break

    def import_talents_from_xml(self):
        obj = untangle.parse('preferences.xml')
        for talent in obj.preferences.talents.talent:
            name = str.lower(talent.name.cdata)
            desc = talent.description.cdata

            self.add_attribute_blueprint(name=name, desc=desc, cost="3", blueprint_type='talent')

    def import_perks_from_xml(self):
        obj = untangle.parse('preferences.xml')
        for perk in obj.preferences.perks.perk:
            name = str.lower(perk.name.cdata)
            desc = perk.description.cdata
            cost = str(perk.cost.cdata)

            self.add_attribute_blueprint(name=name, desc=desc, cost=cost, blueprint_type='perk')

    def import_complications_from_xml(self):
        obj = untangle.parse('preferences.xml')
        for complication in obj.preferences.complications.complication:
            name = str.lower(complication.name.cdata)
            desc = complication.description.cdata
            category = str.lower(complication.category.cdata)

            self.add_attribute_blueprint(name=name, desc=desc, category=category, blueprint_type='complication')

    def add_attribute_blueprint(self, name, stat=None, category=None, desc=None, chippable=False, diff=None, short=None,
                                cost="1", chip_lvl_cost=None, blueprint_type='skill'):
        API_URL = 'https://eo7sjt6hvj.execute-api.us-west-2.amazonaws.com/prod'
        API_RESOURCE = '/skillblueprints'
        ADD_METHOD = '/add'

        ENDPOINT = API_URL + API_RESOURCE + ADD_METHOD

        print('adding blueprint ' + name + "...")

        response = requests.post(url=ENDPOINT, json={'name': name,
                                                     'stat': stat,
                                                     'type': blueprint_type,
                                                     'category': category,
                                                     'desc': desc,
                                                     'chippable': chippable,
                                                     'diff': diff,
                                                     'short': short,
                                                     'cost': cost,
                                                     'chip_lvl_cost': chip_lvl_cost,
                                                     'tags': None})

def main():
    pass

if __name__ == '__main__':
    main()
