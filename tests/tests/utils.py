from __future__ import unicode_literals
from functools import wraps

from django.test import modify_settings


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def set_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(MIDDLEWARE={
            'append': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
            'remove': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
        }):
            return func(*args, **kwargs)

    return wrapper


def set_exempt_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with modify_settings(MIDDLEWARE={
            'remove': ['idempotency_key.middleware.IdempotencyKeyMiddleware'],
            'append': ['idempotency_key.middleware.ExemptIdempotencyKeyMiddleware'],
        }):
            return func(*args, **kwargs)

    return wrapper
