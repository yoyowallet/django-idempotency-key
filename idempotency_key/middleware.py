import logging

from django.conf import settings
from django.urls import get_callable
from rest_framework import status
from rest_framework.exceptions import bad_request

logger = logging.getLogger('django-idempotency-key.idempotency_key.middleware')


def _get_storage_class():
    return get_callable(getattr(settings, 'IDEMPOTENCY_KEY_STORAGE_CLASS', 'idempotency_key.storage.MemoryKeyStorage'))


def _get_encoder_class():
    return get_callable(getattr(settings, 'IDEMPOTENCY_KEY_ENCODER_CLASS', 'idempotency_key.encoders.BasicKeyEncoder'))


def _get_conflict_code():
    return getattr(settings, 'IDEMPOTENCY_KEY_CONFLICT_STATUS_CODE', status.HTTP_409_CONFLICT)


class IdempotencyKeyMiddleware:

    def __init__(self, get_response=None):
        self.get_response = get_response
        self.storage = _get_storage_class()()
        self.encoder = _get_encoder_class()()

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        response = self.process_response(request, response)
        return response

    @staticmethod
    def _is_exempt(request, default=False):
        return getattr(request, 'idempotency_key_exempt', default)

    @staticmethod
    def _is_manual(request, default=False):
        return getattr(request, 'idempotency_key_manual', default)

    @staticmethod
    def _use_key(request, default=True):
        return getattr(request, 'idempotency_key', default)

    @staticmethod
    def _reject(request, reason):
        response = bad_request(request, None)
        logger.error(
            'Error (%s): %s', reason, request.path,
            extra={
                'status_code': 400,
                'request': request,
            }
        )
        return response

    def _set_flags_from_callback(self, request, callback):
        request.idempotency_key_exempt = getattr(callback, 'idempotency_key_exempt', False)
        request.idempotency_key_manual = getattr(callback, 'idempotency_key_manual', False)

    def process_request(self, request):
        key = request.META.get('HTTP_IDEMPOTENCY_KEY')
        if key is not None:
            request.META['IDEMPOTENCY_KEY'] = key

    def process_view(self, request, callback, callback_args, callback_kwargs):
        self._set_flags_from_callback(request, callback)

        # Assume that anything defined as 'safe' by RFC7231 is exempt or if exempt is specified directly
        if self._is_exempt(request) or request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            request.idempotency_key_exempt = True
            return None

        request.idempotency_key_exempt = False

        key = request.META.get('IDEMPOTENCY_KEY')
        if key is None:
            return self._reject(request, 'Idempotency key is required and was not specified in the header.')

        # Has the manual override decorator been specified? if so add it to the request
        manual_override = self._is_manual(request)
        if manual_override:
            request.use_idempotency_key_manual_override = True

        # encode the key and add it to the request
        encoded_key = request.idempotency_key_encoded_key = self.encoder.encode_key(request, key)

        # Check if a response already exists for the encoded key
        key_exists, response = self.storage.retrieve_data(encoded_key)

        # add the key exists result and the original request if it exists
        request.idempotency_key_exists = key_exists
        request.idempotency_key_response = response

        # If not manual override and the key already exists then return the original response as a 409 CONFLICT
        if not manual_override and key_exists:
            status_code = _get_conflict_code()
            if status_code is not None:
                response.status_code = status_code
            return response

        return None

    def process_response(self, request, response):
        if request.idempotency_key_exempt:
            return response

        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            # If the response is 2XX then store the response
            if status.HTTP_200_OK <= response.status_code <= status.HTTP_207_MULTI_STATUS:
                self.storage.store_data(request.idempotency_key_encoded_key, response)

        return response


class ExemptIdempotencyKeyMiddleware(IdempotencyKeyMiddleware):
    """
    This middleware class assume all requests are exempt unless the @idempotency_key_exempt or @idempotency_key
    decorators are specified.
    """

    def _set_flags_from_callback(self, request, callback):
        try:
            idempotency_key = getattr(callback, 'idempotency_key')
        except AttributeError:
            idempotency_key = None

        try:
            idempotency_key_exempt = getattr(callback, 'idempotency_key_exempt')
        except AttributeError:
            idempotency_key_exempt = None

        try:
            idempotency_key_manual = getattr(callback, 'idempotency_key_manual')
        except AttributeError:
            idempotency_key_manual = None

        request.idempotency_key_exempt = idempotency_key_exempt or (
                idempotency_key_exempt is None and idempotency_key_manual is None and not idempotency_key
        )

        request.idempotency_key_manual = idempotency_key_manual

    def process_view(self, request, callback, callback_args, callback_kwargs):
        self._set_flags_from_callback(request, callback)

        # Assume that anything defined as 'safe' by RFC7231 is exempt or if exempt is specified directly
        if self._is_exempt(request) or request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            request.idempotency_key_exempt = True
            return None

        request.idempotency_key_exempt = False

        key = request.META.get('IDEMPOTENCY_KEY')
        if key is None:
            return self._reject(request, 'Idempotency key is required and was not specified in the header.')

        # Has the manual override decorator been specified? if so add it to the request
        if request.idempotency_key_manual:
            request.use_idempotency_key_manual_override = True

        # encode the key and add it to the request
        encoded_key = request.idempotency_key_encoded_key = self.encoder.encode_key(request, key)

        # Check if a response already exists for the encoded key
        key_exists, response = self.storage.retrieve_data(encoded_key)

        # add the key exists result and the original request if it exists
        request.idempotency_key_exists = key_exists
        request.idempotency_key_response = response

        # If not manual override and the key already exists then return the original response as a 409 CONFLICT
        if not request.idempotency_key_manual and key_exists:
            status_code = _get_conflict_code()
            if status_code is not None:
                response.status_code = status_code
            return response

        return None
