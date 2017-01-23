import datetime

import orm.model
import orm.field


class User(orm.model.Model):
    firstname = orm.field.TextField(max_len=128)
    lastname = orm.field.TextField(max_len=128)
    bdate = orm.field.DateField(default=datetime.datetime.now())
    locality_id = orm.field.IntegerField(default=0)


class Locality(orm.model.Model):
    city = orm.field.TextField(max_len=128)
    region = orm.field.TextField(max_len=128)
    country = orm.field.TextField(max_len=128)


class Race(orm.model.Model):
    pass


class RaceConfig(orm.model.Model):
    pass


class Checkpoint(orm.model.Model):
    # a group of sensors

    # type: [start, finish, plain, cross]
    # registration: [required, optional, absent]
    pass


class RfidMark(orm.model.Model):
    # it's possible to use multiple marks per user

    # type
    # size
    pass


class Emergency(orm.model.Model):
    # object that represents context which we can't handle
    # requires human reaction
    pass
