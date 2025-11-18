"""Check if the updated products are in the dataset"""
import pandas as pd

print("=" * 80)
print("CHECKING UPDATED PRODUCTS IN DATASET")
print("=" * 80)

# Load dataset
df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

# Brands to check
brands_to_check = [
    'Samsung', 'Boat', 'boAt', 'Mi', 'Xiaomi',
    'Nivea', 'Dove', 'Himalaya',
    'Cadbury', 'Nestlé', 'Nestle',
    'Harpic', 'Surf Excel'
]

# Products to check
products_to_check = [
    'Samsung 10000mAh Power Bank',
    'boAt Airdopes 131',
    'Mi 3A Fast Charger',
    'Dove Intense Repair Shampoo',
    'Nivea Soft Light Moisturizer',
    'Himalaya Purifying Neem Face Wash',
    'Cadbury Dairy Milk Silk',
    'Nestlé Maggi',
    'Harpic Bathroom Cleaner',
    'Surf Excel Matic Detergent'
]

print("\n🔍 Checking Brands...")
print("-" * 80)

# Check brands
for brand in brands_to_check:
    amazon_matches = df[(df['platform'] == 'Amazon') & 
                       (df['brand'].str.contains(brand, case=False, na=False))]
    flipkart_matches = df[(df['platform'] == 'Flipkart') & 
                         (df['brand'].str.contains(brand, case=False, na=False))]
    
    if len(amazon_matches) > 0 or len(flipkart_matches) > 0:
        print(f"✅ {brand}:")
        print(f"   Amazon: {len(amazon_matches)} products")
        print(f"   Flipkart: {len(flipkart_matches)} products")
        if len(amazon_matches) > 0 and len(flipkart_matches) > 0:
            print(f"   ⭐ BOTH PLATFORMS - Perfect for comparison!")
        print()

print("\n🔍 Checking Products...")
print("-" * 80)

# Check products
for product in products_to_check:
    # Search in product titles
    amazon_matches = df[(df['platform'] == 'Amazon') & 
                       (df['product title'].str.contains(product.split()[0], case=False, na=False))]
    flipkart_matches = df[(df['platform'] == 'Flipkart') & 
                         (df['product title'].str.contains(product.split()[0], case=False, na=False))]
    
    # Also check full product name
    amazon_full = df[(df['platform'] == 'Amazon') & 
                    (df['product title'].str.contains(product, case=False, na=False))]
    flipkart_full = df[(df['platform'] == 'Flipkart') & 
                      (df['product title'].str.contains(product, case=False, na=False))]
    
    if len(amazon_full) > 0 or len(flipkart_full) > 0:
        print(f"✅ {product}:")
        print(f"   Amazon: {len(amazon_full)} exact matches")
        print(f"   Flipkart: {len(flipkart_full)} exact matches")
        if len(amazon_full) > 0 and len(flipkart_full) > 0:
            print(f"   ⭐ BOTH PLATFORMS - Perfect for comparison!")
        elif len(amazon_full) > 0:
            print(f"   Sample: {amazon_full.iloc[0]['product title'][:60]}")
        elif len(flipkart_full) > 0:
            print(f"   Sample: {flipkart_full.iloc[0]['product title'][:60]}")
    elif len(amazon_matches) > 0 or len(flipkart_matches) > 0:
        print(f"⚠️  {product}:")
        print(f"   Amazon: {len(amazon_matches)} partial matches")
        print(f"   Flipkart: {len(flipkart_matches)} partial matches")
    print()

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Count products by platform for common brands
common_brands_found = []
for brand in brands_to_check:
    amazon_count = len(df[(df['platform'] == 'Amazon') & 
                          (df['brand'].str.contains(brand, case=False, na=False))])
    flipkart_count = len(df[(df['platform'] == 'Flipkart') & 
                           (df['brand'].str.contains(brand, case=False, na=False))])
    if amazon_count > 0 and flipkart_count > 0:
        common_brands_found.append((brand, amazon_count, flipkart_count))

print(f"\n✅ Brands found in BOTH platforms: {len(common_brands_found)}")
for brand, amazon_count, flipkart_count in common_brands_found:
    print(f"   - {brand}: Amazon({amazon_count}) | Flipkart({flipkart_count})")

print("\n💡 Search Recommendations:")
print("   Try searching for these brand names:")
for brand, _, _ in common_brands_found[:10]:
    print(f"   - '{brand}'")


