from idempotency_key import locks


def test_single_thread_lock():
    obj = locks.ThreadLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


def test_multi_process_lock():
    obj = locks.MultiProcessRedisLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()
