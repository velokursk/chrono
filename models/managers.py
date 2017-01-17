class Manager(object):
    def __init__(self):
        pass

    def __get__(self, instance, klass):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def __del__(self, instance):
        raise NotImplementedError

    def create(self):
        pass

    def drop(self, model):
        pass

    def filter(self):
        pass

    def get(self):
        pass

    def save(self, model):
        pass
