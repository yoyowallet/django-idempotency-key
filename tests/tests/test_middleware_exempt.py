from functools import wraps

from django.test import modify_settings
from rest_framework import status


def set_exempt_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(MIDDLEWARE={
            'remove': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
            'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
        }):
            return func(*args, **kwargs)

    return wrapper


class TestMiddlewareExempt:

    @set_exempt_middleware
    def test_get_exempt(self, client):
        """Basic GET method is exempt by default because it is a read-only function"""
        response = client.get('/get-voucher/', secure=True)
        assert response.status_code == status.HTTP_200_OK
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    @set_exempt_middleware
    def test_post_exempt(self, client):
        """Test a POST method that has been marked as exempt"""
        response = client.post('/create-voucher-exempt/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

        response = client.post('/create-voucher-exempt/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    @set_exempt_middleware
    def test_post_exempt_no_decorators(self, client):
        """Test a POST method that has been marked as exempt"""
        response = client.post('/create-voucher-no-decorators/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

        response = client.post('/create-voucher-no-decorators/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False


    @set_exempt_middleware
    def test_bad_request_no_key_specified(self, client):
        """
        POSTing to a view function that requires an idempotency key which is not specified in the header will cause a
        400 BAD REQUEST to be generated.
        """
        response = client.post('/create-voucher/', secure=True)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        request = response.wsgi_request
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False

    @set_exempt_middleware
    def test_middleware_duplicate_request(self, client, settings):
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
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'

    @set_exempt_middleware
    def test_middleware_duplicate_request_use_original_status_code(self, client, settings):
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
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'

    @set_exempt_middleware
    def test_middleware_duplicate_request_use_different_status_code(self, client, settings):
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
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'

    @set_exempt_middleware
    def test_middleware_duplicate_request_manual_override(self, client):
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
        assert request.idempotency_key_manual is True
        assert request.idempotency_key_encoded_key == '32841060cc2b1c721d9e6b9fdf1f9e17b54eaf63b8a407a330fd831dc487b4c9'

    @set_exempt_middleware
    def test_middleware_custom_encoder(self, client, settings):
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
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '0000000000000000000000000000000000000000000000000000000000000000'

    @set_exempt_middleware
    def test_middleware_custom_storage(self, client, settings):
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
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'

    @set_exempt_middleware
    def test_idempotency_key_decorator(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
        response = client.post('/create-voucher-use-idempotency-key/', voucher_data, secure=True,
                               HTTP_IDEMPOTENCY_KEY=key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/create-voucher-use-idempotency-key/', voucher_data, secure=True,
                                HTTP_IDEMPOTENCY_KEY=key)
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '0860e61d26b0b9fbc170e80a97ab2f934f3d437b5a58d8af8d1e99e44c180558'

    @set_exempt_middleware
    def test_idempotency_key_exempt_1(self, client):
        key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
        response = client.post('/create-voucher-exempt-test-1/', {}, secure=True, HTTP_IDEMPOTENCY_KEY=key)
        assert status.HTTP_201_CREATED == response.status_code
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    @set_exempt_middleware
    def test_idempotency_key_exempt_2(self, client):
        key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
        response = client.post('/create-voucher-exempt-test-2/', {}, secure=True, HTTP_IDEMPOTENCY_KEY=key)
        assert status.HTTP_201_CREATED == response.status_code
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False
