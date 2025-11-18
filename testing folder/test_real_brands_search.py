"""Test search with real brands"""
import requests
import json

API_BASE_URL = "http://localhost:5000"

# Brands to test
brands_to_test = [
    'Samsung', 'Boat', 'boAt', 'Mi', 'Xiaomi',
    'Nivea', 'Dove', 'Himalaya',
    'Cadbury', 'Nestlé', 'Nestle',
    'Harpic', 'Surf Excel'
]

# Products to test
products_to_test = [
    'Samsung',
    'boAt',
    'Mi',
    'Dove',
    'Nivea',
    'Himalaya',
    'Cadbury',
    'Nestlé',
    'Harpic',
    'Surf Excel'
]

def test_search(term):
    """Test a search term"""
    try:
        url = f"{API_BASE_URL}/api/price-comparison?q={term}"
        print(f"\n🔍 Testing: '{term}'")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            total_matches = data.get('metadata', {}).get('total_matches', 0)
            platform_summary = data.get('platform_summary', [])
            results = data.get('results', [])
            
            print(f"   ✅ Total matches: {total_matches}")
            
            # Check platforms
            amazon_count = sum(1 for r in results if r.get('platform') == 'Amazon')
            flipkart_count = sum(1 for r in results if r.get('platform') == 'Flipkart')
            
            print(f"   📦 Amazon: {amazon_count} products")
            print(f"   📦 Flipkart: {flipkart_count} products")
            
            # Platform summary
            if platform_summary:
                print(f"   💰 Platform Prices:")
                for platform in platform_summary:
                    price = platform.get('best_final_price', 'N/A')
                    print(f"      {platform.get('platform')}: ₹{price}")
            
            # Best overall
            best_overall = data.get('best_overall')
            if best_overall:
                print(f"   🏆 Best Deal: {best_overall.get('platform')} - ₹{best_overall.get('final_price')}")
            
            # Platform gap
            platform_gap = data.get('platform_gap')
            if platform_gap:
                print(f"   💵 Savings: ₹{platform_gap.get('price_gap', 'N/A')}")
            
            if amazon_count > 0 and flipkart_count > 0:
                print(f"   ⭐ PERFECT - Both platforms have products!")
            elif flipkart_count > 0:
                print(f"   ⚠️  Only Flipkart has products (Amazon will show 'No data available')")
            elif amazon_count > 0:
                print(f"   ⚠️  Only Amazon has products (Flipkart will show 'No data available')")
            else:
                print(f"   ❌ No products found")
                
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to API server")
        print(f"   Make sure server is running: python price_api.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING SEARCH WITH REAL BRANDS")
    print("=" * 80)
    print("\n⚠️  Make sure your API server is running!")
    print("   Run: python price_api.py")
    print("=" * 80)
    
    # Test brands
    print("\n📋 Testing Brands:")
    success_count = 0
    for brand in brands_to_test[:10]:  # Test first 10
        if test_search(brand):
            success_count += 1
    
    print(f"\n{'='*80}")
    print(f"Results: {success_count}/{len(brands_to_test[:10])} searches successful")
    print(f"{'='*80}")


