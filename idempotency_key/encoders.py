import abc
import hashlib

from idempotency_key.exceptions import MissingIdempotencyKeyError


class IdempotencyKeyEncoder(object):
    @abc.abstractmethod
    def encode_key(self, request, key):
        raise NotImplementedError


class BasicKeyEncoder(IdempotencyKeyEncoder):
    def encode_key(self, request, key):
        if key is None:
            raise MissingIdempotencyKeyError()
        # Basic method for generating an encoded key
        m = hashlib.sha256()
        m.update(key.encode("UTF-8"))
        m.update(request.path_info.encode("UTF-8"))
        m.update(request.method.encode("UTF-8"))
        m.update(request.body)
        return m.hexdigest()
