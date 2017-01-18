# fields for models
import datetime
import sys


class Field(object):
    name = None  # we should set this instance value from mcs
    default = None
    primary = False

    def __init__(self, **common_kwargs):
        self.common = {}

        if 'default' in common_kwargs:
            self.validate_value(common_kwargs['default'])
            self.common['default'] = common_kwargs['default']
            self.common['has_default'] = True
        else:
            self.common['has_default'] = False

        self.common['primary'] = bool(common_kwargs.get('primary', False))

        unique = bool(common_kwargs.get('unique', False))
        self.common['unique'] = unique or self.common['primary']

    def __get__(self, instance, klass):
        try:
            return instance._meta.values[self.name]
        except KeyError:
            if self.common['has_default']:
                return self.common['default']
            raise AttributeError

    def __set__(self, instance, value):
        self.validate_value(value)
        instance._meta.values[self.name] = value

    def __del__(self, instance):
        raise NotImplementedError

    def validate_value(self, value):
        return


class IntegerField(Field):
    def __init__(self, minimum=0, maximum=sys.maxint, **common_kwargs):
        super(IntegerField, self).__init__(minimum=0, maximum=sys.maxint, **common_kwargs)
        self.minimum = minimum
        self.maximum = maximum

    def validate_value(self, value):
        if not isinstance(value, int):
            raise TypeError
        if not self.minimum <= value <= self.maximum:
            raise ValueError


class TextField(Field):
    def __init__(self, max_len=1024, **common_kwargs):
        super(TextField, self).__init__(max_len=1024, **common_kwargs)
        self.max_len = max_len

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
    def __init__(self, choices, **common_kwargs):
        super(ChoicesField, self).__init__(choices, **common_kwargs)
        self.choices = choices

    def validate_value(self, value):
        if value not in self.choices:
            raise ValueError


class DateField(Field):
    def validate_value(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError
