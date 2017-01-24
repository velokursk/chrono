# fields for models
import datetime
import sys


class Field(object):
    name = None  # we should set this instance value from mcs

    def __init__(self, **common_kwargs):
        if 'default' in common_kwargs:
            self.validate_value(common_kwargs['default'])
            self.default = common_kwargs['default']
            self.has_default = True
        else:
            self.has_default = False

        self.primary = bool(common_kwargs.get('primary', False))

        unique = bool(common_kwargs.get('unique', False))
        self.unique = unique or self.primary

    def __get__(self, instance, klass):
        if instance is None:
            return self
        try:
            return instance._meta.values[self.name]
        except KeyError:
            if self.has_default:
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
    def __init__(self, minimum=0, maximum=sys.maxint, **common_kwargs):
        self.minimum = minimum
        self.maximum = maximum
        super(IntegerField, self).__init__(minimum=minimum, maximum=maximum, **common_kwargs)

    def validate_value(self, value):
        if not isinstance(value, int):
            raise TypeError
        if not self.minimum <= value <= self.maximum:
            raise ValueError


class TextField(Field):
    def __init__(self, max_len=1024, **common_kwargs):
        self.max_len = max_len
        super(TextField, self).__init__(max_len=1024, **common_kwargs)

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
        self.choices = choices
        super(ChoicesField, self).__init__(choices, **common_kwargs)

    def validate_value(self, value):
        if value not in self.choices:
            raise ValueError


class DateField(Field):
    def validate_value(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError


class ForeignKeyField(Field):
    def __init__(self, model_cls, multi=False, **common_kwargs):
        self.model_cls = model_cls
        self.multi = multi
        self.pk_name = model_cls._cls_meta.primary_field
        super(ForeignKeyField, self).__init__(model_cls, multi, **common_kwargs)

    def __get__(self, instance, klass):
        value = super(ForeignKeyField, self).__get__(instance, klass)
        result = [
            self.model_cls.objects.get(**{self.pk_name: pk})
            for pk in value
        ]
        return result
