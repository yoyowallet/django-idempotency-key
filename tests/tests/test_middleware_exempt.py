from typing import Tuple

from django.test import modify_settings
from rest_framework import status

from idempotency_key.encoders import IdempotencyKeyEncoder
from idempotency_key.storage import IdempotencyKeyStorage


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_get_exempt(client):
    """Basic GET method is exempt by default because it is a read-only function"""
    response = client.get('/get-voucher/', secure=True)
    assert response.status_code == status.HTTP_200_OK
    request = response.wsgi_request
    assert request.idempotency_key_exempt is True


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_post_exempt(client):
    """Test a POST method that has been marked as exempt"""
    response = client.post('/create-voucher-exempt/', data={}, secure=True)
    assert response.status_code == status.HTTP_201_CREATED
    request = response.wsgi_request
    assert request.idempotency_key_exempt is True


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_bad_request_no_key_specified(client):
    """
    POSTing to a view function that requires an idempotency key which is not specified in the header will cause a
    400 BAD REQUEST to be generated.
    """
    response = client.post('/create-voucher/', secure=True)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    request = response.wsgi_request
    assert request.idempotency_key_exempt is False


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_middleware_duplicate_request(client, settings):
    del settings.IDEMPOTENCY_KEY_CONFLICT_STATUS_CODE
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_409_CONFLICT
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_middleware_duplicate_request_use_original_status_code(client, settings):
    settings.IDEMPOTENCY_KEY_CONFLICT_STATUS_CODE = None
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_201_CREATED
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_middleware_duplicate_request_use_different_status_code(client, settings):
    settings.IDEMPOTENCY_KEY_CONFLICT_STATUS_CODE = status.HTTP_200_OK
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_200_OK
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_middleware_duplicate_request_manual_override(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    print(f'Call POST')
    response = client.post('/create-voucher-manual/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    print(f'Call POST')
    response2 = client.post('/create-voucher-manual/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)

    # The view code forces a 200 OK to be returned if this is a repeated request.
    assert response2.status_code == status.HTTP_200_OK
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '32841060cc2b1c721d9e6b9fdf1f9e17b54eaf63b8a407a330fd831dc487b4c9'


class MyEncoder(IdempotencyKeyEncoder):
    def encode_key(self, request, key):
        return '0000000000000000000000000000000000000000000000000000000000000000'


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_middleware_custom_encoder(client, settings):
    settings.IDEMPOTENCY_KEY_ENCODER_CLASS = 'tests.tests.test_middleware.MyEncoder'
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_409_CONFLICT
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '0000000000000000000000000000000000000000000000000000000000000000'


class MyStorage(IdempotencyKeyStorage):

    def __init__(self):
        self.idempotency_key_cache_data = dict()

    def store_data(self, encoded_key: str, response: object) -> None:
        pass

    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        return False, None


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_middleware_custom_storage(client, settings):
    """
    In this test to prove the new custom storage class is being used by creating one that does not to store any
    information. Therefore a 409 conflict should never occur and the key will never exist.
    """
    settings.IDEMPOTENCY_KEY_STORAGE_CLASS = 'tests.tests.test_middleware.MyStorage'
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_201_CREATED
    request = response2.wsgi_request
    assert request.idempotency_key_exists is False
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
})
def test_idempotency_key_decorator(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher-use-idempotency-key/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher-use-idempotency-key/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_409_CONFLICT
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '0860e61d26b0b9fbc170e80a97ab2f934f3d437b5a58d8af8d1e99e44c180558'


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
})
def test_idempotency_key_exempt_1(client):
    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher-exempt-test-1/', {}, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code
    request = response.wsgi_request
    assert request.idempotency_key_exempt is True


@modify_settings(MIDDLEWARE={
    'append': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
})
def test_idempotency_key_exempt_2(client):
    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher-exempt-test-2/', {}, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code
    request = response.wsgi_request
    assert request.idempotency_key_exempt is True