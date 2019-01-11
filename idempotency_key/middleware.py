class IdempotencyKeyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # call process_view
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None
