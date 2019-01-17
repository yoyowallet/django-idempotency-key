import abc
from typing import Tuple


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
