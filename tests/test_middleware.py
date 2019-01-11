import uuid

from rest_framework.status import HTTP_201_CREATED
from rest_framework.test import APIRequestFactory

from tests import views


def test_middleware_no_action():
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    # Create a JSON POST request
    factory = APIRequestFactory()
    request = factory.post('/create-voucher/', voucher_data, format='json')
    response = views.create_voucher(request)
    assert HTTP_201_CREATED == response.status_code


def test_middleware_duplicate_request(client):
    voucher_data = {
        'id': 1,
        'name': 'myvoucher0',
        'internal_name': 'myvoucher0',
    }

    # Create a JSON POST request
    factory = APIRequestFactory()
    key = str(uuid.uuid4())
    request1 = factory.post('/create-voucher/', voucher_data, format='json', HTTP_IDEMPOTENCY_KEY=key)
    response1 = views.create_voucher(request1)

    request2 = factory.post('/create-voucher/', voucher_data, format='json', HTTP_IDEMPOTENCY_KEY=key)
    response2 = views.create_voucher(request2)

    assert HTTP_201_CREATED == response2.status_code

