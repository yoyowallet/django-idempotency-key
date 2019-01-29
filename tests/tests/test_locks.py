from idempotency_key import locks


def test_single_thread_lock():
    obj = locks.SingleProcessLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()


def test_multi_process_lock():
    obj = locks.MultiProcessLock()
    assert obj.acquire() is True
    assert obj.acquire() is False
    obj.release()
    assert obj.acquire() is True
    obj.release()
