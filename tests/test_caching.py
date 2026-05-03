"""
Test script to demonstrate the caching functionality in mftool
This script shows the performance improvement with caching enabled
"""

import time
from mftool import Mftool


def test_caching_performance():
    """Demonstrate the performance benefits of caching"""

    print("=" * 60)
    print("MFTOOL CACHING DEMONSTRATION")
    print("=" * 60)

    mf = Mftool()
    test_scheme_code = "119062"  # Example scheme code

    # Test 1: Without Cache
    print("\n[Test 1] Performance WITHOUT cache (10 calls)")
    print("-" * 60)
    mf.disable_cache()
    mf.clear_cache()

    start = time.time()
    for i in range(10):
        result = mf.get_scheme_quote(test_scheme_code)
        if i == 0:
            print(f"Scheme: {result.get('scheme_name', 'N/A')}")
            print(f"NAV: {result.get('nav', 'N/A')}")
    end = time.time()

    time_without_cache = end - start
    print(f"\nTotal time: {time_without_cache:.2f} seconds")
    print(f"Average per call: {time_without_cache/10:.2f} seconds")

    # Test 2: With Cache
    print("\n[Test 2] Performance WITH cache (10 calls)")
    print("-" * 60)
    mf.enable_cache()
    mf.clear_cache()

    start = time.time()
    for i in range(10):
        result = mf.get_scheme_quote(test_scheme_code)
        if i == 0:
            print(f"Call 1: Fetching from API...")
        elif i == 1:
            print(f"Call 2+: Using cached data...")
    end = time.time()

    time_with_cache = end - start
    print(f"\nTotal time: {time_with_cache:.2f} seconds")
    print(f"Average per call: {time_with_cache/10:.2f} seconds")

    # Show improvement
    print("\n" + "=" * 60)
    print("PERFORMANCE IMPROVEMENT")
    print("=" * 60)
    improvement = ((time_without_cache - time_with_cache) / time_without_cache) * 100
    speedup = time_without_cache / time_with_cache
    print(f"Time saved: {time_without_cache - time_with_cache:.2f} seconds")
    print(f"Performance improvement: {improvement:.1f}%")
    print(f"Speedup: {speedup:.1f}x faster")

    # Test 3: Cache Statistics
    print("\n[Test 3] Cache Statistics")
    print("-" * 60)
    stats = mf.get_cache_stats()
    print(f"NAV Cache:")
    print(f"  - Total entries: {stats['nav_cache']['total_entries']}")
    print(f"  - Valid entries: {stats['nav_cache']['valid_entries']}")
    print(f"  - Expired entries: {stats['nav_cache']['expired_entries']}")
    print(f"  - Cache enabled: {stats['nav_cache']['cache_enabled']}")

    print(f"\nScheme Codes Cache:")
    print(f"  - Total entries: {stats['scheme_codes_cache']['total_entries']}")
    print(f"  - Valid entries: {stats['scheme_codes_cache']['valid_entries']}")
    print(f"  - Expired entries: {stats['scheme_codes_cache']['expired_entries']}")
    print(f"  - Cache enabled: {stats['scheme_codes_cache']['cache_enabled']}")

    # Test 4: Different methods
    print("\n[Test 4] Testing different cached methods")
    print("-" * 60)

    print("Fetching scheme details (first time - from API)...")
    start = time.time()
    details = mf.get_scheme_details(test_scheme_code)
    time1 = time.time() - start
    print(f"  Time: {time1:.2f}s")

    print("Fetching scheme details (second time - from cache)...")
    start = time.time()
    details = mf.get_scheme_details(test_scheme_code)
    time2 = time.time() - start
    print(f"  Time: {time2:.4f}s (cached)")

    # Test 5: Cache clearing
    print("\n[Test 5] Cache Management")
    print("-" * 60)
    print("Current cache stats:")
    stats = mf.get_cache_stats()
    print(f"  NAV cache entries: {stats['nav_cache']['total_entries']}")

    print("\nClearing cache...")
    mf.clear_cache()

    stats = mf.get_cache_stats()
    print(f"  NAV cache entries after clear: {stats['nav_cache']['total_entries']}")

    print("\n" + "=" * 60)
    print("CACHING DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. Caching provides significant performance improvements")
    print("2. NAV data is cached for 24 hours (updates once daily)")
    print("3. Scheme codes are cached for 7 days (rarely change)")
    print("4. Cache management is automatic and thread-safe")
    print("5. Use clear_cache() to force fresh data when needed")


def test_multiple_schemes():
    """Test caching with multiple schemes"""

    print("\n" + "=" * 60)
    print("TESTING MULTIPLE SCHEMES")
    print("=" * 60)

    mf = Mftool()
    mf.enable_cache()
    mf.clear_cache()

    # Example scheme codes (replace with valid codes)
    schemes = ["119062", "119061", "119060"]

    print("\nFetching data for 3 schemes (first pass)...")
    start = time.time()
    for code in schemes:
        try:
            quote = mf.get_scheme_quote(code)
            print(f"  {code}: {quote.get('scheme_name', 'N/A')[:50]}")
        except Exception as e:
            print(f"  {code}: Error - {str(e)[:50]}")
    first_pass = time.time() - start

    print(f"\nFirst pass time: {first_pass:.2f}s")

    print("\nFetching same data again (from cache)...")
    start = time.time()
    for code in schemes:
        try:
            quote = mf.get_scheme_quote(code)
        except Exception:
            pass
    second_pass = time.time() - start

    print(f"Second pass time: {second_pass:.4f}s")

    # Handle extremely fast cache (avoid division by zero)
    if second_pass > 0:
        print(f"Speedup: {first_pass/second_pass:.1f}x faster")
    else:
        print(f"Speedup: Cache is instantaneous (< 0.0001s)!")

    stats = mf.get_cache_stats()
    print(f"\nCache now has {stats['nav_cache']['total_entries']} entries")


if __name__ == "__main__":
    try:
        test_caching_performance()
        test_multiple_schemes()

        print("\nAll tests completed successfully!")
        print("\nNote: For best results, ensure you have internet connectivity")
        print("and the AMFI API is accessible.")

    except KeyboardInterrupt:
        print("\n\n  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n Error during testing: {str(e)}")
        print("This may be due to network issues or invalid scheme codes")
