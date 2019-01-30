import abc
import threading

from redis import Redis

from idempotency_key import utils


class IdempotencyKeyLock(abc.ABC):
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
        return self.storage_lock.acquire(blocking=True, timeout=utils.get_lock_timeout())

    def release(self):
        self.storage_lock.release()


class MultiProcessRedisLock(IdempotencyKeyLock):
    """
    Should be used if a lock is required across processes. Not that this class uses Redis in order to perform the lock.
    """

    def __init__(self):
        host, port = utils.get_lock_location()
        self.redis_obj = Redis(host=host, port=port, )
        self.storage_lock = self.redis_obj.lock(
            name=utils.get_lock_name(),
            timeout=utils.get_lock_time_to_live(),  # Time before lock is forcefully released.
            blocking_timeout=utils.get_lock_timeout(),
        )

    def acquire(self, *args, **kwargs) -> bool:
        return self.storage_lock.acquire()

    def release(self):
        self.storage_lock.release()
