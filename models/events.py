import models


class Event(models.base.Model):
    # event on sensor

    # ts
    # duration
    # sensor_id
    pass


class RfidEvent(Event):
    # mark_id
    pass


class PhotoEvent(Event):
    # photo_id
    pass


class VideoEvent(Event):
    # video_id
    pass
