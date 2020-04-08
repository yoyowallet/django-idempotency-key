import json

import pytest

from idempotency_key.encoders import BasicKeyEncoder
from idempotency_key.exceptions import MissingIdempotencyKeyError


def test_basic_encoding():
    class Request:
        path_info = "/myURL/path/"
        method = "POST"
        body = json.dumps({"key": "value"}).encode("UTF-8")

    request = Request()
    obj = BasicKeyEncoder()
    enc_key = obj.encode_key(request, "MyKey")
    assert enc_key == "da44e9b4dd5bc8e7853a43c8e8f2d2c2de4394f6614ab37dd5507b6f5988aac4"


def test_basic_encoder_null_key():
    class Request:
        path_info = "/myURL/path/"
        method = "POST"
        body = json.dumps({"key": "value"}).encode("UTF-8")

    request = Request()
    obj = BasicKeyEncoder()
    with pytest.raises(MissingIdempotencyKeyError) as e_info:
        obj.encode_key(request, None)
    assert e_info.value.args[0] == "Idempotency key cannot be None."
