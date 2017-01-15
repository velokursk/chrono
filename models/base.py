import models.fields


class ModelMeta(object):
    __fields = {}

    def __init__(self, **kwargs):
        # self.__values = {}
        self.__values = {
            name: factory()
            for name, factory in self.__fields.iteritems()
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
        if name not in cls.__fields:
            raise AttributeError(name)


class ClassMeta(ModelMeta):
    __fields = {
        'model_field_names': list,  # list of all field names for current model
    }


class InstanceMeta(ModelMeta):
    __fields = {
        'values': dict,
    }


class Model(object):
    __metaclass__ = models.fields.FieldMcs

    _cls_meta = ClassMeta()
    _meta = None

    def __init__(self, **kwargs):
        self._meta = InstanceMeta()

        for name, value in kwargs.iteritems():
            if name not in self._cls_meta.model_field_names:
                raise ValueError
            setattr(self, name, value)


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
