from rest_framework.decorators import api_view
from rest_framework.response import Response

from idempotency_key.decorators import use_idempotency_key


@api_view(['POST'])
@use_idempotency_key
def create_voucher(request, *args, **kwargs):
    return Response(status=201, data={'key1': 'value1', 'key2': 'value2'})


@api_view(['POST'])
@use_idempotency_key(manual_override=True)
def create_voucher_manual(request, *args, **kwargs):
    return Response(status=201, data={'key1': 'value1', 'key2': 'value2'})
