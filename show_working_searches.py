"""Show what search terms will work"""
import pandas as pd

df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

print("=" * 80)
print("🔍 WHAT TO SEARCH - WORKING SEARCH TERMS")
print("=" * 80)

print("\n⭐ BEST OPTIONS - Works for BOTH Platforms (Full Comparison):")
print("-" * 80)

# Check common keywords
keywords = ['Stick', 'Essential', 'Snack', 'Fire', 'Happy']
for keyword in keywords:
    amazon_count = len(df[(df['product title'].str.contains(keyword, case=False, na=False)) & 
                          (df['platform'] == 'Amazon')])
    flipkart_count = len(df[(df['product title'].str.contains(keyword, case=False, na=False)) & 
                            (df['platform'] == 'Flipkart')])
    if amazon_count > 0 and flipkart_count > 0:
        print(f"✅ '{keyword}' - Amazon: {amazon_count} | Flipkart: {flipkart_count} | Total: {amazon_count + flipkart_count}")
        print(f"   👉 Try searching: '{keyword}'")

print("\n" + "=" * 80)
print("📦 Flipkart Brands (Will show Flipkart results only):")
print("-" * 80)

brands = ['Dove', 'Himalaya', 'Cadbury', 'Nivea', 'Mi', 'boAt', 'Boat', 'Harpic', 'Nestlé', 'Nestle', 'Surf Excel']
for brand in brands:
    flipkart_count = len(df[(df['brand'].str.contains(brand, case=False, na=False)) & 
                            (df['platform'] == 'Flipkart')])
    amazon_count = len(df[(df['brand'].str.contains(brand, case=False, na=False)) & 
                          (df['platform'] == 'Amazon')])
    if flipkart_count > 0:
        status = "✅" if amazon_count > 0 else "⚠️ "
        print(f"{status} '{brand}' - Flipkart: {flipkart_count} products | Amazon: {amazon_count} products")
        print(f"   👉 Try searching: '{brand}'")

print("\n" + "=" * 80)
print("🎯 RECOMMENDED: Start with these 3 searches:")
print("=" * 80)
print("1. Search: 'Stick' - Shows BOTH platforms with full comparison")
print("2. Search: 'Essential' - Shows BOTH platforms with full comparison")
print("3. Search: 'Dove' - Shows Flipkart products (Amazon will show 'No data')")
print("\n" + "=" * 80)


