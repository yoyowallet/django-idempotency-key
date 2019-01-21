from functools import wraps

from django.core.cache import cache
from django.test import modify_settings, override_settings
from rest_framework import status

from tests.tests.utils import for_all_methods


def set_exempt_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(MIDDLEWARE={
            'remove': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
            'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
        }):
            return func(*args, **kwargs)

    return wrapper


@for_all_methods(set_exempt_middleware)
class TestMiddlewareExempt:
    the_key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'

    def test_get_exempt(self, client):
        """Basic GET method is exempt by default because it is a read-only function"""
        response = client.get('/views/get-voucher/', secure=True)
        assert response.status_code == status.HTTP_200_OK
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    def test_post_exempt(self, client):
        """Test a POST method that has been marked as exempt"""
        response = client.post('/views/create-voucher-exempt/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

        response = client.post('/views/create-voucher-exempt/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    def test_post_no_decorators(self, client):
        """Test a POST method that has been marked as exempt"""
        response = client.post('/views/create-voucher-no-decorators/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

        response = client.post('/views/create-voucher-no-decorators/', data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    def test_bad_request_no_key_specified(self, client):
        """
        POSTing to a view function that requires an idempotency key which is not specified in the header will cause a
        400 BAD REQUEST to be generated.
        """
        response = client.post('/views/create-voucher/', secure=True)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        request = response.wsgi_request
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False

    @override_settings(
        IDEMPOTENCY_KEY={}
    )
    def test_middleware_duplicate_request(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == 'b204f77b6555b66c71296426364f22f65ffde694152e1e5b17f8f024b33e2df3'

    @override_settings(
        IDEMPOTENCY_KEY={'CONFLICT_STATUS_CODE': None}
    )
    def test_middleware_duplicate_request_use_original_status_code(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_201_CREATED
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == 'b204f77b6555b66c71296426364f22f65ffde694152e1e5b17f8f024b33e2df3'

    @override_settings(
        IDEMPOTENCY_KEY={'CONFLICT_STATUS_CODE': status.HTTP_200_OK}
    )
    def test_middleware_duplicate_request_use_different_status_code(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_200_OK
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == 'b204f77b6555b66c71296426364f22f65ffde694152e1e5b17f8f024b33e2df3'

    def test_middleware_duplicate_request_manual_override(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher-manual/', voucher_data, secure=True,
                               HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher-manual/', voucher_data, secure=True,
                                HTTP_IDEMPOTENCY_KEY=self.the_key)

        # The view code forces a 200 OK to be returned if this is a repeated request.
        assert response2.status_code == status.HTTP_200_OK
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is True
        assert request.idempotency_key_encoded_key == '96cbe9a5f3e24c87f6cc8808b6cd2d91ecd2bf9b8e52fa4b34ad6b3d5626dabb'

    @override_settings(
        IDEMPOTENCY_KEY={
            'ENCODER_CLASS': 'tests.tests.test_middleware.MyEncoder'
        }
    )
    def test_middleware_custom_encoder(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == '0000000000000000000000000000000000000000000000000000000000000000'

    @override_settings(
        IDEMPOTENCY_KEY={
            'STORAGE_CLASS': 'tests.tests.test_middleware.MyStorage'
        }
    )
    def test_middleware_custom_storage(self, client):
        """
        In this test to prove the new custom storage class is being used by creating one that does not to store any
        information. Therefore a 409 conflict should never occur and the key will never exist.
        """
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_201_CREATED
        request = response2.wsgi_request
        assert request.idempotency_key_exists is False
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == 'b204f77b6555b66c71296426364f22f65ffde694152e1e5b17f8f024b33e2df3'

    def test_idempotency_key_decorator(self, client):
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True,
                               HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True,
                                HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == 'b204f77b6555b66c71296426364f22f65ffde694152e1e5b17f8f024b33e2df3'

    def test_idempotency_key_exempt_1(self, client):
        response = client.post('/views/create-voucher-exempt-test-1/', {}, secure=True,
                               HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    def test_idempotency_key_exempt_2(self, client):
        response = client.post('/views/create-voucher-exempt-test-2/', {}, secure=True,
                               HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert status.HTTP_201_CREATED == response.status_code
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    @override_settings(
        IDEMPOTENCY_KEY={
            'STORAGE_CLASS': 'idempotency_key.storage.CacheKeyStorage'
        }
    )
    @set_exempt_middleware
    def test_middleware_cache_storage(self, client):
        """
        Test Django cache storage
        """
        cache.clear()
        voucher_data = {
            'id': 1,
            'name': 'myvoucher0',
            'internal_name': 'myvoucher0',
        }

        response = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response.status_code == status.HTTP_201_CREATED

        response2 = client.post('/views/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=self.the_key)
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == 'b204f77b6555b66c71296426364f22f65ffde694152e1e5b17f8f024b33e2df3'
