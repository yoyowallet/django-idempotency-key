import abc
from collections import defaultdict
import time
from typing import Tuple

from django.core.cache import caches
from django.http.response import HttpResponse


class CachedHttpResponse:
    def __init__(self, value: object):
        self._response = value
        self._mtime = time.time()

    @property
    def response_and_mtime(self):
        return self._response, self._mtime

    @response_and_mtime.setter
    def response_and_mtime(self, value: object):
        if not isinstance(value, HttpResponse):
            raise ValueError("The value must be an instance of HttpResponse")
        self._response = value
        self._mtime = time.time()


class IdempotencyKeyStorage(object):
    @abc.abstractmethod
    def __init__(self, ttl: int):
        """
        Create a new store.
        :param ttl: The maximum number of seconds that the store will retain incomplete entries
        """
        raise NotImplementedError

    @abc.abstractmethod
    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        """
        Store date to the store using the specified key.
        :param cache_name: The name of the cache to use defined in settings under CACHES
        :param encoded_key: the key used to store the response data under
        :param response: The response data to store
        :return: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        """
        Retrieve data from the store using the specified key.
        :param cache_name: The name of the cache to use defined in settings under CACHES
        :param encoded_key: The key that was used to store the response data
        :return: the response data
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_data(self, cache_name: str, encoded_key: str) -> None:
        """
        Delete data from the store using the specified key.
        :param cache_name: The name of the cache to use defined in settings under CACHES
        :param encoded_key: The key that was used to store the response data
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def validate_storage(name: str):
        """
        Validate that the storage name exists. If the class is using django `CACHES`
        setting then this function ensures that the cache is setup correctly in the
        settings file and will cause a failure at startup if it is not.
        This function should raise an exception if the storage name cannot be validated.
        :param name: The name of the storage.
        """
        raise NotImplementedError


class MemoryKeyStorage(IdempotencyKeyStorage):
    def __init__(self, ttl: int):
        self.ttl = ttl
        self.idempotency_key_cache_data = defaultdict(dict)

    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        cached_response = CachedHttpResponse(response)
        self.idempotency_key_cache_data[cache_name][encoded_key] = cached_response

    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        the_cache = self.idempotency_key_cache_data[cache_name]
        if the_cache is None or encoded_key not in the_cache:
            return False, None

        response, mtime = the_cache[encoded_key].response_and_mtime
        if response is None and mtime + self.ttl < time.time():
            # Incomplete value expired, delete it and pretend that it was never here.
            del the_cache[encoded_key]
            return False, None

        return True, response

    def delete_data(self, cache_name: str, encoded_key: str) -> None:
        the_cache = self.idempotency_key_cache_data[cache_name]

        if the_cache and encoded_key in the_cache:
            del the_cache[encoded_key]

    @staticmethod
    def validate_storage(name: str):
        pass


class CacheKeyStorage(IdempotencyKeyStorage):
    def __init__(self, ttl: int):
        self.ttl = ttl

    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        cached_response = CachedHttpResponse(response)
        caches[cache_name].set(encoded_key, cached_response)

    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        if encoded_key not in caches[cache_name]:
            return False, None

        response, mtime = caches[cache_name].get(encoded_key).response_and_mtime
        if response is None and mtime + self.ttl < time.time():
            # Incomplete value expired, delete it and pretend that it was never here.
            caches[cache_name].delete(encoded_key)
            return False, None

        return True, response

    def delete_data(self, cache_name: str, encoded_key: str):
        if encoded_key in caches[cache_name]:
            caches[cache_name].delete(encoded_key)

    @staticmethod
    def validate_storage(name: str):
        # Check that the cache exists. If the cache is not found then an
        # InvalidCacheBackendError is raised. Note that there is no get function on the
        # caches object, so we cannot perform a normal check.
        caches[name]
