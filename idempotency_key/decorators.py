from rest_framework import status
from rest_framework.exceptions import ValidationError

from idempotency_key.encoders import BasicKeyEncoder, IdempotencyKeyEncoder
from idempotency_key.storage import MemoryKeyStorage, IdempotencyKeyStorage

_registry = dict()


def idempotency_key_required(func, encoder=BasicKeyEncoder, storage=MemoryKeyStorage):
    if not issubclass(encoder, IdempotencyKeyEncoder):
        raise ValidationError('Invalid encoder type. Expected a type derived from IdempotencyKeyEncoder.')

    if not issubclass(storage, IdempotencyKeyStorage):
        raise ValidationError('Invalid storage type. Expected a type derived from IdempotencyKeyStorage.')

    encoder_obj = encoder()
    storage_obj = storage()

    def wrapper1(request, *args, **kwargs):

        key = request.META.get('HTTP_IDEMPOTENCY_KEY')
        # If the key
        if key is None:
            raise ValidationError('Idempotency key missing in header.')

        encoded_key = encoder_obj.encode_key(request, key)

        # try to retrieve the data
        key_exists, response = storage_obj.retrieve_data(encoded_key)

        # If we have seen this key before then return the same response
        if key_exists:
            return response

        response = func(request, *args, **kwargs)

        # If we are returning a 2XX status code then store the result and return the response
        if status.HTTP_200_OK <= response.status_code <= status.HTTP_207_MULTI_STATUS:
            storage_obj.store_data(encoded_key, response)
        return response

    _registry['idempotency_key_required'] = True
    return wrapper1


def idempotency_key_manual_override(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    _registry['idempotency_key_manual_override'] = True
    return wrapper
