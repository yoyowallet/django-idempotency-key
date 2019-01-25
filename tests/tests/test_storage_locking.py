from idempotency_key import status
from idempotency_key.middleware import IdempotencyKeyMiddleware


def test_storage_when_locked_returns_423():
    class Request:
        idempotency_key_manual = False
        pass

    request = Request()
    obj = IdempotencyKeyMiddleware()
    lock = obj.storage_lock.acquire(blocking=True, timeout=-1)
    assert lock is True

    response = obj.generate_response(request, 'mykey', lock=True)
    assert response.status_code == status.HTTP_423_LOCKED
    obj.storage_lock.release()

    # Now that the lock is open, running the function again should return None because no key will exist in the cache
    response = obj.generate_response(request, 'mykey', lock=True)
    assert response is None
