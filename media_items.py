from media_item import MediaItem


class MediaItems:
    just_watch = None
    providers = None
    media_items_list = []
    media_items_alfred_json_list = []

    def __init__(self, just_watch, query, providers):
        self.just_watch = just_watch
        self.providers = providers
        for media_item in just_watch.search_for_item(query, page_size=5)['items']:
            media_item = MediaItem(media_item, providers)
            if media_item.is_valid:
                self.media_items_list.append(media_item)
                self.media_items_alfred_json_list.append(media_item.to_alfred_json())
            else:
                pass  # ignore this title

    def get(self):
        return self.media_items_list

    def get_alfred_json_list(self):
        return self.media_items_alfred_json_list
