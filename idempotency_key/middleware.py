from django.conf import settings
from django.urls import get_callable
from rest_framework import status
from rest_framework.exceptions import bad_request


def _get_storage_class():
    return get_callable(getattr(settings, 'IDEMPOTENCY_KEY_STORAGE_CLASS', 'idempotency_key.storage.MemoryKeyStorage'))


def _get_encoder_class():
    return get_callable(getattr(settings, 'IDEMPOTENCY_KEY_ENCODER_CLASS)', 'idempotency_key.encoders.BasicKeyEncoder'))


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

    def process_request(self, request):
        key = request.META.get('HTTP_IDEMPOTENCY_KEY')
        if key is not None:
            request.META['IDEMPOTENCY_KEY'] = key

    def process_view(self, request, callback, callback_args, callback_kwargs):

        # Assume that anything defined as 'safe' by RFC7231 is exempt or if exempt is specified directly
        if getattr(callback, 'idempotency_key_exempt', False) or request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            request.idempotency_key_exempt = True
            return None

        request.idempotency_key_exempt = False

        key = request.META.get('IDEMPOTENCY_KEY')
        if key is None:
            return bad_request(request, None)

        # Has the manual override decorator been specified? if so add it to the request
        manual = getattr(callback, 'use_idempotency_key_manual_override', False)
        if manual:
            request.use_idempotency_key_manual_override = True

        # encode the key and add it to the request
        encoded_key = request.idempotency_key_encoded_key = self.encoder.encode_key(request, key)

        # Check if a response already exists for the encoded key
        key_exists, response = self.storage.retrieve_data(encoded_key)

        # add the key exists result and the original request if it exists
        request.idempotency_key_exists = key_exists
        request.idempotency_key_response = response

        # If not manual override and the key already exists then return the original response as a 409 CONFLICT
        if not manual and key_exists:
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
