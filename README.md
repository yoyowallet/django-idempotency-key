## Idempotency key Django middleware
Adds in some middleware to Django that pulls out the idempotency key from the request header and will automatically return the previous response data if the idempotency key was already specified. 

## Installation

`pip install idempotency_key`

## Configuration

First add to your MIDDLEWARE settings under your settings file.

```
MIDDLEWARE = [
   ...
   'idempotency_key.middleware.IdempotencyKeyMiddleware',
]
```
