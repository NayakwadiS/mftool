# Caching Layer Implementation Guide

## Overview

A TTL-based (Time-To-Live) caching layer has been implemented in mftool to significantly reduce redundant API calls. Since NAV data only updates once daily, caching dramatically improves performance, especially in MCP environments where LLMs may call the same tool repeatedly.

## Features

### 1. **Automatic Caching**
- **NAV Data Cache**: 24-hour TTL (86,400 seconds)
  - `get_scheme_quote()` - Current NAV and scheme details
  - `get_scheme_details()` - Scheme metadata
  - `get_scheme_historical_nav()` - Historical NAV data with 52-week high/low

- **Scheme Codes Cache**: 7-day TTL (604,800 seconds)
  - `get_scheme_codes()` - List of all scheme codes and names
  - Rarely changes, so longer cache duration

### 2. **Cache Management Methods**

#### Clear Cache
```python
from mftool import Mftool

mf = Mftool()
# Clear all cached data
mf.clear_cache()
```

#### Get Cache Statistics
```python
stats = mf.get_cache_stats()
print(stats)
# Output:
# {
#     'nav_cache': {
#         'total_entries': 15,
#         'valid_entries': 15,
#         'expired_entries': 0,
#         'cache_enabled': True
#     },
#     'scheme_codes_cache': {
#         'total_entries': 2,
#         'valid_entries': 2,
#         'expired_entries': 0,
#         'cache_enabled': True
#     }
# }
```

#### Disable/Enable Cache
```python
# Temporarily disable caching
mf.disable_cache()

# Re-enable caching
mf.enable_cache()
```

## Implementation Details

### Cache Architecture

The caching system uses two separate in-memory cache instances:

1. **`_cache`**: For NAV and historical data (24h TTL)
2. **`_scheme_codes_cache`**: For scheme codes list (7d TTL)

### Thread-Safe Design

The `CacheManager` class uses threading locks to ensure thread-safe operations:
- Safe for concurrent access
- Automatic expiry handling
- Memory-efficient with automatic cleanup of expired entries

### Cache Keys

Cache keys are generated based on:
- Method name
- Scheme code
- Output format (as_json, as_Dataframe)

Example: `"quote:119062:False"` for `get_scheme_quote("119062", as_json=False)`

## Performance Benefits

### Before Caching
```python
import time
from mftool import Mftool

mf = Mftool()
mf.disable_cache()

start = time.time()
for i in range(10):
    mf.get_scheme_quote("119062")
end = time.time()

print(f"Time without cache: {end - start:.2f}s")
# Expected: ~5-10 seconds (10 API calls)
```

### After Caching
```python
mf.enable_cache()
mf.clear_cache()

start = time.time()
for i in range(10):
    mf.get_scheme_quote("119062")
end = time.time()

print(f"Time with cache: {end - start:.2f}s")
# Expected: ~0.5-1 second (1 API call + 9 cache hits)
```

## Advanced Usage

### DiskCache (Optional)

For persistent caching across sessions, you can use the `DiskCache` class:

```python
from mftool.cache import DiskCache

# Create a disk-based cache
disk_cache = DiskCache(cache_dir='./mftool_cache', default_ttl=86400)

# Use like CacheManager
value = disk_cache.get("my_key")
if value is None:
    value = fetch_expensive_data()
    disk_cache.set("my_key", value)
```

### Custom TTL

While the default TTL values are optimized for mutual fund data, you can customize them:

```python
from mftool.cache import CacheManager

# Create custom cache with 1-hour TTL
short_cache = CacheManager(default_ttl=3600)
```

## Best Practices

1. **Don't disable cache unless necessary**: The cache is optimized for mutual fund data patterns
2. **Clear cache after market close**: NAV updates happen after market hours
3. **Monitor cache stats**: Use `get_cache_stats()` to understand cache effectiveness
4. **Cache is automatic**: No code changes needed for existing applications

## Cache Invalidation Strategy

### When to Clear Cache

- **After NAV updates** (typically after 9 PM IST on trading days)
- **When debugging** data inconsistencies
- **After scheme code changes** (rare, but happens with new fund launches)

### Automatic Expiry

The cache automatically expires entries based on TTL:
- Expired entries are removed on access
- No manual cleanup needed
- Memory footprint remains small

## MCP Integration Benefits

In Model Context Protocol (MCP) environments:

1. **Reduced API Load**: LLMs often query the same fund multiple times
2. **Faster Response**: Near-instant responses for cached data
3. **Better UX**: Reduced latency for end users
4. **API Rate Limiting**: Helps stay within API rate limits

## Example: Complete Workflow

```python
from mftool import Mftool

# Initialize mftool (cache enabled by default)
mf = Mftool()

# First call - fetches from API and caches
quote1 = mf.get_scheme_quote("119062")
print("First call completed")

# Second call - returns from cache (fast!)
quote2 = mf.get_scheme_quote("119062")
print("Second call completed (from cache)")

# Check cache statistics
stats = mf.get_cache_stats()
print(f"Cache hits: {stats['nav_cache']['valid_entries']}")

# Clear cache when needed (e.g., after NAV update)
mf.clear_cache()
print("Cache cleared")

# Next call will fetch fresh data
quote3 = mf.get_scheme_quote("119062")
print("Fresh data fetched")
```

## Troubleshooting

### Cache Not Working?
```python
# Check if cache is enabled
stats = mf.get_cache_stats()
if not stats['nav_cache']['cache_enabled']:
    mf.enable_cache()
```

### Stale Data?
```python
# Clear cache to force fresh fetch
mf.clear_cache()
```

### Memory Concerns?
```python
# Cache uses minimal memory (~1KB per entry)
# For reference: 1000 cached quotes ≈ 1MB
# Clear cache periodically if needed
mf.clear_cache()
```

## Technical Specifications

- **Storage**: In-memory (RAM)
- **Thread-Safety**: Yes (uses threading.Lock)
- **Persistence**: No (cache cleared on restart)
- **TTL Precision**: Second-level
- **Key Generation**: String-based with function parameters
- **Serialization**: Native Python objects (no pickling)

## Future Enhancements

Potential improvements for future versions:
- Disk-based persistence option
- Configurable TTL per method
- Cache warming on startup
- LRU (Least Recently Used) eviction policy
- Cache size limits
- Redis/Memcached backend support

## Conclusion

The caching layer is production-ready and requires no configuration. It's designed to work transparently, improving performance without changing existing code behavior.

