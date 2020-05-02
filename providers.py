from provider import Provider


class Providers:
    just_watch = None
    providers = {}

    def __init__(self, just_watch):
        self.just_watch = just_watch
        for provider in just_watch.get_providers():
            provider_obj = Provider(provider)
            self.providers[provider_obj.id] = provider_obj

    def get_provider(self, provider_id):
        return self.providers.get(provider_id)
