from idempotency_key.utils import idempotency_key_exists, idempotency_key_response


class Request(object):
    pass


class Response(object):
    pass


def test_idempotency_key_exists_none():
    request = Request()
    assert idempotency_key_exists(request) is False


def test_idempotency_key_exists_false():
    request = Request()
    request.idempotency_key_exists = False
    assert idempotency_key_exists(request) is False


def test_idempotency_key_exists_true():
    request = Request()
    request.idempotency_key_exists = True
    assert idempotency_key_exists(request) is True


def test_idempotency_key_response_none():
    request = Request()
    assert idempotency_key_response(request) is None


def test_idempotency_key_response_object():
    request = Request()
    response = Response()
    request.idempotency_key_response = response
    assert idempotency_key_response(request) is response
