import models.storages
import models.errors


class Manager(object):
    def __init__(self, storage_cls):
        pass

    def __get__(self, instance, klass):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def __del__(self, instance):
        raise NotImplementedError

    def create(self, model_attrs):
        pass

    def drop(self, model):
        pass

    def filter(self, **query):
        pass

    def get(self, **query):
        pass

    def save(self, model):
        pass

    def get_last_created_pk(self):
        pass


class ModelManager(Manager):
    def __init__(self, storage_cls=models.storages.SingletonRamStorage):
        self.storage_cls = storage_cls

    def __get__(self, instance, klass):
        if not hasattr(self.klass):
            self.klass = klass
            self.storage = self.storage_cls(klass)
        return self

    def create(self, model, kwargs):
        pass

    def drop(self, model):
        self.storage.drop(model)

    def filter(self, **query):
        return self.storage.get(**query)

    def get(self, **query):
        result = self.storage.get(**query)
        if len(result) != 1:
            raise models.errors.MoreThanOneError
        return result[0]

    def save(self, model):
        self.storage.set(model)

    def get_last_created_pk(self):
        self.last_pk = None
        pass
