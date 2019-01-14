import uuid

from rest_framework import status


def test_get_exempt(client):
    """Basic GET method is exempt by default because it is a read-only function"""
    response = client.get('/get-voucher/', secure=True)
    assert response.status_code == status.HTTP_200_OK
    request = response.wsgi_request
    assert request.idempotency_key_exempt is True


def test_post_exempt(client):
    """Test a POST method that has been marked as exempt"""
    response = client.post('/create-voucher-exempt/', data={}, secure=True)
    assert response.status_code == status.HTTP_201_CREATED
    request = response.wsgi_request
    assert request.idempotency_key_exempt is True


def test_bad_request_no_key_specified(client):
    """
    POSTing to a view function that requires an idempotency key which is not specified in the header will cause a
    400 BAD REQUEST to be generated.
    """
    response = client.post('/create-voucher/', secure=True)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    request = response.wsgi_request
    assert request.idempotency_key_exempt is False


def test_middleware_duplicate_request(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert response2.status_code == status.HTTP_409_CONFLICT
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '562be6fe17ab443a60b287e022b42c40d57f74432e6c41f0fd0035558209d22e'


def test_middleware_duplicate_request_manual_override(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    key = '7495e32b-709b-4fae-bfd4-2497094bf3fd'
    response = client.post('/create-voucher-manual/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)
    assert status.HTTP_201_CREATED == response.status_code

    response2 = client.post('/create-voucher-manual/', voucher_data, secure=True, HTTP_IDEMPOTENCY_KEY=key)

    # The view code forces a 200 OK to be returned if this is a repeated request.
    assert response2.status_code == status.HTTP_200_OK
    request = response2.wsgi_request
    assert request.idempotency_key_exists is True
    assert request.idempotency_key_exempt is False
    assert request.idempotency_key_encoded_key == '32841060cc2b1c721d9e6b9fdf1f9e17b54eaf63b8a407a330fd831dc487b4c9'
