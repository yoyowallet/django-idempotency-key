import pytest
from django.test import override_settings

from idempotency_key.locks import basic, redis


def test_single_thread_lock():
    obj = basic.ThreadLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"LOCATION": "redis://localhost"}})
def test_multi_process_lock_only_host():
    obj = redis.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"LOCATION": "redis://localhost:6379/1"}})
def test_multi_process_lock_host_and_port():
    obj = redis.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"LOCATION": ""}})
def test_multi_process_lock_empty_string_must_be_set():
    with pytest.raises(ValueError):
        redis.MultiProcessRedisLock()


@override_settings(IDEMPOTENCY_KEY={"LOCK": {"LOCATION": None}})
def test_multi_process_lock_null_must_be_set():
    with pytest.raises(ValueError):
        redis.MultiProcessRedisLock()
