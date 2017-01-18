class Storage(object):
    def set(self, model):
        pass

    def get(self, model_cls, **query):
        pass

    def drop(self, models):
        pass


class SingletonRamStorage(object):
    items = {}

    def set(self, model):
        storage = self._get_model_storage(model.__class__)
        storage[model.pk] = model

    def get(self, model_cls, **query):
        storage = self._get_model_storage(model_cls)
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

    def _get_model_storage(self, model):
        model_key = model.__class__
        try:
            return self.items[model_key]
        except KeyError:
            self.items[model_key] = {}
            return self.items[model_key]