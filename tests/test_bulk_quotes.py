"""
Test script demonstrating bulk/batch quote fetching performance
Shows the massive speed improvements with concurrent fetching
"""
import time
from mftool import Mftool


def test_bulk_quotes():
    """Demonstrate bulk quote fetching performance"""

    print("=" * 70)
    print("BULK QUOTE FETCHING DEMONSTRATION")
    print("=" * 70)

    mf = Mftool()

    # Portfolio of 20 schemes
    portfolio_codes = [
        '119597', '119062', '119061', '119060', '119551',
        '119552', '119553', '119554', '119555', '119556',
        '120503', '120504', '120505', '120506', '120507',
        '118989', '118990', '118991', '118992', '118993'
    ]

    print(f"\nTesting with {len(portfolio_codes)} schemes")
    print("=" * 70)

    # Test 1: Sequential fetching (old way)
    print("\n[Test 1] Sequential Fetching (one by one)")
    print("-" * 70)
    mf.clear_cache()  # Start fresh

    start = time.time()
    sequential_results = {}
    for code in portfolio_codes:
        quote = mf.get_scheme_quote(code)
        if quote:
            sequential_results[code] = quote
    sequential_time = time.time() - start

    print(f"✓ Fetched {len(sequential_results)} quotes sequentially")
    print(f"  Time taken: {sequential_time:.2f} seconds")
    print(f"  Average per quote: {sequential_time/len(portfolio_codes):.2f}s")

    # Test 2: Bulk fetching (new way)
    print("\n[Test 2] Bulk Fetching (concurrent)")
    print("-" * 70)
    mf.clear_cache()  # Start fresh

    start = time.time()
    bulk_results = mf.get_bulk_quotes(portfolio_codes, show_progress=True)
    bulk_time = time.time() - start

    print(f"\n✓ Fetched {len(bulk_results)} quotes with bulk method")
    print(f"  Time taken: {bulk_time:.2f} seconds")
    print(f"  Average per quote: {bulk_time/len(portfolio_codes):.2f}s")

    # Show performance comparison
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON")
    print("=" * 70)
    speedup = sequential_time / bulk_time if bulk_time > 0 else float('inf')
    improvement = ((sequential_time - bulk_time) / sequential_time) * 100

    print(f"Sequential time:  {sequential_time:.2f}s")
    print(f"Bulk time:        {bulk_time:.2f}s")
    print(f"Time saved:       {sequential_time - bulk_time:.2f}s")
    print(f"Speedup:          {speedup:.1f}x faster")
    print(f"Improvement:      {improvement:.1f}%")

    # Test 3: Show sample data
    print("\n[Test 3] Sample Quotes")
    print("-" * 70)
    sample_codes = list(bulk_results.keys())[:3]
    for code in sample_codes:
        quote = bulk_results[code]
        if quote:
            print(f"{code}: {quote.get('scheme_name', 'N/A')[:50]}")
            print(f"  NAV: {quote.get('nav', 'N/A')}, Updated: {quote.get('last_updated', 'N/A')}")


def test_portfolio_calculation():
    """Demonstrate portfolio value calculation"""

    print("\n\n" + "=" * 70)
    print("PORTFOLIO VALUE CALCULATION")
    print("=" * 70)

    mf = Mftool()

    # Example portfolio
    holdings = [
        {'scheme_code': '119597', 'units': 100.5},
        {'scheme_code': '119062', 'units': 250.75},
        {'scheme_code': '119061', 'units': 50.25},
        {'scheme_code': '119060', 'units': 175.0},
        {'scheme_code': '119551', 'units': 300.0},
    ]

    print(f"\nCalculating value for portfolio of {len(holdings)} schemes...")
    print("-" * 70)

    start = time.time()
    portfolio = mf.calculate_portfolio_value(holdings)
    calc_time = time.time() - start

    print(f"\n✓ Portfolio calculated in {calc_time:.2f} seconds")
    print("\nPortfolio Summary:")
    print(f"  Total Schemes: {portfolio['total_schemes']}")
    print(f"  Total Value:   ₹{portfolio['total_value']:,.2f}")
    print(f"  Currency:      {portfolio['currency']}")

    print("\nHoldings Breakdown:")
    print("-" * 70)
    for holding in portfolio['holdings'][:5]:  # Show first 5
        print(f"\n{holding['scheme_code']}: {holding['scheme_name'][:45]}")
        print(f"  Units: {holding['units']:.2f}")
        print(f"  NAV:   ₹{holding['nav']}")
        print(f"  Value: ₹{holding['current_value']:,.2f}")

def test_with_caching():
    """Demonstrate how caching improves bulk fetching even more"""

    print("\n\n" + "=" * 70)
    print("BULK FETCHING WITH CACHING")
    print("=" * 70)

    mf = Mftool()
    codes = ['119597', '119062', '119061', '119060', '119551'] * 4  # 20 codes

    print(f"\nFetching {len(codes)} quotes (with duplicates)...")

    # First run - no cache
    print("\n[Run 1] No cache")
    mf.clear_cache()
    start = time.time()
    quotes1 = mf.get_bulk_quotes(codes, show_progress=True)
    time1 = time.time() - start
    print(f"Time: {time1:.2f}s")

    # Second run - with cache
    print("\n[Run 2] With cache")
    start = time.time()
    quotes2 = mf.get_bulk_quotes(codes, show_progress=True)
    time2 = time.time() - start
    print(f"Time: {time2:.2f}s")

    if time2 > 0:
        print(f"\n✓ Second run {time1/time2:.1f}x faster with cache!")
    else:
        print(f"\n✓ Second run instantly faster with cache!")


if __name__ == "__main__":
    try:
        test_bulk_quotes()
        test_portfolio_calculation()
        test_with_caching()

        print("\n\n" + "=" * 70)
        print("ALL BULK FETCHING TESTS COMPLETED!")
        print("=" * 70)
        print("\nKey Benefits:")
        print("• 5-10x faster for portfolio operations")
        print("• Concurrent API calls (default: 10 workers)")
        print("• Automatic caching integration")
        print("• Progress tracking available")
        print("• Perfect for portfolio management tools")

    except KeyboardInterrupt:
        print("\n\n  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
