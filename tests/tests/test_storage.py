import pickle

from django.core.cache import caches
from django.test import override_settings

from idempotency_key.storage import MemoryKeyStorage, CacheKeyStorage


def test_memory_storage_store():
    cache_name = 'default'
    obj = MemoryKeyStorage()
    obj.store_data(cache_name, 'key', 'value')
    assert 'key' in obj.idempotency_key_cache_data[cache_name].keys()
    assert obj.idempotency_key_cache_data[cache_name]['key'] == 'value'


def test_memory_storage_retrieve():
    cache_name = 'default'
    obj = MemoryKeyStorage()
    obj.store_data(cache_name, 'key', 'value')
    key_exists, value = obj.retrieve_data(cache_name, 'key')
    assert key_exists is True
    assert value == 'value'


def test_memory_storage_cache_name_not_present():
    cache_name = 'default'
    obj = MemoryKeyStorage()
    key_exists, value = obj.retrieve_data(cache_name, 'key')
    assert key_exists is False
    assert value is None


def test_memory_storage_retrieve_no_key():
    cache_name = 'default'
    obj = MemoryKeyStorage()
    # This creates a cache with name default and adds a dummy key:value pair
    obj.store_data(cache_name, 'somekey', None)
    # now try to get a key that does not exist
    key_exists, value = obj.retrieve_data(cache_name, 'key')
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
        obj.store_data('default', 'key', 'value')

        cache = caches['default']
        assert 'key' in cache
        assert cache.get('key') == pickle.dumps('value')


class TestNamedCache:
    @override_settings(
        CACHES={
            'FiveMinuteCache': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'f4c706ac-d71c-4ef5-9c7a-998396773de5',
            }
        },
        IDEMPOTENCY_KEY={
            'STORAGE': {
                'STORAGE_CLASS': 'idempotency_key.storage.CacheKeyStorage',
                'CACHE_NAME': 'FiveMinuteCache'
            },
        },
    )
    def test_cache_storage_store_named_cache(self):
        obj = CacheKeyStorage()
        obj.store_data('FiveMinuteCache', 'key', 'value')

        cache = caches['FiveMinuteCache']
        assert 'key' in cache
        assert cache.get('key') == pickle.dumps('value')
