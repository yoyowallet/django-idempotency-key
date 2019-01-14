from functools import wraps


# NOTE:
# The following decorators must be specified BEFORE the @api_view decorator or the function will not be marked
# correctly.
#
# i.e:
#
# @use_idempotency_key
# @api_view(['POST'])
# def my_view_func()
#   ...

def use_idempotency_key(view_func):
    """
    Mark a view function as requiring idempotency key protection.
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.use_idempotency_key = True
    return wraps(view_func)(wrapped_view)


def idempotency_key_exempt(view_func):
    """
    Mark a view function as being exempt from the idempotency key protection.
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.idempotency_key_exempt = True
    return wraps(view_func)(wrapped_view)


def use_idempotency_key_manual_override(view_func):
    """
    Mark a view function as requiring idempotency key protection but the view should control the response.
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.use_idempotency_key_manual_override = True
    return wraps(view_func)(wrapped_view)
