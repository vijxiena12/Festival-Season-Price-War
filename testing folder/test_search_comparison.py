"""
Test script to verify search comparison is working correctly
"""
import requests
import json

API_BASE_URL = "http://localhost:5000"

def test_search(term):
    """Test a search term and show comparison results"""
    print(f"\n{'='*80}")
    print(f"Testing search: '{term}'")
    print(f"{'='*80}")
    
    try:
        url = f"{API_BASE_URL}/api/price-comparison?q={term}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Search successful!")
            print(f"   Total matches: {data.get('metadata', {}).get('total_matches', 0)}")
            
            # Platform summary
            platform_summary = data.get('platform_summary', [])
            print(f"\n📊 Platform Comparison:")
            for platform in platform_summary:
                print(f"   {platform.get('platform', 'Unknown')}:")
                print(f"      Best Price: ₹{platform.get('best_final_price', 'N/A')}")
                print(f"      MRP: ₹{platform.get('mrp', 'N/A')}")
                print(f"      Discount: {platform.get('discount_percent', 'N/A')}%")
                if platform.get('festive_window'):
                    print(f"      Festive Event: {platform.get('festive_window')}")
            
            # Platform gap
            platform_gap = data.get('platform_gap')
            if platform_gap:
                print(f"\n💰 Price Gap:")
                print(f"   Cheapest: {platform_gap.get('cheapest_platform')} - ₹{platform_gap.get('cheapest_price')}")
                print(f"   Next Best: {platform_gap.get('next_best_platform')} - ₹{platform_gap.get('next_best_price', 'N/A')}")
                print(f"   Savings: ₹{platform_gap.get('price_gap', 'N/A')}")
            
            # Best overall
            best_overall = data.get('best_overall')
            if best_overall:
                print(f"\n🏆 Best Overall Deal:")
                print(f"   Platform: {best_overall.get('platform')}")
                print(f"   Price: ₹{best_overall.get('final_price', 'N/A')}")
                print(f"   Product: {best_overall.get('product', 'N/A')[:50]}")
            
            # Results count by platform
            results = data.get('results', [])
            amazon_count = sum(1 for r in results if r.get('platform') == 'Amazon')
            flipkart_count = sum(1 for r in results if r.get('platform') == 'Flipkart')
            print(f"\n📦 Results by Platform:")
            print(f"   Amazon: {amazon_count} products")
            print(f"   Flipkart: {flipkart_count} products")
            
            if amazon_count > 0 and flipkart_count > 0:
                print(f"\n✅ COMPARISON AVAILABLE - Both platforms have products!")
            elif amazon_count > 0:
                print(f"\n⚠️  Only Amazon products found")
            elif flipkart_count > 0:
                print(f"\n⚠️  Only Flipkart products found")
            else:
                print(f"\n❌ No products found")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API server at {API_BASE_URL}")
        print("   Make sure the server is running: python price_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*80)
    print("SEARCH COMPARISON TEST")
    print("="*80)
    
    # Test with recommended search terms
    test_terms = ["Fire", "Essential", "Stick", "Snack"]
    
    for term in test_terms:
        test_search(term)
    
    print(f"\n{'='*80}")
    print("Test Complete!")
    print("="*80)


