from rest_framework.decorators import api_view
from rest_framework.response import Response

from idempotency_key.decorators import idempotency_key_required, idempotency_key_manual_override


@api_view(['POST'])
@idempotency_key_manual_override
@idempotency_key_required
def create_voucher(request, *args, **kwargs):
    return Response(status=201, data={'key1': 'value1', 'key2': 'value2'})

@api_view(['POST'])
@idempotency_key_required
@idempotency_key_manual_override
def create_voucher_2(request, *args, **kwargs):
    return Response(status=201, data={'key1': 'value1', 'key2': 'value2'})


@api_view(['GET'])
@idempotency_key_required
def get_voucher(request, *args, **kwargs):
    return Response(status=201, data={'key1': 'value1', 'key2': 'value2'})
