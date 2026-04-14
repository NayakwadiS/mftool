"""
Cache utility for mftool
Implements TTL-based caching to reduce redundant API calls
"""
import time
import json
import os
from functools import wraps
from threading import Lock


class CacheManager:
    """
    Thread-safe in-memory cache with TTL support
    """
    def __init__(self, default_ttl=86400):  # 24 hours default
        self._cache = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.enabled = True

    def get(self, key):
        """Get value from cache if not expired"""
        if not self.enabled:
            return None

        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    # Remove expired entry
                    del self._cache[key]
        return None

    def set(self, key, value, ttl=None):
        """Set value in cache with TTL"""
        if not self.enabled:
            return

        if ttl is None:
            ttl = self.default_ttl

        expiry = time.time() + ttl
        with self._lock:
            self._cache[key] = (value, expiry)

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def clear_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        with self._lock:
            expired_keys = [k for k, (_, expiry) in self._cache.items() if current_time >= expiry]
            for key in expired_keys:
                del self._cache[key]

    def disable(self):
        """Disable caching"""
        self.enabled = False

    def enable(self):
        """Enable caching"""
        self.enabled = True

    def get_stats(self):
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            current_time = time.time()
            valid_entries = sum(1 for _, expiry in self._cache.values() if current_time < expiry)
            expired_entries = total_entries - valid_entries

        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_enabled': self.enabled
        }


class DiskCache:
    """
    Persistent disk-based cache with TTL support
    """
    def __init__(self, cache_dir=None, default_ttl=86400):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache')

        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.enabled = True
        self._lock = Lock()

        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, key):
        """Generate cache file path for key"""
        # Use hash to create safe filename
        safe_key = str(abs(hash(key)))
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def get(self, key):
        """Get value from disk cache if not expired"""
        if not self.enabled:
            return None

        cache_path = self._get_cache_path(key)

        with self._lock:
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r') as f:
                        cache_data = json.load(f)

                    if time.time() < cache_data['expiry']:
                        return cache_data['value']
                    else:
                        # Remove expired file
                        os.remove(cache_path)
                except (json.JSONDecodeError, KeyError, IOError):
                    # Invalid cache file, remove it
                    if os.path.exists(cache_path):
                        os.remove(cache_path)

        return None

    def set(self, key, value, ttl=None):
        """Set value in disk cache with TTL"""
        if not self.enabled:
            return

        if ttl is None:
            ttl = self.default_ttl

        cache_path = self._get_cache_path(key)
        expiry = time.time() + ttl

        cache_data = {
            'value': value,
            'expiry': expiry,
            'created': time.time()
        }

        with self._lock:
            try:
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f)
            except IOError:
                pass  # Silently fail if can't write cache

    def clear(self):
        """Clear all cache files"""
        with self._lock:
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

    def clear_expired(self):
        """Remove all expired cache files"""
        current_time = time.time()
        with self._lock:
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r') as f:
                                cache_data = json.load(f)
                            if current_time >= cache_data['expiry']:
                                os.remove(file_path)
                        except (json.JSONDecodeError, KeyError, IOError):
                            os.remove(file_path)

    def disable(self):
        """Disable caching"""
        self.enabled = False

    def enable(self):
        """Enable caching"""
        self.enabled = True


def cached(ttl=86400, cache_type='memory'):
    """
    Decorator for caching function results

    :param ttl: Time to live in seconds (default 24 hours)
    :param cache_type: 'memory' or 'disk'
    """
    def decorator(func):
        # Create cache instance for this function
        if cache_type == 'disk':
            cache = DiskCache(default_ttl=ttl)
        else:
            cache = CacheManager(default_ttl=ttl)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            # Skip 'self' for instance methods
            cache_args = args[1:] if args and hasattr(args[0], func.__name__) else args
            cache_key = f"{func.__name__}:{str(cache_args)}:{str(kwargs)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        # Attach cache management methods
        wrapper.clear_cache = cache.clear
        wrapper.clear_expired = cache.clear_expired
        wrapper.disable_cache = cache.disable
        wrapper.enable_cache = cache.enable

        return wrapper
    return decorator

