"""Cache utilities for API responses"""

import hashlib
import time
from typing import Optional
from ..model.response_body import SeedanceResponseBody


def generate_cache_key(request_body) -> Optional[str]:
    """Generate a cache key based on request parameters"""
    # Only cache deterministic requests (temperature = 0)
    if getattr(request_body, 'temperature', None) != 0:
        return None

    cacheable_params = ('prompt', 'model', 'max_tokens', 'temperature')
    cache_data = {}
    for param in cacheable_params:
        if hasattr(request_body, param):
            value = getattr(request_body, param)
            if value is not None:
                cache_data[param] = value
    
    cache_str = str(sorted(cache_data.items()))
    return hashlib.md5(cache_str.encode()).hexdigest()


def get_cached_response(cache_key: str, cache: dict) -> Optional[SeedanceResponseBody]:
    """Get response from cache if available"""
    if cache_key and cache_key in cache:
        cached_at, response = cache[cache_key]
        # Check if cache is still valid (for simplicity, we'll assume it's always valid for this example)
        return response
    return None


def set_cache_response(cache_key: str, response: SeedanceResponseBody, cache: dict):
    """Store response in cache"""
    if cache_key:
        cache[cache_key] = (time.time(), response)