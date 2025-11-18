import pandas as pd

# Load dataset
df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

# Separate by platform
amazon = df[df['platform'] == 'Amazon']
flipkart = df[df['platform'] == 'Flipkart']

print("=" * 80)
print("ANALYZING COMMON PRODUCTS FOR PRICE COMPARISON")
print("=" * 80)

# Get sample products from each platform
print("\n=== AMAZON PRODUCTS (Sample) ===")
for idx, row in amazon.head(15).iterrows():
    title = str(row['product title'])[:70] if pd.notna(row['product title']) else 'N/A'
    brand = str(row['brand']) if pd.notna(row['brand']) else 'N/A'
    category = str(row['bb category']) if pd.notna(row['bb category']) else 'N/A'
    print(f"{title} | Brand: {brand} | Category: {category}")

print("\n=== FLIPKART PRODUCTS (Sample) ===")
for idx, row in flipkart.head(15).iterrows():
    title = str(row['product title'])[:70] if pd.notna(row['product title']) else 'N/A'
    brand = str(row['brand']) if pd.notna(row['brand']) else 'N/A'
    category = str(row['bb category']) if pd.notna(row['bb category']) else 'N/A'
    print(f"{title} | Brand: {brand} | Category: {category}")

# Find common keywords in product titles
print("\n" + "=" * 80)
print("SEARCHING FOR COMMON KEYWORDS...")
print("=" * 80)

# Common product keywords to search for
common_keywords = ['Echo', 'Kindle', 'Fire', 'Basics', 'Solimo', 'Happy Belly']

print("\n=== PRODUCTS CONTAINING COMMON KEYWORDS ===")
for keyword in common_keywords:
    amazon_matches = amazon[amazon['product title'].str.contains(keyword, case=False, na=False)]
    flipkart_matches = flipkart[flipkart['product title'].str.contains(keyword, case=False, na=False)]
    
    if len(amazon_matches) > 0 or len(flipkart_matches) > 0:
        print(f"\nKeyword: '{keyword}'")
        print(f"  Amazon: {len(amazon_matches)} products")
        if len(amazon_matches) > 0:
            print(f"    Example: {amazon_matches.iloc[0]['product title'][:60]}")
        print(f"  Flipkart: {len(flipkart_matches)} products")
        if len(flipkart_matches) > 0:
            print(f"    Example: {flipkart_matches.iloc[0]['product title'][:60]}")

# Get unique brands from each
print("\n" + "=" * 80)
print("RECOMMENDED SEARCH TERMS FOR COMPARISON")
print("=" * 80)

# Since Amazon has mostly its own products, let's find searchable terms
amazon_brands = set(amazon['brand'].dropna().str.lower().unique())
flipkart_brands = set(flipkart['brand'].dropna().str.lower().unique())

print("\nAmazon Brands:", sorted(list(amazon_brands)))
print("\nTop Flipkart Brands:", sorted(list(flipkart_brands))[:20])

# Find products that might match by searching for common words
print("\n" + "=" * 80)
print("10 RECOMMENDED SEARCH TERMS:")
print("=" * 80)

recommendations = []

# Check Amazon products
for idx, row in amazon.iterrows():
    if pd.notna(row['product title']):
        title = str(row['product title']).lower()
        # Check if any part of this title appears in Flipkart
        words = title.split()
        for word in words:
            if len(word) > 3:  # Skip short words
                flipkart_matches = flipkart[flipkart['product title'].str.contains(word, case=False, na=False)]
                if len(flipkart_matches) > 0 and word not in [r.lower() for r in recommendations]:
                    recommendations.append(word.title())
                    if len(recommendations) >= 10:
                        break
        if len(recommendations) >= 10:
            break

if len(recommendations) < 10:
    # Add some common Amazon product names
    amazon_products = amazon['product title'].dropna().head(10)
    for product in amazon_products:
        # Extract main product name (first few words)
        words = str(product).split()[:3]
        search_term = ' '.join(words)
        if search_term not in recommendations:
            recommendations.append(search_term)
        if len(recommendations) >= 10:
            break

print("\n1-10. Try searching for these terms:")
for i, term in enumerate(recommendations[:10], 1):
    print(f"   {i}. {term}")

print("\n" + "=" * 80)
print("NOTE: Since Amazon and Flipkart have different product catalogs,")
print("you may need to search for generic product types or brand names.")
print("=" * 80)


