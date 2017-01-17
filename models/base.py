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
            return self.__values[name]
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
        klass = super(FieldMcs, mcs).__new__(mcs, name, bases, dict_)
        field_names = mcs.get_all_field_names(bases, dict_)
        klass._cls_meta.model_field_names = field_names
        mcs.update_name_on_fields(klass)
        return klass

    @staticmethod
    def get_model_field_names(dict_):
        names = [
            key
            for key, value in dict_.iteritems()
            if isinstance(value, models.fields.Field)
        ]
        return names

    @staticmethod
    def get_parents_field_names(bases):
        names = []
        for base_class in reversed(bases):
            if hasattr(base_class, '_cls_meta'):
                names.extend(base_class._cls_meta.model_field_names)
        return names

    @classmethod
    def get_all_field_names(cls, bases, dict_):
        names = []
        names.extend(cls.get_parents_field_names(bases))
        names.extend(cls.get_model_field_names(dict_))
        return set(names)

    @classmethod
    def update_name_on_fields(cls, klass):
        for attr, value in klass.__dict__.iteritems():
            if isinstance(value, models.fields.Field):
                value.name = attr


class Model(object):
    __metaclass__ = FieldMcs

    _cls_meta = ClassMeta()
    _meta = None

    id = models.fields.IntegerField()

    def __init__(self, **kwargs):
        self._meta = InstanceMeta()

        for name, value in kwargs.iteritems():
            if name not in self._cls_meta.model_field_names:
                raise ValueError
            setattr(self, name, value)

    def __str__(self):
        mask = '<{}: {}>'
        return mask.format(self.__class__.__name__, self._meta.values)


class User(Model):
    firstname = models.fields.TextField(max_len=128)
    lastname = models.fields.TextField(max_len=128)
    bdate = models.fields.DateField(max_len=128)
    locality_id = models.fields.IntegerField()


class Locality(Model):
    city = models.fields.TextField(max_len=128)
    region = models.fields.TextField(max_len=128)
    country = models.fields.TextField(max_len=128)


class Race(Model):
    pass


class RaceConfig(Model):
    pass


class Checkpoint(Model):
    # a group of sensors

    # type: [start, finish, plain, cross]
    # registration: [required, optional, absent]
    pass


class RfidMark(Model):
    # it's possible to use multiple marks per user

    # type
    # size
    pass


class Emergency(Model):
    # object that represents context which we can't handle
    # requires human reaction
    pass


class CheckpointEmergency(Emergency):
    pass


class RaceEmergency(Emergency):
    pass
