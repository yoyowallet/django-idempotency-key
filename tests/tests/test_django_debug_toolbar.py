from functools import wraps

from django.core.exceptions import ImproperlyConfigured
from django.test import modify_settings, override_settings
import pytest

from tests.tests.utils import for_all_methods


def set_debug_toolbar_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(MIDDLEWARE={
            'prepend': ['debug_toolbar.middleware.DebugToolbarMiddleware'],
            'append': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
            'remove': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
        }):
            with override_settings(
                    DEBUG=True
            ):
                return func(*args, **kwargs)

    return wrapper


@for_all_methods(set_debug_toolbar_middleware)
class TestDjangoDebugToolbar:
    urls = {
        name: '/views/{}/'.format(name) for name in
        ['create']
    }

    def test_post(self, client):
        """
        If django debug toolbar is specified before us in the middleware then ensure an ImproperlyConfigured
        exception is throw to work the user that idempotency keys will not work correctly.
        """
        with pytest.raises(ImproperlyConfigured):
            client.post(self.urls['create'], data={}, secure=True)
