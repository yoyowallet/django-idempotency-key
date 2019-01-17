import abc
import pickle
from typing import Tuple

from django.core.cache import cache


class IdempotencyKeyStorage(object):

    @abc.abstractmethod
    def store_data(self, encoded_key: str, response: object) -> None:
        pass

    @abc.abstractmethod
    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        pass


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

    def store_data(self, encoded_key: str, response: object) -> None:
        str_response = pickle.dumps(response)
        cache.set(encoded_key, str_response)

    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        if cache.__contains__(encoded_key):
            str_response = cache.get(encoded_key)
            return True, pickle.loads(str_response)

        return False, None
