from san.cache import TTLCache, _metadata_cache, clear_cache


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache(ttl=60.0)
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_miss_returns_none(self):
        cache = TTLCache(ttl=60.0)
        assert cache.get("nonexistent") is None

    def test_expired_entry_returns_none(self):
        cache = TTLCache(ttl=0.0)
        cache.set("key", "value")
        # TTL of 0 means immediately expired
        assert cache.get("key") is None

    def test_clear_removes_all(self):
        cache = TTLCache(ttl=60.0)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_overwrite_key(self):
        cache = TTLCache(ttl=60.0)
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"


class TestClearCache:
    def test_clear_cache_function(self):
        _metadata_cache.set("test_key", "test_value")
        assert _metadata_cache.get("test_key") == "test_value"
        clear_cache()
        assert _metadata_cache.get("test_key") is None
