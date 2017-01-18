import models.fields
import models.errors


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
        'field_names': list,  # list of all field names for current model
        'primary_field': str,
        'unique': bool,
    }


class InstanceMeta(ModelMeta):
    _fields = {
        'values': dict,
    }


class ModelCreationHandler(object):
    def __init__(self, context):
        self.context = context
        # name, bases, dict_
        # model_field_names, parent_field_names, field_names

    def run_before(self):
        return self.context

    def run_after(self):
        return self.context


class FieldsHandler(ModelCreationHandler):
    def run_before(self):
        self.context['model_field_names'] = self._get_model_field_names(self.context['dict_'])
        self.context['parent_field_names'] = self._get_parents_field_names(self.context['bases'])
        all_names = []
        all_names.extend(self.context['parent_field_names'])
        all_names.extend(self.context['model_field_names'])
        self.context['field_names'] = list(set(all_names))
        return self.context

    def run_after(self):
        self.context['klass']._cls_meta.field_names = self.context['field_names']
        for attr, value in self.context['klass'].__dict__.iteritems():
            if isinstance(value, models.fields.Field):
                value.name = attr
        return self.context

    @staticmethod
    def _get_model_field_names(dict_):
        names = [
            key
            for key, value in dict_.iteritems()
            if isinstance(value, models.fields.Field)
        ]
        return names

    @staticmethod
    def _get_parents_field_names(bases):
        names = []
        for base_class in reversed(bases):
            if hasattr(base_class, '_cls_meta'):
                names.extend(base_class._cls_meta.field_names)
        return names


class PrimaryHandler(ModelCreationHandler):
    # we should have one and only one primary key
    def run_after(self):
        # set primary_key
        pk_name = self._get_pk_name()
        self.context['klass']._cls_meta['primary_field'] = pk_name

    def _get_pk_name(self):
        pk_names = []
        pk_names.extend(self.__get_pk_names_from_parents())
        pk_names.extend(self.__get_pk_names_from_model_fields())
        if len(set(pk_names)) != 1:
            raise models.errors.PrimaryKeyError
        return pk_names[0]

    def __get_pk_names_from_parents(self):
        names = []
        for base_class in reversed(self.context['bases']):
            for attr, value in base_class.__dict__.iteritems():
                if isinstance(value, models.fields.Field) and value.primary:
                    names.append(attr)
        return names

    def __get_pk_names_from_model_fields(self):
        names = []
        for attr, value in self.context['klass'].__dict__.iteritems():
            if isinstance(value, models.fields.Field) and value.primary:
                names.append(attr)
        return names


class FieldMcs(type):
    # we don't support field names with leading underscore

    def __new__(mcs, name, bases, dict_):
        context = {
            'name': name,
            'bases': bases,
            'dict_': dict_,
        }
        prepared_context = mcs.prepare_context(context)
        klass = super(FieldMcs, mcs).__new__(mcs, name, bases, dict_)
        prepared_klass = mcs.customize_class(klass, prepared_context)
        return prepared_klass

    @staticmethod
    def prepare_context(context):
        handlers = [
            FieldsHandler,  # this one should be the first
        ]
        for handler in handlers:
            context = handler(context).run_before()
        return context

    @staticmethod
    def customize_class(klass, context):
        context['klass'] = klass
        handlers = [
            FieldsHandler,  # this one should be the first
            PrimaryHandler,
        ]
        for handler in handlers:
            context = handler(context).run_after()
        return context['klass']

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
            if name not in self._cls_meta.field_names:
                raise ValueError
            setattr(self, name, value)

    def __str__(self):
        mask = '<{}: {}>'
        return mask.format(self.__class__.__name__, self._meta.values)

    @property
    def pk(self):
        pk_name = self._cls_meta['primary_field']
        return getattr(self, pk_name)


class User(Model):
    firstname = models.fields.TextField(max_len=128)
    lastname = models.fields.TextField(max_len=128)
    bdate = models.fields.DateField()
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
