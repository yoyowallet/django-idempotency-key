from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from idempotency_key.decorators import idempotency_key_exempt, use_idempotency_key_manual_override


@api_view(['GET'])
def get_voucher(request, *args, **kwargs):
    return Response(status=200, data={'idempotency_key_exempt': request.idempotency_key_exempt})


@idempotency_key_exempt
@api_view(['POST'])
def create_voucher_exempt(request, *args, **kwargs):
    return Response(status=201, data={'idempotency_key_exempt': request.idempotency_key_exempt})


@api_view(['POST'])
def create_voucher_bad_request(request, *args, **kwargs):
    return Response(status=200, data={})


@api_view(['POST'])
def create_voucher(request, *args, **kwargs):
    return Response(status=201, data={})


@use_idempotency_key_manual_override
@api_view(['POST'])
def create_voucher_manual(request, *args, **kwargs):
    if request.idempotency_key_exists:
        response = request.idempotency_key_response
        response.status_code = status.HTTP_200_OK
        return response
    else:
        return Response(status=status.HTTP_201_CREATED, data={})
