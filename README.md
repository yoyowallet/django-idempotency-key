## Idempotency key Django middleware
Adds in some middleware to Django that pulls out the idempotency key from the request header and will automatically return the previous response data if the idempotency key was already specified. 

## Installation

`pip install django_idempotency_key`

## Configuration

First add to your MIDDLEWARE settings under your settings file.

```
MIDDLEWARE = [
   ...
   'idempotency_key.middleware.IdempotencyKeyMiddleware',
]
```
**WARNING** - Adding this ad middleware will require that all non-safe HTTP methods will require an indempotency key specified in the request header under HTTP_IDEMPOTENCY_KEY
