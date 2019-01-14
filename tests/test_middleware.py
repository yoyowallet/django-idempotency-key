import uuid

from rest_framework import status


def test_middleware_duplicate_request(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = str(uuid.uuid4())
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_409_CONFLICT == response2.status_code
    # key_exists is set to false here because the code should return the original response to us and not a new one
    # that would have key_exists set to True
    assert response2.data['key_exists'] is False


def test_middleware_duplicate_request_manual_override(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = str(uuid.uuid4())
    response = client.post('/create-voucher-manual/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher-manual/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)

    # The view code forces a 200 OK to be returned if this is a repeated request.
    assert status.HTTP_200_OK == response2.status_code
    # key_exists should be true here because the decorator code allows the view function to be called when the same
    # request is made due to manual override.
    assert response2.data['key_exists'] is True
