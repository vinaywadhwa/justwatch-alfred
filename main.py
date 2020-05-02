import argparse
import sys
import constants
from media_item import MediaItem
from workflow import Workflow3, ICON_ERROR
from workflow.background import run_in_background, is_running
from media_items import MediaItems
from providers import Providers
import json
from thumbnails import Thumbs

_thumbs = None
wf = None


def thumbnail(img_path):
    return thumbs().thumbnail(img_path)


def thumbs():
    global _thumbs
    if _thumbs is None:
        _thumbs = Thumbs(wf.datafile('thumbs'))
    return _thumbs


def show_results_providers(media_item, should_rerun):
    offers = media_item.offers
    if len(offers) > 0:
        result = {'items': [offer.get_alfred_json(offers[offer]) for offer in
                            sorted(offers.keys(), key=lambda i: i.display_priority)]}
        if should_rerun:
            result['rerun'] = 0.5
    else:

        result = {'items': [{'title': "Nothing was found",
                             'icon': {'path': ICON_ERROR},
                             'subtitle': "No movie/tv-show was found with that name (%s)" % constants.LOCALE,
                             'valid': False,
                             'autocomplete': ""
                             }]

                  }
    print(json.dumps(result))


def process_thumbnails_providers(t, media_item):
    more_images_to_load = False

    if len(media_item.offers) == 0:
        return

    for offer in media_item.offers.keys():
        image_url = offer.icon_url
        icon_path = None
        if image_url.startswith('http'):
            icon_path = t.thumbnail(image_url)
        if icon_path is None:
            more_images_to_load = True
            wf.logger.error("more_images_to_load = %s" % more_images_to_load)
            icon_path = wf.workflowfile("icon.png")
        offer.icon_url = icon_path
    return more_images_to_load


def show_results_search(media_items, should_rerun):
    if len(media_items) > 0:
        result = {'items': media_items}
        wf.logger.error("should_rerun = %s" % should_rerun)
        if should_rerun:
            result['rerun'] = 0.5
    else:

        result = {'items': [{'title': "Nothing was found",
                             'subtitle': "No movie/tv-show was found with that name (%s)" % constants.LOCALE,
                             'icon': {'path': ICON_ERROR},
                             'valid': False,
                             'autocomplete': ""
                             }]

                  }
    print(json.dumps(result))


def process_thumbnails_search(t, media_items):
    more_images_to_load = False
    for media_item in media_items:
        image_url = media_item['icon']
        icon_path = None
        if image_url.startswith('http'):
            icon_path = t.thumbnail(image_url)
            media_item['quicklookurl'] = icon_path
            media_item['subtitle'] = "%s | quick-look to enlarge poster" % media_item['subtitle']
        if icon_path is None:
            more_images_to_load = True
            wf.logger.error("more_images_to_load = %s" % more_images_to_load)
            icon_path = wf.workflowfile("icon.png")
        media_item['icon'] = {"path": icon_path}
    return more_images_to_load


def parse_title_id(title_id):
    wf.logger.error("$$$$$$$$$$" + title_id)
    split_meat = title_id.split("|")
    content_type = split_meat[len(split_meat) - 2].strip()
    title_id = split_meat[len(split_meat) - 1].strip()
    return title_id, content_type


def main(wf):
    from justwatch import JustWatch
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search_keyword')
    parser.add_argument('-t', '--title_id')
    parser.add_argument('-i', '--input_locale')

    args = parser.parse_args()

    search_keyword = args.search_keyword
    title_id = args.title_id
    constants.LOCALE = args.input_locale

    just_watch = JustWatch(country=constants.LOCALE)
    providers = Providers(just_watch)
    t = thumbs()
    if search_keyword is not None:
        media_items = MediaItems(just_watch, sys.argv[len(sys.argv) - 1], providers).get_alfred_json_list()
        should_rerun = process_thumbnails_search(t, media_items)
        wf.logger.error("should_rerun = %s" % should_rerun)
        show_results_search(media_items, should_rerun)
    elif title_id is not None:
        title_id, content_type = parse_title_id(title_id)
        media_item = MediaItem(just_watch.get_title(title_id=title_id, content_type=content_type), providers)
        should_rerun = process_thumbnails_providers(t, media_item)
        show_results_providers(media_item, should_rerun)
    else:
        pass

    t.save_queue()
    if t.has_queue:
        if not is_running('generate_thumbnails'):
            run_in_background('generate_thumbnails',
                              ['/usr/bin/python',
                               wf.workflowfile('thumbnails.py')])


if __name__ == '__main__':
    wf = Workflow3(libraries=['./lib'])
    sys.exit(wf.run(main))
