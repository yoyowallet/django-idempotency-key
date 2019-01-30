from django.conf import settings
from django.utils import module_loading

from idempotency_key import status


def idempotency_key_exists(request):
    return getattr(request, 'idempotency_key_exists', False)


def idempotency_key_response(request):
    return getattr(request, 'idempotency_key_response', None)


def get_encoder_class():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    return module_loading.import_string(idkey_settings.get('ENCODER_CLASS', 'idempotency_key.encoders.BasicKeyEncoder'))


def get_conflict_code():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    return idkey_settings.get('CONFLICT_STATUS_CODE', status.HTTP_409_CONFLICT)


def get_storage_class():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    storage_settings = idkey_settings.get('STORAGE', dict())
    return module_loading.import_string(storage_settings.get('CLASS', 'idempotency_key.storage.MemoryKeyStorage'))


def get_storage_cache_name():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    storage_settings = idkey_settings.get('STORAGE', dict())
    return storage_settings.get('CACHE_NAME', 'default')


def get_storage_store_on_statuses():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    storage_settings = idkey_settings.get('STORAGE', dict())
    return storage_settings.get(
        'STORE_ON_STATUSES', [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_205_RESET_CONTENT,
            status.HTTP_206_PARTIAL_CONTENT,
            status.HTTP_207_MULTI_STATUS,
        ]
    )


def get_lock_class():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    lock_settings = idkey_settings['LOCK'] if 'LOCK' in idkey_settings else dict()
    return module_loading.import_string(lock_settings.get('CLASS', 'idempotency_key.locks.SingleProcessLock'))


def get_lock_timeout():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    lock_settings = idkey_settings['LOCK'] if 'LOCK' in idkey_settings else dict()
    return lock_settings.get('TIMEOUT', 0.1)  # default to 100ms


def get_lock_enable():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    lock_settings = idkey_settings['LOCK'] if 'LOCK' in idkey_settings else dict()
    return lock_settings.get('ENABLE', True)


def get_lock_time_to_live():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    lock_settings = idkey_settings['LOCK'] if 'LOCK' in idkey_settings else dict()
    return lock_settings.get('TTL', None)


def get_lock_name():
    idkey_settings = getattr(settings, 'IDEMPOTENCY_KEY', dict())
    lock_settings = idkey_settings['LOCK'] if 'LOCK' in idkey_settings else dict()
    return lock_settings.get('NAME', 'MyLock')
