"""Cache mechanism implementation for API responses"""

import hashlib
import time
from typing import Optional, Dict, Any
from ..model.response_body import SeedanceResponseBody
from ..model.request_body import SeedanceRequestBody


class CacheMechanism:
    """Implement caching for API responses"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize cache mechanism.
        
        Args:
            max_size: Maximum number of items in cache
            ttl: Time-to-live for cache items in seconds
        """
        self.cache: Dict[str, tuple] = {}  # cache_key -> (timestamp, response)
        self.max_size = max_size
        self.ttl = ttl

    def generate_cache_key(self, request_body: SeedanceRequestBody) -> Optional[str]:
        """
        Generate a cache key based on request parameters.
        
        Args:
            request_body: Request body to generate key for
            
        Returns:
            Cache key string or None if request is not cacheable
        """
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

    def get_cached_response(self, cache_key: str) -> Optional[SeedanceResponseBody]:
        """
        Get response from cache if available and not expired.
        
        Args:
            cache_key: Key to look up in cache
            
        Returns:
            Cached response or None if not found or expired
        """
        if cache_key in self.cache:
            timestamp, response = self.cache[cache_key]
            # Check if cache is still valid based on TTL
            if time.time() - timestamp < self.ttl:
                return response
            else:
                # Remove expired entry
                del self.cache[cache_key]
        return None

    def set_cache_response(self, cache_key: str, response: SeedanceResponseBody):
        """
        Store response in cache.
        
        Args:
            cache_key: Key to store response under
            response: Response to cache
        """
        if cache_key:
            # Check if we need to evict oldest entries due to size limit
            if len(self.cache) >= self.max_size:
                # Remove oldest entry (by timestamp)
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][0])
                del self.cache[oldest_key]
            
            self.cache[cache_key] = (time.time(), response)

    def clear_cache(self):
        """Clear all cached entries."""
        self.cache.clear()

    def remove_expired_entries(self):
        """Remove all expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]