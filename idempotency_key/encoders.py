import abc
import hashlib
import json


class IdempotencyKeyEncoder(object):
    @abc.abstractmethod
    def encode_key(self, request, key):
        pass


class BasicKeyEncoder(IdempotencyKeyEncoder):
    def encode_key(self, request, key):
        # Basic method for generating an encoded key
        m = hashlib.sha256()
        m.update(key.encode('UTF-8'))
        m.update(request.path_info.encode('UTF-8'))
        m.update(request.method.encode('UTF-8'))
        m.update(json.dumps(request.POST).encode('UTF-8'))
        return m.hexdigest()
