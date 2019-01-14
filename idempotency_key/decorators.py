from functools import wraps

from rest_framework import status
from rest_framework.exceptions import ValidationError

from idempotency_key.encoders import BasicKeyEncoder, IdempotencyKeyEncoder
from idempotency_key.storage import MemoryKeyStorage, IdempotencyKeyStorage


def _check_and_get_objects(encoder, storage):
    if not issubclass(encoder, IdempotencyKeyEncoder):
        raise ValidationError('Invalid encoder type. Expected a type derived from IdempotencyKeyEncoder.')

    if not issubclass(storage, IdempotencyKeyStorage):
        raise ValidationError('Invalid storage type. Expected a type derived from IdempotencyKeyStorage.')

    return encoder(), storage()


def get_key_from_header(request):
    key = request.META.get('HTTP_IDEMPOTENCY_KEY')
    # If the key
    if key is None:
        raise ValidationError('Idempotency key missing in header.')
    return key


def use_idempotency_key(*args, encoder=BasicKeyEncoder, storage=MemoryKeyStorage, manual_override=False):
    # Create instances of the encode and storage classes specific to the callback function
    encoder_obj, storage_obj = _check_and_get_objects(encoder, storage)

    def _idempotency_key_required(func):

        @wraps(func)
        def wrapper(request, *args, **kwargs):
            key = get_key_from_header(request)

            # Encode the key to ensure it is unique
            encoded_key = encoder_obj.encode_key(request, key)

            # try to retrieve the data
            key_exists, response = storage_obj.retrieve_data(encoded_key)

            # If the view does not want to concern itself with idempotency-key checking and we have seen this key
            # before then return the same response.
            if not manual_override and key_exists:
                response.status_code = status.HTTP_409_CONFLICT
                return response

            # Call the original function
            response = func(
                request=request,
                key_exists=key_exists,
                encoded_key=encoded_key,
                response=response,
                *args,
                **kwargs
            )

            # If we are returning a 2XX status code then store the result and return the response
            if status.HTTP_200_OK <= response.status_code <= status.HTTP_207_MULTI_STATUS:
                storage_obj.store_data(encoded_key, response)
            return response

        return wrapper

    # Depending on how the decorator is used args[0] may contain the callback function
    # i.e:
    # @idempotency_key_required                            len(args) == 1, args[0] is function to be wrapped
    # @idempotency_key_required(encoder=BasicKeyEncoder)   len(args) == 0
    if len(args) == 1 and callable(args[0]):
        return _idempotency_key_required(args[0])
    else:
        return _idempotency_key_required
