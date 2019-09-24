from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.test import modify_settings
import pytest


class TestDjangoDebugToolbar:
    urls = {
        name: '/views/{}/'.format(name) for name in
        ['create']
    }

    @pytest.fixture(autouse=True)
    def _modify_settings(self):
        with modify_settings(MIDDLEWARE={
            'prepend': ['debug_toolbar.middleware.DebugToolbarMiddleware'],
            'append': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
            'remove': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
        }):
            yield

    def test_post(self, client, settings):
        """
        If django debug toolbar is specified before us in the middleware then ensure an ImproperlyConfigured
        exception is throw to work the user that idempotency keys will not work correctly.
        """
        settings.DEBUG = True
        with pytest.raises(ImproperlyConfigured):
            client.post(self.urls['create'], data={}, secure=True)
