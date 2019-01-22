import abc
import pickle
from typing import Tuple

from django.core.cache import caches

from idempotency_key.middleware import _get_cache_name


class IdempotencyKeyStorage(object):

    @abc.abstractmethod
    def store_data(self, encoded_key: str, response: object) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        raise NotImplementedError


class MemoryKeyStorage(IdempotencyKeyStorage):

    def __init__(self):
        self.idempotency_key_cache_data = dict()

    def store_data(self, encoded_key: str, response: object) -> None:
        self.idempotency_key_cache_data[encoded_key] = response

    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        if encoded_key in self.idempotency_key_cache_data.keys():
            return True, self.idempotency_key_cache_data[encoded_key]

        return False, None


class CacheKeyStorage(IdempotencyKeyStorage):

    def __init__(self):
        self.cache_name = _get_cache_name()
        self.the_cache = caches[self.cache_name]

    def store_data(self, encoded_key: str, response: object) -> None:
        str_response = pickle.dumps(response)
        self.the_cache.set(encoded_key, str_response)

    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        if self.the_cache.__contains__(encoded_key):
            str_response = self.the_cache.get(encoded_key)
            return True, pickle.loads(str_response)

        return False, None
