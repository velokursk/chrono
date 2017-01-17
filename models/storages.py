class Storage(object):
    def set(self, model):
        pass

    def get(self, **query):
        pass

    def drop(self, models):
        pass


class RamStorage(object):
    items = {}

    def set(self, model):
        pass

    def get(self, **query):
        pass

    def drop(self, models):
        pass

    def _get_model_storage(self, model):
        model_key = model.__class__
        try:
            return self.items[model_key]
        except KeyError:
            self.items[model_key] = {}
            return self.items[model_key]

    def _get_model_pk(self, model):
        pass
