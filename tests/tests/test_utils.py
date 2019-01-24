from django.test import override_settings

from idempotency_key import status
from idempotency_key.utils import idempotency_key_exists, idempotency_key_response, get_store_on_statuses


class Request(object):
    pass


class Response(object):
    pass


def test_idempotency_key_exists_none():
    request = Request()
    assert idempotency_key_exists(request) is False


def test_idempotency_key_exists_false():
    request = Request()
    request.idempotency_key_exists = False
    assert idempotency_key_exists(request) is False


def test_idempotency_key_exists_true():
    request = Request()
    request.idempotency_key_exists = True
    assert idempotency_key_exists(request) is True


def test_idempotency_key_response_none():
    request = Request()
    assert idempotency_key_response(request) is None


def test_idempotency_key_response_object():
    request = Request()
    response = Response()
    request.idempotency_key_response = response
    assert idempotency_key_response(request) is response


@override_settings(
    IDEMPOTENCY_KEY={
        'STORE_ON_STATUSES': [status.HTTP_200_OK]
    }
)
def test_get_store_on_statuses_default():
    assert get_store_on_statuses() == [
        status.HTTP_200_OK
    ]


@override_settings(
    IDEMPOTENCY_KEY={}
)
def test_get_store_on_statuses_not_specified():
    assert get_store_on_statuses() == [
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
        status.HTTP_202_ACCEPTED,
        status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        status.HTTP_204_NO_CONTENT,
        status.HTTP_205_RESET_CONTENT,
        status.HTTP_206_PARTIAL_CONTENT,
        status.HTTP_207_MULTI_STATUS,
    ]
