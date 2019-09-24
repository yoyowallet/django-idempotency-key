from __future__ import absolute_import, unicode_literals

from django.http import JsonResponse

from idempotency_key import status


class MissingIdempotencyKeyError(Exception):

    def __init__(self, msg=None):
        if msg is None:
            msg = 'Idempotency key cannot be None.'
        super(MissingIdempotencyKeyError, self).__init__(msg)

    """
    Raised when an idempotency key has not been specified
    """
    pass


class DecoratorsMutuallyExclusiveError(Exception):
    pass


def bad_request(request, exception, *args, **kwargs):
    """
    Generic 400 error handler.
    """
    data = {
        'error': 'Bad Request (400)'
    }
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def resource_locked(request, exception, *args, **kwargs):
    """
    Generic 423 error handler.
    """
    data = {
        'error': 'Resource Locked (423)'
    }
    return JsonResponse(data, status=status.HTTP_423_LOCKED)
