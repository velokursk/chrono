# fields for models


class Field(object):
    def __get__(self, instance, klass):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def __del__(self, instance):
        raise NotImplementedError
