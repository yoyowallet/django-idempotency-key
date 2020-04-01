from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from idempotency_key.decorators import idempotency_key_exempt, idempotency_key, idempotency_key_manual
from idempotency_key.utils import idempotency_key_exists


class MyViewSet(ViewSet):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        return Response(status=200, data={'idempotency_key_exempt': request.idempotency_key_exempt})

    def create_no_decorators(self, request, *args, **kwargs):
        return Response(status=201, data={'idempotency_key_exempt': request.idempotency_key_exempt})

    @idempotency_key_exempt
    def create_exempt(self, request, *args, **kwargs):
        return Response(status=201, data={'idempotency_key_exempt': request.idempotency_key_exempt})

    @idempotency_key
    def create(self, request, *args, **kwargs):
        return Response(status=201, data={})

    @idempotency_key(optional=True)
    def create_optional(self, request, *args, **kwargs):
        return Response(status=201, data={})

    @idempotency_key_manual
    def create_manual(self, request, *args, **kwargs):
        if idempotency_key_exists(request):
            response = request.idempotency_key_response
            response.status_code = status.HTTP_200_OK
            return response
        else:
            return Response(status=status.HTTP_201_CREATED, data={})

    @idempotency_key_exempt
    @idempotency_key
    def create_exempt_test_1(self, request, *args, **kwargs):
        return Response(status=201, data={})

    @idempotency_key
    @idempotency_key_exempt
    def create_exempt_test_2(self, request, *args, **kwargs):
        return Response(status=201, data={})

    @idempotency_key_manual
    @idempotency_key_exempt
    def create_manual_exempt_1(self, request, *args, **kwargs):
        return Response(status=201, data={})

    @idempotency_key_exempt
    @idempotency_key_manual
    def create_manual_exempt_2(self, request, *args, **kwargs):
        return Response(status=201, data={})

    @idempotency_key(cache_name='FiveMinuteCache')
    def create_with_my_cache(self, request, *args, **kwargs):
        return Response(status=201, data={})


class MyModelViewSet(ViewSet):
    def create(self, request, *args, **kwargs):
        return Response(status=201, data={})


class MyMixin(MyModelViewSet):
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ViewSetBase(MyModelViewSet):
    @idempotency_key
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# NOTE: the base classes must be specified in the correct order where the decorators appear in the first base class
# or they will not be detected by the middleware.
class MyViewSet2(ViewSetBase, MyMixin):
    pass


class ViewSetBaseExempt(MyModelViewSet):
    @idempotency_key_exempt
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# NOTE: the base classes must be specified in the correct order where the decorators appear in the first base class
# or they will not be detected by the middleware.
class MyViewSet2Exempt(ViewSetBaseExempt, MyMixin):
    pass
