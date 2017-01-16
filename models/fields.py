# fields for models
import sys


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


class IntegerField(Field):
    def __init__(self, default=None, minimum=0, maximum=sys.maxint):
        self.minimum = minimum
        self.maximum = maximum
        self.default = default

    def __get__(self, instance, klass):
        try:
            return instance._meta.values[self.name]
        except KeyError:
            if self.default is not None:
                return self.default
            raise AttributeError

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError
        if not self.minimum <= value <= self.maximum:
            raise ValueError
        instance._meta.values[self.name] = value
