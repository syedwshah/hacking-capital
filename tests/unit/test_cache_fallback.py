from app.core.cache import KnowledgeCache


def test_cache_set_get_fallback():
    c = KnowledgeCache()
    c.set_summary("AAPL", "daily", {"x": 1}, ttl_s=1)
    assert c.get_summary("AAPL", "daily") == {"x": 1}


