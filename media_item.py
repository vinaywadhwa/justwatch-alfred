import json
import pprint
from datetime import datetime

import constants


class MediaItem:
    providers = None
    is_valid = True
    media_item_data = ''
    id = ''
    title = ''
    display_priority = ''
    icon_url = ''
    media_type = ''
    original_release_year = ''
    offers = {}

    def __init__(self, media_item_data, providers):
        self.providers = providers
        self.media_item_data = media_item_data
        self.parse(media_item_data)
        # pprint.pprint(vars(self))

    def parse(self, media_item):
        self.id = media_item['id']
        self.media_type = media_item['object_type']

        if 'title' in media_item:
            self.title = media_item['title']
        else:
            self.title = media_item['full_path'].split('/')[-1].replace('-', ' ').title()

        if 'original_release_year' in media_item:
            self.original_release_year = media_item['original_release_year']

        if 'poster' in media_item:
            self.icon_url = self.get_image_url(media_item['poster'])
        # print(self.icon_url)
        if 'offers' in media_item:
            self.offers = self.parse_offers(media_item['offers'])
        # pprint.pprint(media_item)
        # pprint.pprint(vars(self))

        if len(self.offers) == 0 and self.original_release_year == '':
            self.is_valid = False

    def get_image_url(self, relative_path):
        # https://images.justwatch.com/icon/430997/s100
        # 'icon_url': '/icon/430997/{profile}',
        image_url_prefix = "https://images.justwatch.com"
        image_quality = "s592"
        return "%s%s" % (image_url_prefix, relative_path.format(profile=image_quality))

    def parse_offers(self, offers):
        offer_list = {}
        # pprint.pprint(offers)
        for offer in offers:
            urls = offer['urls']
            streaming_url = urls['standard_web']
            provider_id = offer['provider_id']
            if 'date_created' in offer:
                available_since = datetime.strptime(offer['date_created'], '%Y-%m-%d').strftime('%b %Y')
            else:
                available_since = None
            monetization_type = offer['monetization_type']
            monetization_type = "%s%s" % (monetization_type[:0], monetization_type[0:].capitalize())
            if (monetization_type != "rent" or monetization_type != "buy") \
                    and ('retail_price' in offer and 'currency' in offer):
                currency = offer['currency']
                retail_price = offer['retail_price']
                price = "%s (%s %s)" % (monetization_type, currency, retail_price)
            else:
                price = monetization_type
            provider = self.providers.get_provider(provider_id)

            if provider is not None:
                offer_list[provider] = {"streaming_url": streaming_url, "price": price,
                                        "available_since": available_since}
                # offer_list[provider] = streaming_url
        return offer_list

    def to_alfred_json(self):
        result = {}
        result['uid'] = self.id
        result['type'] = 'default'
        if self.original_release_year != '':
            result['title'] = "%s (%s)" % (self.title, self.original_release_year)
        else:
            result['title'] = self.title

        result['icon'] = self.icon_url
        result['autocomplete'] = self.title
        # result['uid'] = self.id
        if len(self.offers) > 0:
            provider_names = ', '.join(
                [offer.title for offer in sorted(self.offers.keys(), key=lambda i: i.display_priority)])
            result['subtitle'] = "Available (%s) :  %s" % (constants.LOCALE, provider_names)
            result['arg'] = "%s|%s|%s" % (self.get_limited_length_title(), self.media_type, self.id)
            result['valid'] = True
        else:
            result['subtitle'] = "No providers available (%s)" % constants.LOCALE
            result['arg'] = None
            result['valid'] = False


        return result

    def get_limited_length_title(self):
        result = self.title
        if len(self.title) > 11:
            result = "%s..." % self.title[0:8]
        return result
