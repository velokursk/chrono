class User(object):
    pass


class Race(object):
    pass


class RaceConfig(object):
    pass


class Checkpoint(object):
    # a group of sensors
    pass


class RfidMark(object):
    # it's possible to ise multiple marks per user
    pass


class Emergency(object):
    # object that represents context which we can't handle
    # requires human reaction
    pass


class CheckpointEmergency(Emergency):
    pass


class RaceEmergency(Emergency):
    pass
