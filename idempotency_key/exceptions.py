class MissingIdempotencyKeyError(Exception):

    def __init__(self, msg=None):
        if msg is None:
            msg = 'Idempotency key cannot be None.'
        super().__init__(msg)

    """
    Raised when an idempotency key has not been specified
    """
    pass


class DecoratorsMutuallyExclusiveError(Exception):
    pass
