# --== UNDER CONSTRUCTION Jan-2019 ==--
This package is being actively worked on and is not ready just yet. Please check back later.

## Idempotency key Django middleware
Middleware to Django that pulls out the idempotency key from the request header and will automatically return the previous response data if the idempotency key was already specified. 
There are two middleware classes which allows view functions to opt-in or out-out individually depending on your needs.

## Installation

`pip install django_idempotency_key`

## Configuration

First add to your MIDDLEWARE settings under your settings file.

If you want all non-safe view function to automatically use idempotency keys then use the following:

```
MIDDLEWARE = [
   ...
   'idempotency_key.middleware.IdempotencyKeyMiddleware',
]
```

**WARNING** - Adding this as middleware will require that all client requests to non-safe HTTP methods to supply an indempotency key specified in the request header under HTTP_IDEMPOTENCY_KEY. If this is missing then a 400 BAD REQUEST is returned.

However if you prefer that all view functions are exempt by default and you will out-in on a per view function basis then use the following:

```
MIDDLEWARE = [
   ...
   'idempotency_key.middleware.ExemptIdempotencyKeyMiddleware',
]
```

## Decorators
There are three decorators available that control how idempotency keys work with your view function.

### @idempotency_key
This will ensure that the specified view function uses idempotency keys and will expect the client to send the HTTP_IDEMPOTENCY_KEY (idempotency-key) header. 

**NOTE:** If the IdempotencyKeyMiddleware class is used then this decorator is redundant.

### @idempotency_key_exempt
This will ensure that the specified view function is exempt from idempotency keys and multiple requests with the same data will run the view function every time.

**NOTE:** If the ExemptIdempotencyKeyMiddleware class is used then this decorator is redundant.

### @idempotency_key_manual
When specified the view function will dictate the response provided on a conflict. The decorator will set two variables on the request object that informs the user if the key exists in storage and what the response object was on the last call if the key exists.

These two variables are defined as follows:

```
(boolean) request.idempotency_key_exists
(object) request.idempotency_key_response
```

By default `idempotency_key_response` will return a Response object

## Required header
When a idempotnecy key is enabled on a view function the calling client must specify a unique key in the headers called HTTP_IDEMPOTENCY_KEY. If this is missing then a 400 BAD RESPONSE is returned.

