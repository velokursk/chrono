class ModelError(Exception):
    pass


class PrimaryKeyError(ModelError):
    pass


class MoreThanOneError(ModelError):
    pass


class UnknownParameterError(ModelError):
    pass


class FieldNotUniqueError(ModelError):
    pass


class DoesNotExistError(ModelError):
    pass
