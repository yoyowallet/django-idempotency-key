from functools import wraps
from typing import Tuple

import pytest
from django.core.cache import InvalidCacheBackendError, cache, caches
from django.test import modify_settings, override_settings

from idempotency_key import status
from idempotency_key.encoders import BasicKeyEncoder, IdempotencyKeyEncoder
from idempotency_key.exceptions import DecoratorsMutuallyExclusiveError
from idempotency_key.storage import IdempotencyKeyStorage
from tests.tests.utils import for_all_methods


def set_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(
            MIDDLEWARE={
                "append": ["idempotency_key.middleware.IdempotencyKeyMiddleware"],
                "remove": ["idempotency_key.middleware.ExemptIdempotencyKeyMiddleware"],
            }
        ):
            return func(*args, **kwargs)

    return wrapper


class MyEncoder(IdempotencyKeyEncoder):
    def encode_key(self, request, key):
        return "0000000000000000000000000000000000000000000000000000000000000000"


class MyStorage(IdempotencyKeyStorage):
    def __init__(self):
        self.idempotency_key_cache_data = dict()

    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        pass

    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        return False, None


@for_all_methods(set_middleware)
class TestMiddlewareInclusive:
    the_key = "7495e32b-709b-4fae-bfd4-2497094bf3fd"
    urls = {
        name: "/viewsets/{}/".format(name)
        for name in [
            "get",
            "create",
            "create-optional",
            "create-exempt",
            "create-no-decorators",
            "create-manual",
            "create-exempt-test-1",
            "create-exempt-test-2",
            "create-manual-exempt-1",
            "create-manual-exempt-2",
            "create-nested-decorator",
            "create-nested-decorator-exempt",
            "create-with-my-cache",
        ]
    }

    def test_get_exempt(self, client):
        """Basic GET method is exempt by default because it is a read-only function"""
        response = client.get(self.urls["get"], secure=True)
        assert response.status_code == status.HTTP_200_OK
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    def test_post_exempt(self, client):
        """Test a POST method that has been marked as exempt"""
        response = client.post(self.urls["create-exempt"], data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

        response = client.post(self.urls["create-exempt"], data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False

    def test_post_no_decorators(self, client):
        response = client.post(
            self.urls["create-no-decorators"],
            data={},
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False

        response = client.post(
            self.urls["create-no-decorators"],
            data={},
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        request = response.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    def test_post_optional(self, client):
        response = client.post(self.urls["create-optional"], data={}, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        request = response.wsgi_request
        assert request.idempotency_key_optional is True
        assert request.idempotency_key_exempt is True

    def test_bad_request_no_key_specified(self, client):
        """
        POSTing to a view function that requires an idempotency key which is not
        specified in the header will cause a 400 BAD REQUEST to be generated.
        """
        response = client.post(self.urls["create"], secure=True)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        request = response.wsgi_request
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False

    @override_settings(IDEMPOTENCY_KEY={})
    def test_middleware_duplicate_request(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    @override_settings(IDEMPOTENCY_KEY={"CONFLICT_STATUS_CODE": None})
    def test_middleware_duplicate_request_use_original_status_code(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_201_CREATED
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    @override_settings(IDEMPOTENCY_KEY={"CONFLICT_STATUS_CODE": status.HTTP_200_OK})
    def test_middleware_duplicate_request_use_different_status_code(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_200_OK
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    def test_middleware_duplicate_request_manual_override(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create-manual"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create-manual"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )

        # The view code forces a 200 OK to be returned if this is a repeated request.
        assert response2.status_code == status.HTTP_200_OK
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is True
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    @override_settings(
        IDEMPOTENCY_KEY={"ENCODER_CLASS": "tests.tests.test_middleware.MyEncoder"}
    )
    def test_middleware_custom_encoder(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert (
            request.idempotency_key_encoded_key
            == "0000000000000000000000000000000000000000000000000000000000000000"
        )

    @override_settings(
        IDEMPOTENCY_KEY={"STORAGE": {"CLASS": "tests.tests.test_middleware.MyStorage"}}
    )
    def test_middleware_custom_storage(self, client):
        """
        In this test to prove the new custom storage class is being used by creating
        one that does not to store any information. Therefore a 409 conflict should
        never occur and the key will never exist.
        """
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_201_CREATED
        request = response2.wsgi_request
        assert request.idempotency_key_exists is False
        assert request.idempotency_key_response is None
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    def test_idempotency_key_decorator(self, client):
        voucher_data = {
            "id": 1,
            "name": "myvoucher0",
            "internal_namtests/testse": "myvoucher0",
        }

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    def test_idempotency_key_exempt_mutually_exclusive_1(self, client):
        with pytest.raises(DecoratorsMutuallyExclusiveError):
            client.post(
                self.urls["create-exempt-test-1"],
                {},
                secure=True,
                HTTP_IDEMPOTENCY_KEY=self.the_key,
            )
            pass

    def test_idempotency_key_exempt_mutually_exclusive_2(self, client):
        with pytest.raises(DecoratorsMutuallyExclusiveError):
            client.post(
                self.urls["create-exempt-test-2"],
                {},
                secure=True,
                HTTP_IDEMPOTENCY_KEY=self.the_key,
            )

    def test_manual_exempt_mutually_exclusive_1(self, client):
        with pytest.raises(DecoratorsMutuallyExclusiveError):
            client.post(
                self.urls["create-manual-exempt-1"],
                {},
                secure=True,
                HTTP_IDEMPOTENCY_KEY=self.the_key,
            )
            pass

    def test_manual_exempt_mutually_exclusive_2(self, client):
        with pytest.raises(DecoratorsMutuallyExclusiveError):
            client.post(
                self.urls["create-manual-exempt-2"],
                {},
                secure=True,
                HTTP_IDEMPOTENCY_KEY=self.the_key,
            )

    @override_settings(
        IDEMPOTENCY_KEY={"STORAGE_CLASS": "idempotency_key.storage.CacheKeyStorage"}
    )
    @set_middleware
    def test_middleware_cache_storage(self, client):
        """
        Test Django cache storage
        """
        cache.clear()
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response2
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    def test_nested_decorator(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}
        response = client.post(
            self.urls["create-nested-decorator"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED
        response2 = client.post(
            self.urls["create-nested-decorator"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response2
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    def test_nested_decorator_exempt(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}
        response = client.post(
            self.urls["create-nested-decorator-exempt"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED
        response2 = client.post(
            self.urls["create-nested-decorator-exempt"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_201_CREATED
        request = response2.wsgi_request
        assert hasattr(request, "idempotency_key_exists") is False
        assert hasattr(request, "idempotency_key_response") is False
        assert request.idempotency_key_exempt is True
        assert request.idempotency_key_manual is False
        assert hasattr(request, "idempotency_key_encoded_key") is False

    @override_settings(
        IDEMPOTENCY_KEY={
            "STORAGE": {"STORE_ON_STATUSES": [status.HTTP_207_MULTI_STATUS]}
        }
    )
    def test_store_on_statuses_does_not_store(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_201_CREATED
        request = response2.wsgi_request
        assert request.idempotency_key_exists is False
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    @override_settings(
        IDEMPOTENCY_KEY={"STORAGE": {"STORE_ON_STATUSES": [status.HTTP_201_CREATED]}}
    )
    def test_store_on_statuses_does_store(self, client):
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )

    @override_settings(
        IDEMPOTENCY_KEY={
            "STORAGE": {
                "CLASS": "idempotency_key.storage.CacheKeyStorage",
                "CACHE_NAME": "FiveMinuteCache",
            }
        },
        CACHES={},
    )
    def test_middleware_invalid_cache_name(self, client):
        """
        Tests @idempotency_key(cache_name='FiveMinuteCache') decorator where the cache
        name has not been configured under settings.CACHE
        """
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        with pytest.raises(InvalidCacheBackendError):
            client.post(
                self.urls["create-with-my-cache"],
                voucher_data,
                secure=True,
                HTTP_IDEMPOTENCY_KEY=self.the_key,
            )

    @override_settings(
        IDEMPOTENCY_KEY={
            "STORAGE": {
                "CLASS": "idempotency_key.storage.CacheKeyStorage",
                # This should be overridden by the decorator:
                "CACHE_NAME": "SevenDayCache",
            }
        }
    )
    def test_middleware_cache_storage_using_custom_cache_name_on_decorator(
        self, client
    ):
        """
        Tests @idempotency_key(cache_name='FiveMinuteCache') decorator
        """
        caches["default"].clear()
        caches["FiveMinuteCache"].clear()
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create-with-my-cache"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert status.HTTP_201_CREATED == response.status_code

        response2 = client.post(
            self.urls["create-with-my-cache"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response2
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )
        assert request.idempotency_key_cache_name == "FiveMinuteCache"

    @override_settings(
        IDEMPOTENCY_KEY={
            "STORAGE": {
                "CLASS": "idempotency_key.storage.CacheKeyStorage",
                # This should be overridden by the decorator:
                "CACHE_NAME": "FiveMinuteCache",
            }
        }
    )
    def test_middleware_storage_cache_name_provides_default_name(self, client):
        """
        Tests @idempotency_key(cache_name='FiveMinuteCache') decorator
        """
        caches["FiveMinuteCache"].clear()
        voucher_data = {"id": 1, "name": "myvoucher0", "internal_name": "myvoucher0"}

        response = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response.status_code == status.HTTP_201_CREATED

        response2 = client.post(
            self.urls["create"],
            voucher_data,
            secure=True,
            HTTP_IDEMPOTENCY_KEY=self.the_key,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        request = response2.wsgi_request
        assert request.idempotency_key_exists is True
        assert request.idempotency_key_response == response2
        assert request.idempotency_key_exempt is False
        assert request.idempotency_key_manual is False
        assert request.idempotency_key_encoded_key == BasicKeyEncoder().encode_key(
            request, self.the_key
        )
        assert request.idempotency_key_cache_name == "FiveMinuteCache"
