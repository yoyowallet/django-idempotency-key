from django.test import override_settings

from idempotency_key import locks


def test_single_thread_lock():
    obj = locks.ThreadLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


@override_settings(
    IDEMPOTENCY_KEY={
        'LOCK': {
            'LOCATION': 'localhost',
        }
    }
)
def test_multi_process_lock_only_host():
    obj = locks.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


@override_settings(
    IDEMPOTENCY_KEY={
        'LOCK': {
            'LOCATION': 'localhost:6379',
        }
    }
)
def test_multi_process_lock_host_and_port():
    obj = locks.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()
