from __future__ import absolute_import, unicode_literals
import abc
import threading
import six

if six.PY2:
    from .compat import Lock
else:
    from threading import Lock

from redis import Redis

from idempotency_key import utils


@six.add_metaclass(abc.ABCMeta)
class IdempotencyKeyLock:
    @abc.abstractmethod
    def acquire(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def release(self):
        raise NotImplementedError()


class ThreadLock(IdempotencyKeyLock):
    """
    Should be used only when there is one process sharing the storage class resource.
    This uses the built-in python threading module to protect a resource.
    """
    storage_lock = Lock()

    def acquire(self, *args, **kwargs):
        return self.storage_lock.acquire(blocking=True, timeout=utils.get_lock_timeout())

    def release(self):
        self.storage_lock.release()


class MultiProcessRedisLock(IdempotencyKeyLock):
    """
    Should be used if a lock is required across processes. Not that this class uses Redis in order to perform the lock.
    """

    def __init__(self):
        location = utils.get_lock_location()
        if location is None or location == '':
            raise ValueError('Redis server location must be set in the settings file.')

        self.redis_obj = Redis.from_url(location)
        self.storage_lock = self.redis_obj.lock(
            name=utils.get_lock_name(),
            timeout=utils.get_lock_time_to_live(),  # Time before lock is forcefully released.
            blocking_timeout=utils.get_lock_timeout(),
        )

    def acquire(self, *args, **kwargs):
        return self.storage_lock.acquire()

    def release(self):
        self.storage_lock.release()
