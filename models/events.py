import models


class Event(models.base.Model):
    # event on sensor
    pass


class RfidEvent(Event):
    pass


class PhotoEvent(Event):
    pass


class VideoEvent(Event):
    pass
