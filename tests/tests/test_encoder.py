import pytest
from django.test.client import RequestFactory

from idempotency_key.encoders import BasicKeyEncoder
from idempotency_key.exceptions import MissingIdempotencyKeyError


def test_basic_encoding():
    request = RequestFactory().post(
        "/myURL/path/", {"key": "value"}, "application/json"
    )
    obj = BasicKeyEncoder()
    enc_key = obj.encode_key(request, "MyKey")
    assert enc_key == "da44e9b4dd5bc8e7853a43c8e8f2d2c2de4394f6614ab37dd5507b6f5988aac4"


def test_basic_encoder_null_key():
    request = RequestFactory().post(
        "/myURL/path/", {"key": "value"}, "application/json"
    )
    obj = BasicKeyEncoder()
    with pytest.raises(MissingIdempotencyKeyError) as e_info:
        obj.encode_key(request, None)
    assert e_info.value.args[0] == "Idempotency key cannot be None."


def test_basic_encoder_uses_authorization_header():
    request1 = RequestFactory().post(
        "/myURL/path/",
        {"key": "value"},
        "application/json",
        HTTP_AUTHORIZATION="Bearer 123",
    )
    request2 = RequestFactory().post(
        "/myURL/path/",
        {"key": "value"},
        "application/json",
        HTTP_AUTHORIZATION="Bearer 321",
    )

    encoder = BasicKeyEncoder()
    key1 = encoder.encode_key(request1, "test-idempotency-key")
    key2 = encoder.encode_key(request2, "test-idempotency-key")
    assert key1 != key2
