"""
Quick test script to verify "Fire" search is working
"""
import requests
import json

API_BASE_URL = "http://localhost:5000"

print("=" * 60)
print("Testing 'Fire' Search")
print("=" * 60)

try:
    # Test without date filter
    print("\n1. Testing search WITHOUT date filter:")
    url = f"{API_BASE_URL}/api/price-comparison?q=Fire"
    print(f"   URL: {url}")
    response = requests.get(url, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success!")
        print(f"   Total matches: {data.get('metadata', {}).get('total_matches', 0)}")
        
        platform_summary = data.get('platform_summary', [])
        print(f"\n   Platform Summary:")
        for platform in platform_summary:
            print(f"      {platform.get('platform', 'Unknown')}: {platform.get('count', 0)} products")
        
        results = data.get('results', [])
        if results:
            print(f"\n   Sample results (first 3):")
            for i, result in enumerate(results[:3], 1):
                print(f"      {i}. {result.get('product', 'N/A')} - {result.get('platform', 'N/A')} - ₹{result.get('final_price', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ ERROR: Cannot connect to API server!")
    print("   Make sure the server is running:")
    print("   python price_api.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("If you see 'Cannot connect', start the API server:")
print("  python price_api.py")
print("=" * 60)

