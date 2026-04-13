"""
Test script demonstrating the new scheme search functionality
Makes it easy to find mutual funds by name without knowing codes
"""
from mftool import Mftool


def test_basic_search():
    """Demonstrate basic scheme search"""

    print("=" * 70)
    print("SCHEME SEARCH DEMONSTRATION")
    print("=" * 70)

    mf = Mftool()

    # Test 1: Search for HDFC midcap schemes
    print("\n[Test 1] Searching for 'HDFC midcap'")
    print("-" * 70)
    results = mf.search_schemes("HDFC midcap", limit=5)

    print(f"Found {len(results)} matching schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name']}")

    # Test 2: Search for Axis bluechip
    print("\n\n[Test 2] Searching for 'Axis bluechip'")
    print("-" * 70)
    results = mf.search_schemes("Axis bluechip", limit=3)

    print(f"Found {len(results)} matching schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name']}")

    # Test 3: Get quote using search result
    print("\n\n[Test 3] Using search result to get quote")
    print("-" * 70)
    matches = mf.search_schemes("ICICI prudential bluechip", limit=1)

    if matches:
        code = matches[0]['code']
        name = matches[0]['name']
        print(f"Found: {name}")
        print(f"Code: {code}")

        quote = mf.get_scheme_quote(code)
        if quote:
            print(f"\nNAV: ₹{quote['nav']}")
            print(f"Last Updated: {quote['last_updated']}")
    else:
        print("No matches found")


def test_search_by_amc():
    """Demonstrate searching within specific AMC"""

    print("\n\n" + "=" * 70)
    print("SEARCH BY AMC (FUND HOUSE)")
    print("=" * 70)

    mf = Mftool()

    # Test 1: Get all HDFC schemes
    print("\n[Test 1] All HDFC schemes (limited to 5)")
    print("-" * 70)
    results = mf.search_schemes_by_amc("HDFC", limit=5)

    print(f"Found {len(results)} HDFC schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name'][:60]}")

    # Test 2: Search for HDFC equity schemes
    print("\n\n[Test 2] HDFC equity schemes")
    print("-" * 70)
    results = mf.search_schemes_by_amc("HDFC", "equity", limit=5)

    print(f"Found {len(results)} HDFC equity schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name'][:60]}")

    # Test 3: Search for SBI liquid schemes
    print("\n\n[Test 3] SBI liquid schemes")
    print("-" * 70)
    results = mf.search_schemes_by_amc("SBI", "liquid", limit=3)

    print(f"Found {len(results)} SBI liquid schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name'][:60]}")


def test_search_by_type():
    """Demonstrate searching by scheme type"""

    print("\n\n" + "=" * 70)
    print("SEARCH BY SCHEME TYPE")
    print("=" * 70)

    mf = Mftool()

    # Test 1: Find ELSS schemes
    print("\n[Test 1] All ELSS (tax-saving) schemes")
    print("-" * 70)
    results = mf.search_schemes_by_type("elss", limit=5)

    print(f"Found {len(results)} ELSS schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name'][:60]}")

    # Test 2: Find index funds
    print("\n\n[Test 2] Index funds")
    print("-" * 70)
    results = mf.search_schemes_by_type("index", limit=5)

    print(f"Found {len(results)} index funds:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name'][:60]}")

    # Test 3: Find HDFC ELSS schemes (combining type + AMC)
    print("\n\n[Test 3] HDFC ELSS schemes")
    print("-" * 70)
    results = mf.search_schemes_by_type("elss", "hdfc", limit=3)

    print(f"Found {len(results)} HDFC ELSS schemes:\n")
    for scheme in results:
        print(f"  {scheme['code']}: {scheme['name'][:60]}")


def test_llm_friendly_workflow():
    """Demonstrate LLM-friendly workflow"""

    print("\n\n" + "=" * 70)
    print("LLM-FRIENDLY WORKFLOW EXAMPLE")
    print("=" * 70)

    mf = Mftool()

    # Scenario: User asks "What's the NAV of HDFC midcap growth fund?"
    print("\nScenario: User asks 'What's the NAV of HDFC midcap growth fund?'")
    print("-" * 70)

    # Step 1: Search for the fund
    print("\nStep 1: Search for the fund")
    matches = mf.search_schemes("HDFC midcap growth", limit=3)

    print(f"Found {len(matches)} matches:")
    for i, scheme in enumerate(matches, 1):
        print(f"  {i}. {scheme['name']}")

    # Step 2: Use first match to get quote
    if matches:
        print(f"\nStep 2: Get NAV for top match")
        code = matches[0]['code']
        quote = mf.get_scheme_quote(code)

        if quote:
            print(f"\n✓ Answer: The NAV of {quote['scheme_name']} is ₹{quote['nav']}")
            print(f"  (Last updated: {quote['last_updated']})")

    # Scenario 2: Portfolio building
    print("\n\n" + "=" * 70)
    print("Scenario: Building a portfolio with search")
    print("-" * 70)

    # User wants: HDFC equity, ICICI debt, Axis ELSS
    searches = [
        ("HDFC equity growth", "Large cap equity"),
        ("ICICI debt", "Debt fund"),
        ("Axis ELSS", "Tax saving")
    ]

    portfolio = []
    print("\nSearching for portfolio components:\n")

    for search_term, category in searches:
        matches = mf.search_schemes(search_term, limit=1)
        if matches:
            portfolio.append(matches[0])
            print(f"✓ {category}: {matches[0]['name'][:50]}")
            print(f"  Code: {matches[0]['code']}\n")

    # Get quotes for all
    if portfolio:
        print("\nFetching current NAVs...")
        codes = [s['code'] for s in portfolio]
        quotes = mf.get_bulk_quotes(codes)

        print("\nPortfolio Summary:")
        print("-" * 70)
        for scheme in portfolio:
            code = scheme['code']
            quote = quotes.get(code)
            if quote:
                print(f"{scheme['name'][:45]}")
                print(f"  NAV: ₹{quote['nav']}")


def test_fuzzy_matching():
    """Demonstrate fuzzy matching capabilities"""

    print("\n\n" + "=" * 70)
    print("FUZZY MATCHING DEMONSTRATION")
    print("=" * 70)

    mf = Mftool()

    test_cases = [
        ("hdfc", "Lowercase search"),
        ("HDFC", "Uppercase search"),
        ("midcap", "Partial word"),
        ("bluechip", "Alternative spelling"),
        ("tax saver", "Multi-word search"),
    ]

    for search_term, description in test_cases:
        print(f"\n[{description}] Searching for: '{search_term}'")
        print("-" * 70)
        results = mf.search_schemes(search_term, limit=3)

        print(f"Found {len(results)} matches:")
        for scheme in results:
            print(f"  • {scheme['name'][:65]}")


if __name__ == "__main__":
    try:
        test_basic_search()
        test_search_by_amc()
        test_search_by_type()
        test_llm_friendly_workflow()
        test_fuzzy_matching()

        print("\n\n" + "=" * 70)
        print("✅ ALL SEARCH TESTS COMPLETED!")
        print("=" * 70)
        print("\nKey Benefits:")
        print("• No need to know scheme codes")
        print("• Case-insensitive fuzzy matching")
        print("• Search by AMC, type, or name")
        print("• Perfect for LLM/AI applications")
        print("• Works seamlessly with existing methods")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

