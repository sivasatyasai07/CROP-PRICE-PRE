import time
from typing import Dict, Any, Optional
import os

API_CACHE_ENABLED = os.getenv("API_CACHE_ENABLED", "true").lower() == "true"
API_CACHE_TTL_SECONDS = int(os.getenv("API_CACHE_TTL_SECONDS", "300"))

class SimpleMemoryCache:
    """In-memory cache for API payloads with TTL support and force refresh override."""
    
    def __init__(self, ttl_seconds: int = API_CACHE_TTL_SECONDS):
        self.ttl = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str, force_refresh: bool = False) -> Optional[Any]:
        if not API_CACHE_ENABLED or force_refresh:
            return None
        item = self._store.get(key)
        if not item:
            return None
        if time.time() - item["timestamp"] > self.ttl:
            del self._store[key]
            return None
        return item["value"]

    def set(self, key: str, value: Any):
        if not API_CACHE_ENABLED:
            return
        self._store[key] = {
            "value": value,
            "timestamp": time.time()
        }

    def clear(self):
        self._store.clear()

global_cache = SimpleMemoryCache()
