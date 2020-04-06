from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from idempotency_key.decorators import (
    idempotency_key_exempt,
    idempotency_key,
    idempotency_key_manual,
)
from idempotency_key.utils import idempotency_key_exists


@api_view(["GET"])
def get(request, *args, **kwargs):
    return Response(
        status=200, data={"idempotency_key_exempt": request.idempotency_key_exempt}
    )


@api_view(["POST"])
def create_no_decorators(request, *args, **kwargs):
    return Response(
        status=201, data={"idempotency_key_exempt": request.idempotency_key_exempt}
    )


@idempotency_key_exempt
@api_view(["POST"])
def create_exempt(request, *args, **kwargs):
    return Response(
        status=201, data={"idempotency_key_exempt": request.idempotency_key_exempt}
    )


@idempotency_key
@api_view(["POST"])
def create(request, *args, **kwargs):
    return Response(status=201, data={})


@idempotency_key_manual
@api_view(["POST"])
def create_manual(request, *args, **kwargs):
    if idempotency_key_exists(request):
        response = request.idempotency_key_response
        response.status_code = status.HTTP_200_OK
        return response
    else:
        return Response(status=status.HTTP_201_CREATED, data={})


@idempotency_key_exempt
@idempotency_key
@api_view(["POST"])
def create_exempt_test_1(request, *args, **kwargs):
    return Response(status=201, data={})


@idempotency_key
@idempotency_key_exempt
@api_view(["POST"])
def create_exempt_test_2(request, *args, **kwargs):
    return Response(status=201, data={})


@idempotency_key_manual
@idempotency_key_exempt
@api_view(["POST"])
def create_manual_exempt_1(request, *args, **kwargs):
    return Response(status=201, data={})


@idempotency_key_exempt
@idempotency_key_manual
@api_view(["POST"])
def create_manual_exempt_2(request, *args, **kwargs):
    return Response(status=201, data={})


@idempotency_key(cache_name="FiveMinuteCache")
@api_view(["POST"])
def create_with_my_cache(request, *args, **kwargs):
    return Response(status=201, data={})
