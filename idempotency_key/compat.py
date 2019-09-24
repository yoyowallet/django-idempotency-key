from __future__ import unicode_literals
import threading
import time


class Lock(object):
    _lock_class = threading.Lock

    def __init__(self):
        self._lock = self._lock_class()
        self._cond = threading.Condition(threading.Lock())

    def acquire(self, blocking=True, timeout=-1):
        if not blocking or timeout == 0:
            return self._lock.acquire(False)
        cond = self._cond
        lock = self._lock
        if timeout < 0:
            with cond:
                while True:
                    if lock.acquire(False):
                        return True
                    else:
                        cond.wait()
        else:
            with cond:
                current_time = time.time()
                stop_time = current_time + timeout
                while current_time < stop_time:
                    if lock.acquire(False):
                        return True
                    else:
                        cond.wait(stop_time - current_time)
                        current_time = time.time()
                return False

    def release(self):
        with self._cond:
            self._lock.release()
            self._cond.notify()

    __enter__ = acquire

    def __exit__(self, t, v, tb):
        self.release()


class RLock(Lock):
    _lock_class = threading.RLock
