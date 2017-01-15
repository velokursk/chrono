# fields for models


class Field(object):
    name = None  # we should set this instance value from mcs

    def __get__(self, instance, klass):
        try:
            return instance._meta.values[self.name]
        except KeyError:
            raise AttributeError

    def __set__(self, instance, value):
        instance._meta.values[self.name] = value

    def __del__(self, instance):
        raise NotImplementedError
