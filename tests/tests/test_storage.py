from idempotency_key.storage import MemoryKeyStorage


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


