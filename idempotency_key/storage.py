import abc
import pickle
from typing import Tuple

from django.core.cache import caches

from idempotency_key import status
from idempotency_key.utils import get_cache_name


class IdempotencyKeyStorage(object):

    @abc.abstractmethod
    def store_data(self, encoded_key: str, response: object) -> None:
        """
        called when data should be stored in the storage medium
        :param encoded_key: the key used to store the response data under
        :param response: The response data to store
        :return: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        """
        Retrieve data from the sore using the specified key.
        :param encoded_key: The key that was used to store the response data
        :return: the response data
        """
        raise NotImplementedError

    def store_on_statuses(self):
        """
        returns a list of statuses in which the data should be stored. Override this function to change.
        :return: list of status codes
        """
        return [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_205_RESET_CONTENT,
            status.HTTP_206_PARTIAL_CONTENT,
            status.HTTP_207_MULTI_STATUS,
        ]


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
        self.cache_name = get_cache_name()
        self.the_cache = caches[self.cache_name]

    def store_data(self, encoded_key: str, response: object) -> None:
        str_response = pickle.dumps(response)
        self.the_cache.set(encoded_key, str_response)

    def retrieve_data(self, encoded_key: str) -> Tuple[bool, object]:
        if encoded_key in self.the_cache:
            str_response = self.the_cache.get(encoded_key)
            return True, pickle.loads(str_response)

        return False, None
