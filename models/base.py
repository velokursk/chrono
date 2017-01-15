import models.fields


class ModelMeta(object):
    _fields = {}

    def __init__(self, **kwargs):
        self.__values = {
            name: factory()
            for name, factory in self._fields.iteritems()
        }
        for name, value in kwargs.iteritems():
            self.__check_field_name(name)
            self.__values[name] = value

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            self.__check_field_name(name)
        self.__dict__[name] = value

    def __getattr__(self, name):
        try:
            self.__values[name]
        except KeyError:
            raise AttributeError(name)

    def __str__(self):
        mask = '<{cls_name}: {values}>'
        return mask.format(cls_name=self.__class__.__name__, values=self.__values)

    @classmethod
    def __check_field_name(cls, name):
        if name not in cls._fields:
            raise AttributeError(name)


class ClassMeta(ModelMeta):
    _fields = {
        'model_field_names': list,  # list of all field names for current model
    }


class InstanceMeta(ModelMeta):
    _fields = {
        'values': dict,
    }


class FieldMcs(type):
    # we don't support field names with leading underscore

    def __new__(mcs, name, bases, dict_):
        cls = type(name, bases, dict_)
        fields = self.get_all_fields(bases, dict_)
        cls._cls_meta.model_field_names = fields.keys()

    def get_model_fields(self, dict_):
        fields = {
            key: value
            for key, value in dict_
            if isinstance(value, models.fields.Field)
        }
        return fields

    def get_parents_fields(self, bases):
        pass

    def get_all_fields(self, bases, dict_):
        fields = {}
        fields.update(self.get_parents_fields(bases))
        fields.update(self.get_model_fields(dict_))
        return fields


class Model(object):
    __metaclass__ = FieldMcs

    _cls_meta = ClassMeta()
    _meta = None

    id = None

    def __init__(self, **kwargs):
        self._meta = InstanceMeta()

        for name, value in kwargs.iteritems():
            if name not in self._cls_meta.model_field_names:
                raise ValueError
            setattr(self, name, value)

    def __str__(self):
        mask = '<{}: {}, values: {}>'
        return mask.format(self.__class__.__name__, self.id, self._meta.values)


class User(Model):
    pass


class Race(Model):
    pass


class RaceConfig(Model):
    pass


class Checkpoint(Model):
    # a group of sensors
    pass


class RfidMark(Model):
    # it's possible to ise multiple marks per user
    pass


class Emergency(Model):
    # object that represents context which we can't handle
    # requires human reaction
    pass


class CheckpointEmergency(Emergency):
    pass


class RaceEmergency(Emergency):
    pass
