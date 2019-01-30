import abc
import threading

from idempotency_key.utils import get_lock_timeout


class IdempotencyKeyLock(object):
    @abc.abstractmethod
    def acquire(self, *args, **kwargs) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def release(self):
        raise NotImplementedError()


class ThreadLock(IdempotencyKeyLock):
    """
    Should be used only when there is one process sharing the storage class resource.
    This uses the built-in python threading module to protect a resource.
    """
    storage_lock = threading.Lock()

    def acquire(self, *args, **kwargs) -> bool:
        return self.storage_lock.acquire(blocking=True, timeout=get_lock_timeout())

    def release(self):
        self.storage_lock.release()
