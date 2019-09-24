from __future__ import unicode_literals
from django.test import override_settings
import pytest

from idempotency_key import locks


def test_single_thread_lock():
    obj = locks.ThreadLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


def test_multi_process_lock_only_host(settings):
    settings.IDEMPOTENCY_KEY = {
        'LOCK': {
            'LOCATION': 'Redis://localhost',
        }
    }
    obj = locks.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


def test_multi_process_lock_host_and_port(settings):
    settings.IDEMPOTENCY_KEY = {
        'LOCK': {
            'LOCATION': 'Redis://localhost:6379/1',
        }
    }
    obj = locks.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


def test_multi_process_lock_empty_string_must_be_set(settings):
    settings.IDEMPOTENCY_KEY = {
        'LOCK': {
            'LOCATION': '',
        }
    }
    with pytest.raises(ValueError):
        locks.MultiProcessRedisLock()


def test_multi_process_lock_null_must_be_set(settings):
    settings.IDEMPOTENCY_KEY = {
        'LOCK': {
            'LOCATION': None
        }
    }
    with pytest.raises(ValueError):
        locks.MultiProcessRedisLock()
