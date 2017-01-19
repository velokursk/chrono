class ModelError(Exception):
    pass


class PrimaryKeyError(ModelError):
    pass


class MoreThanOneError(ModelError):
    pass


class UnknownParameterError(ModelError):
    pass
