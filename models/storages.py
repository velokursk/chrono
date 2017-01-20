class Storage(object):
    def __init__(self, model_cls):
        self.model_cls = model_cls

    def set(self, model):
        pass

    def get(self, **query):
        pass

    def drop(self, models):
        pass


class SingletonRamStorage(Storage):
    items = {}

    def set(self, model):
        storage = self._get_model_storage()
        storage[model.pk] = model

    def get(self, **query):
        storage = self._get_model_storage()
        models = storage.values()
        for attr, value in query.iteritems():
            models = [
                model
                for model in models
                if getattr(model, attr) == value
            ]
        return models

    def drop(self, *models):
        for model in models:
            storage = self._get_model_storage(model.__class__)
            del storage[model.pk]

    def _get_model_storage(self):
        model_key = self.model_cls
        try:
            return self.items[model_key]
        except KeyError:
            self.items[model_key] = {}
            return self.items[model_key]
