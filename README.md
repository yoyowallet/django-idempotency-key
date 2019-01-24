## Idempotency key Django middleware
Middleware to Django that pulls out the idempotency key from the request header and will automatically return the previous response data if the idempotency key was already specified. 
There are two middleware classes which allow view functions to opt-in or opt-out individually depending on your needs.

## Installation

`pip install django_idempotency_key`

## Configuration

First, add to your MIDDLEWARE settings under your settings file.

If you want all non-safe view function to automatically use idempotency keys then use the following:

```
MIDDLEWARE = [
   ...
   'idempotency_key.middleware.IdempotencyKeyMiddleware',
]
```

**WARNING** - Adding this as middleware will require that all client requests to non-safe HTTP methods to supply an idempotency key specified in the request header under HTTP_IDEMPOTENCY_KEY. If this is missing then a 400 BAD REQUEST is returned.

However, if you prefer that all view functions are exempt by default and you will out-in on a per view function basis then use the following:

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

`idempotency_key_response` will always return a Response object is set.

## Required header
When an idempotency key is enabled on a view function the calling client must specify a unique key in the headers called HTTP_IDEMPOTENCY_KEY. If this is missing then a 400 BAD RESPONSE is returned.

## Settings
The following settings can be used to modify the behaviour of the idempotency key middleware.
```
from idempotency_key import status

IDEMPOTENCY_KEY = {
    # Specify the storage class to be used for idempotency keys
    # If not specified then defaults to 'idempotency_key.storage.MemoryKeyStorage'
    'STORAGE_CLASS': 'idempotency_key.storage.MemoryKeyStorage',

    # Specify the key encoder class to be used for idempotency keys.
    # If not specified then defaults to 'idempotency_key.encoders.BasicKeyEncoder'
    'ENCODER_CLASS': 'idempotency_key.encoders.BasicKeyEncoder',

    # Set the response code on a conflict.
    # If not specified this defaults to HTTP_409_CONFLICT
    # If set to None then the original request's status code is used.
    'CONFLICT_STATUS_CODE': status.HTTP_409_CONFLICT,
    
    # Name of the django cache configuration to use for the CacheStorageKey storage class
    'CACHE_NAME': 'default',
    
    # The use of a lock around the storage object so that only one thread at a time can access it.
    # By default this is set to true. WARNING: setting this to false may allow duplicate calls to occur if the timing 
    # is right. 
    'ENABLE_LOCK': True,
    
    # If the ENABLE_LOCK setting is True above then this represents the timeout (in seconds as a floating point number) 
    # to occur before the thread gives up waiting. If a timeout occurs the middleware will return a HTTP_423_LOCKED 
    # response.
    'LOCKING_TIMEOUT': 0.1,
    
    # When the response is to be stored you have the option of deciding when this happens based on the responses
    # status code. If the response status code matches one of the statuses below then it will be stored.
    # The statuses below are the defaults used if this setting is not specified.
    'STORE_ON_STATUSES': [
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
        status.HTTP_202_ACCEPTED,
        status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        status.HTTP_204_NO_CONTENT,
        status.HTTP_205_RESET_CONTENT,
        status.HTTP_206_PARTIAL_CONTENT,
        status.HTTP_207_MULTI_STATUS,
    ]
}
```
