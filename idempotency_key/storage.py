import abc
import pickle
from typing import Tuple

from django.core.cache import caches


class IdempotencyKeyStorage(object):

    @abc.abstractmethod
    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        """
        called when data should be stored in the storage medium
        :param cache_name: The name of the cache to use defined in settings under CACHES
        :param encoded_key: the key used to store the response data under
        :param response: The response data to store
        :return: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        """
        Retrieve data from the sore using the specified key.
        :param cache_name: The name of the cache to use defined in settings under CACHES
        :param encoded_key: The key that was used to store the response data
        :return: the response data
        """
        raise NotImplementedError


class MemoryKeyStorage(IdempotencyKeyStorage):

    def __init__(self):
        self.idempotency_key_cache_data = dict()

    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        if self.idempotency_key_cache_data.get(cache_name) is None:
            self.idempotency_key_cache_data[cache_name] = dict()

        self.idempotency_key_cache_data[cache_name][encoded_key] = response

    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        the_cache = self.idempotency_key_cache_data.get(cache_name)
        if the_cache is None:
            return False, None

        if encoded_key in the_cache.keys():
            return True, the_cache[encoded_key]

        return False, None


class CacheKeyStorage(IdempotencyKeyStorage):

    def store_data(self, cache_name: str, encoded_key: str, response: object) -> None:
        str_response = pickle.dumps(response)
        caches[cache_name].set(encoded_key, str_response)

    def retrieve_data(self, cache_name: str, encoded_key: str) -> Tuple[bool, object]:
        if encoded_key in caches[cache_name]:
            str_response = caches[cache_name].get(encoded_key)
            return True, pickle.loads(str_response)

        return False, None
