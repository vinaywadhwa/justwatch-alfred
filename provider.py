import pprint

import constants


class Provider:
    id = ''
    title = ''
    short_name = ''
    monetization_types = []
    display_priority = ''
    icon_url = ''

    def __init__(self, provider_data):
        self.parse(provider_data)

    def parse(self, provider):
        self.title = provider['clear_name']
        self.short_name = provider['short_name']
        self.monetization_types = provider['monetization_types']
        self.id = provider['id']
        self.display_priority = provider['display_priority']
        self.icon_url = self.get_image_url(provider['icon_url'])
        # pprint.pprint(provider)
        # pprint.pprint(vars(self))

    def get_image_url(self, relative_path):
        # https://images.justwatch.com/icon/430997/s100
        # 'icon_url': '/icon/430997/{profile}',
        image_url_prefix = "https://images.justwatch.com"
        image_quality = "s100"
        return "%s%s" % (image_url_prefix, relative_path.format(profile=image_quality))

    def get_alfred_json(self, streaming_url):
        result = {}
        # result['uid'] = self.id
        result['type'] = 'default'
        result['title'] = self.title
        result['icon'] = {"path": self.icon_url}
        result['autocomplete'] = self.title
        # result['uid'] = self.id
        result['valid'] = True
        result['subtitle'] = "Available (%s) :  %s" % (constants.LOCALE, streaming_url)
        result['arg'] = streaming_url
        result['quicklookurl'] = streaming_url
        return result
