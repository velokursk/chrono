# fields for models
import sys


class Field(object):
    name = None  # we should set this instance value from mcs
    default = None

    def __get__(self, instance, klass):
        try:
            return instance._meta.values[self.name]
        except KeyError:
            if self.default is not None:
                return self.default
            raise AttributeError

    def __set__(self, instance, value):
        self.validate_value(value)
        instance._meta.values[self.name] = value

    def __del__(self, instance):
        raise NotImplementedError

    def validate_value(self, value):
        return


class IntegerField(Field):
    def __init__(self, default=None, minimum=0, maximum=sys.maxint):
        self.minimum = minimum
        self.maximum = maximum
        self.default = default

    def validate_value(self, value):
        if not isinstance(value, int):
            raise TypeError
        if not self.minimum <= value <= self.maximum:
            raise ValueError


class TextField(Field):
    def __init__(self, default=None, max_len=1024):
        self.max_len = max_len
        self.default = default

    def validate_value(self, value):
        if not isinstance(value, basestring):
            raise TypeError
        if len(value) > self.max_len:
            raise ValueError
