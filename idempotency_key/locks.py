import abc
import threading

from redis import StrictRedis

from idempotency_key import utils
from idempotency_key.utils import get_lock_timeout


class IdempotencyKeyLock(abc.ABC):
    @abc.abstractmethod
    def acquire(self, *args, **kwargs) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def release(self):
        raise NotImplementedError()


class SingleProcessLock(IdempotencyKeyLock):
    """
    Should be used only when there is one process sharing the storage class resource.
    This uses the built-in python threading module to protect a resource.
    """
    storage_lock = threading.Lock()

    def acquire(self, *args, **kwargs) -> bool:
        return self.storage_lock.acquire(blocking=True, timeout=get_lock_timeout())

    def release(self):
        self.storage_lock.release()


class MultiProcessLock(IdempotencyKeyLock):
    """
    Should be used if a lock is required across processes. Not that this class uses Redis in order to perform the lock.
    """
    storage_lock = StrictRedis().lock(
        name=utils.get_lock_name(),
        timeout=utils.get_lock_time_to_live(),  # Time before lock is forcefully released.
        blocking_timeout=get_lock_timeout(),
    )

    def acquire(self, *args, **kwargs) -> bool:
        return self.storage_lock.acquire()

    def release(self):
        self.storage_lock.release()
