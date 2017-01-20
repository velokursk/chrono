import datetime

import models.errors
import models.fields
import models.managers


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
        'unique_fields': list,
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


class ClsMetaHandler(ModelCreationHandler):
    def run_before(self):
        self.context['dict_']['_cls_meta'] = ClassMeta()
        return self.context


class FieldsHandler(ModelCreationHandler):
    def run_before(self):
        self.context['parents_field_names'] = self.parents_field_names
        self.context['model_field_names'] = self.model_field_names
        self.context['field_names'] = self.field_names
        return self.context

    def run_after(self):
        self.context['klass']._cls_meta.field_names = self.context['field_names']
        self.context['klass']._cls_meta.unique_fields = self._get_fields_with_setting('unique', True)
        self._set_name_for_fields()
        return self.context

    @property  # before
    def model_field_names(self):
        if 'model_field_names' in self.context:
            return self.context['model_field_names']
        names = [
            key
            for key, value in self.context['dict_'].iteritems()
            if isinstance(value, models.fields.Field)
        ]
        self.context['model_field_names'] = names
        return names

    @property  # before
    def parents_field_names(self):
        if 'parents_field_names' in self.context:
            return self.context['parents_field_names']
        names = []
        for base_class in reversed(self.context['bases']):
            if hasattr(base_class, '_cls_meta'):
                names.extend(base_class._cls_meta.field_names)
        self.context['parents_field_names'] = names
        return names

    @property  # before and after
    def field_names(self):
        if 'klas' in self.context:
            all_names = self.context['klass']._cls_meta.field_names
            if all_names:
                return all_names
        if 'field_names' in self.context:
            return self.context['field_names']
        all_names = []
        all_names.extend(self.parents_field_names)
        all_names.extend(self.model_field_names)
        self.context['field_names'] = list(set(all_names))
        return self.context['field_names']

    def _set_name_for_fields(self):
        for attr, value in self.context['klass'].__dict__.iteritems():
            if isinstance(value, models.fields.Field):
                value.name = attr

    def _get_fields_with_setting(self, setting_name, setting_value):
        result = []
        for field_name in self.field_names:
            field_descriptor = getattr(self.context['klass'], field_name)
            if hasattr(field_descriptor, setting_name):
                if getattr(field_descriptor, setting_name) == setting_value:
                    result.append(field_name)
        return result


class PrimaryHandler(ModelCreationHandler):
    # we should have one and only one primary key
    def run_after(self):
        # set primary_key
        pk_name = self._get_pk_name()
        self.context['klass']._cls_meta.primary_field = pk_name
        return self.context

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
                if isinstance(value, models.fields.Field):
                    if value.primary:
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
            ClsMetaHandler,
            FieldsHandler,
        ]
        for handler in handlers:
            context = handler(context).run_before()
        return context

    @staticmethod
    def customize_class(klass, context):
        context['klass'] = klass
        handlers = [
            FieldsHandler,
            PrimaryHandler,
        ]
        for handler in handlers:
            context = handler(context).run_after()
        return context['klass']


class Model(object):
    __metaclass__ = FieldMcs

    _meta = None
    objects = models.managers.ModelManager()

    id = models.fields.IntegerField(primary=True)

    def __init__(self, **kwargs):
        self._meta = InstanceMeta()

        self.__check_for_unknown_params(kwargs)
        self.__check_for_initial_values(kwargs)

        self._meta.values.update(kwargs)

    def __str__(self):
        mask = '<{}: {}>'
        return mask.format(self.__class__.__name__, self._meta.values)

    def __check_for_unknown_params(self, kwargs):
        for name, value in kwargs.iteritems():
            if name not in self._cls_meta.field_names:
                raise models.errors.UnknownParameterError

    def __check_for_initial_values(self, kwargs):
        fields_wo_initial_value = [
            k
            for k in self._cls_meta.field_names
            if k not in kwargs
        ]
        if not all([getattr(self.__class__, name).has_default for name in fields_wo_initial_value]):
            raise models.errors.ModelError

    @property
    def pk(self):
        pk_name = self._cls_meta.primary_field
        return getattr(self, pk_name)

    def save(self):
        return self.objects.save(self)


class User(Model):
    firstname = models.fields.TextField(max_len=128)
    lastname = models.fields.TextField(max_len=128)
    bdate = models.fields.DateField(default=datetime.datetime.now())
    locality_id = models.fields.IntegerField(default=0)


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
