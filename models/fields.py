# fields for models
import datetime
import sys


class Field(object):
    name = None  # we should set this instance value from mcs
    default = None

    def __init__(self):
        pass

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


class HexTextField(TextField):
    def validate_value(self, value):
        super(HexTextField, self).validate_value(value)
        for ch in value:
            if ch not in '0123456789ABCDEF':
                raise ValueError


class ChoicesField(Field):
    def __init__(self, choices, default=None):
        self.choices = choices
        self.default = default

    def validate_value(self, value):
        if value not in self.choices:
            raise ValueError


class DateField(Field):
    def __init__(self, default=datetime.datetime.now()):
        self.default = default

    def validate_value(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError
