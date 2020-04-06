from django.test import override_settings

from idempotency_key import status
from idempotency_key import storage
from idempotency_key import utils


class Request(object):
    pass


class Response(object):
    pass


def test_idempotency_key_exists_none():
    request = Request()
    assert utils.idempotency_key_exists(request) is False


def test_idempotency_key_exists_false():
    request = Request()
    request.idempotency_key_exists = False
    assert utils.idempotency_key_exists(request) is False


def test_idempotency_key_exists_true():
    request = Request()
    request.idempotency_key_exists = True
    assert utils.idempotency_key_exists(request) is True


def test_idempotency_key_response_none():
    request = Request()
    assert utils.idempotency_key_response(request) is None


def test_idempotency_key_response_object():
    request = Request()
    response = Response()
    request.idempotency_key_response = response
    assert utils.idempotency_key_response(request) is response


@override_settings(
    IDEMPOTENCY_KEY={"STORAGE": {"STORE_ON_STATUSES": [status.HTTP_200_OK]}}
)
def test_get_store_on_statuses_default():
    assert utils.get_storage_store_on_statuses() == [status.HTTP_200_OK]


@override_settings(IDEMPOTENCY_KEY={})
def test_get_store_on_statuses_not_specified():
    assert utils.get_storage_store_on_statuses() == [
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
        status.HTTP_202_ACCEPTED,
        status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        status.HTTP_204_NO_CONTENT,
        status.HTTP_205_RESET_CONTENT,
        status.HTTP_206_PARTIAL_CONTENT,
        status.HTTP_207_MULTI_STATUS,
    ]


@override_settings(IDEMPOTENCY_KEY={})
def test_get_lock_class_default():
    assert utils.get_lock_class() is storage.MemoryKeyStorage


@override_settings(
    IDEMPOTENCY_KEY={"LOCK": {"CLASS": "idempotency_key.storage.CacheKeyStorage"}}
)
def test_get_lock_class_default():
    assert utils.get_lock_class() is storage.CacheKeyStorage


@override_settings(IDEMPOTENCY_KEY={})
def test_get_lock_timeout_default():
    assert utils.get_lock_timeout() == 0.1


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"TIMEOUT": 1.8}})
def test_get_lock_timeout_default():
    assert utils.get_lock_timeout() == 1.8


@override_settings(IDEMPOTENCY_KEY={})
def test_get_lock_enable_default():
    assert utils.get_lock_enable() is True


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"ENABLE": False}})
def test_get_lock_enable_default():
    assert utils.get_lock_enable() is False


@override_settings(IDEMPOTENCY_KEY={})
def test_get_lock_ttl_default():
    assert utils.get_lock_time_to_live() is None


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"TTL": 1}})
def test_get_lock_ttl_default():
    assert utils.get_lock_time_to_live() == 1


@override_settings(IDEMPOTENCY_KEY={})
def test_get_lock_name_default():
    assert utils.get_lock_name() is "MyLock"


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"NAME": "testname"}})
def test_get_lock_name_default():
    assert utils.get_lock_name() == "testname"


def test_get_lock_location_default():
    location = utils.get_lock_location()
    assert location == "Redis://localhost:6379/1"


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"LOCATION": "testname"}})
def test_get_lock_location_only_host():
    location = utils.get_lock_location()
    assert location == "testname"


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"LOCATION": "testname:1234"}})
def test_get_lock_location_host_and_port():
    location = utils.get_lock_location()
    assert location == "testname:1234"
