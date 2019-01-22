import pickle

from django.core.cache import caches
from django.test import override_settings

from idempotency_key.storage import MemoryKeyStorage, CacheKeyStorage


def test_memory_storage_store():
    obj = MemoryKeyStorage()
    obj.store_data('key', 'value')
    assert 'key' in obj.idempotency_key_cache_data.keys()
    assert obj.idempotency_key_cache_data['key'] == 'value'


def test_memory_storage_retrieve():
    obj = MemoryKeyStorage()
    obj.store_data('key', 'value')
    key_exists, value = obj.retrieve_data('key')
    assert key_exists is True
    assert value == 'value'


def test_memory_storage_retrieve_no_key():
    obj = MemoryKeyStorage()
    key_exists, value = obj.retrieve_data('key')
    assert key_exists is False
    assert value is None


class TestDefaultCache:
    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'a1394848-7dba-456b-93c5-5959bd293dc6',
            }
        }
    )
    def test_cache_storage_store_default_cache(self):
        obj = CacheKeyStorage()
        obj.store_data('key', 'value')

        cache = caches['default']
        assert 'key' in cache
        assert cache.get('key') == pickle.dumps('value')


class TestNamedCache:
    @override_settings(
        CACHES={
            'MyCache': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'f4c706ac-d71c-4ef5-9c7a-998396773de5',
            }
        },
        IDEMPOTENCY_KEY={
            'STORAGE_CLASS': 'idempotency_key.storage.CacheKeyStorage',
            'CACHE_NAME': 'MyCache'
        },
    )
    def test_cache_storage_store_named_cache(self):
        obj = CacheKeyStorage()
        obj.store_data('key', 'value')

        cache = caches['MyCache']
        assert 'key' in cache
        assert cache.get('key') == pickle.dumps('value')
