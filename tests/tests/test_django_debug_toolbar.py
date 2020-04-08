from functools import wraps

from django.core.exceptions import ImproperlyConfigured
from django.test import modify_settings, override_settings
import pytest


def set_debug_toolbar_middleware_start(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(
            MIDDLEWARE={
                "prepend": ["debug_toolbar.middleware.DebugToolbarMiddleware"],
                "append": ["idempotency_key.middleware.IdempotencyKeyMiddleware"],
                "remove": ["idempotency_key.middleware.ExemptIdempotencyKeyMiddleware"],
            }
        ):
            with override_settings(DEBUG=True):
                return func(*args, **kwargs)

    return wrapper


def set_debug_toolbar_middleware_end(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(
            MIDDLEWARE={
                "prepend": [],
                "append": [
                    "idempotency_key.middleware.IdempotencyKeyMiddleware",
                    "debug_toolbar.middleware.DebugToolbarMiddleware",
                ],
                "remove": ["idempotency_key.middleware.ExemptIdempotencyKeyMiddleware"],
            }
        ):
            with override_settings(DEBUG=True):
                return func(*args, **kwargs)

    return wrapper


class TestDjangoDebugToolbar:
    """
    There was an issue if django debug toolbar was specified before us in the
    middleware chain then the idempotency code would be bypassed. The code was updated
    so that an ImproperlyConfigured exception was throw to warn the user that
    idempotency keys will not work correctly. This was an issue for Django 1.9 which is
    no longer supported.
    Now we just make sure that the ImproperlyConfigured exception is not thrown
    regardless of the django toolbar position in the middleware.
    """

    urls = {name: "/views/{}/".format(name) for name in ["create"]}

    @set_debug_toolbar_middleware_start
    def test_post(self, client):
        """
        django-debug-toolbar added BEFORE idempotency-key
        """
        try:
            client.post(self.urls["create"], data={}, secure=True)
        except ImproperlyConfigured:
            pytest.fail("ImproperlyConfigured was raised but should not have been.")

        try:
            client.post(self.urls["create"], data={}, secure=True)
        except ImproperlyConfigured:
            pytest.fail("ImproperlyConfigured was raised but should not have been.")

    @set_debug_toolbar_middleware_end
    def test_post_2(self, client):
        """
        django-debug-toolbar added AFTER idempotency-key
        """
        try:
            client.post(self.urls["create"], data={}, secure=True)
        except ImproperlyConfigured:
            pytest.fail("ImproperlyConfigured was raised but should not have been.")
