from rest_framework.decorators import api_view
from rest_framework.response import Response

from idempotency_key.decorators import use_idempotency_key


@api_view(['POST'])
@use_idempotency_key
def create_voucher(request, key_exists, encoded_key, response, *args, **kwargs):
    return Response(
        status=201,
        data={'key_exists': key_exists, 'encoded_key': encoded_key, 'response': str(response)}
    )


@api_view(['POST'])
@use_idempotency_key(manual_override=True)
def create_voucher_manual(request, key_exists, encoded_key, response, *args, **kwargs):
    if key_exists:
        return Response(
            status=200,
            data={'key_exists': key_exists, 'encoded_key': encoded_key, 'response': str(response)}
        )
    else:
        return Response(
            status=201,
            data={'key_exists': key_exists, 'encoded_key': encoded_key, 'response': str(response)}
        )
