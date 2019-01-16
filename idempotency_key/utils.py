def idempotency_key_exists(request):
    return getattr(request, 'idempotency_key_exists', False)


def idempotency_key_response(request):
    return getattr(request, 'idempotency_key_response', None)
