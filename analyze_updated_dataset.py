import pandas as pd

print("=" * 80)
print("ANALYZING UPDATED DATASET FOR COMMON PRODUCTS")
print("=" * 80)

# Load the dataset
df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

# Separate by platform
amazon = df[df['platform'] == 'Amazon']
flipkart = df[df['platform'] == 'Flipkart']

print(f"\n📊 Dataset Summary:")
print(f"   Total Products: {len(df)}")
print(f"   Amazon Products: {len(amazon)}")
print(f"   Flipkart Products: {len(flipkart)}")

# Find common brands
amazon_brands = set(amazon['brand'].dropna().str.strip().str.lower().unique())
flipkart_brands = set(flipkart['brand'].dropna().str.strip().str.lower().unique())
common_brands = amazon_brands & flipkart_brands

print(f"\n🏷️  Brand Analysis:")
print(f"   Amazon Unique Brands: {len(amazon_brands)}")
print(f"   Flipkart Unique Brands: {len(flipkart_brands)}")
print(f"   Common Brands: {len(common_brands)}")

if len(common_brands) > 0:
    print(f"\n   Common Brands Found:")
    for brand in sorted(list(common_brands))[:20]:
        amazon_count = len(amazon[amazon['brand'].str.lower().str.strip() == brand])
        flipkart_count = len(flipkart[flipkart['brand'].str.lower().str.strip() == brand])
        print(f"      - {brand.title()}: Amazon({amazon_count}) | Flipkart({flipkart_count})")

# Find common categories
amazon_cats = set(amazon['bb category'].dropna().str.strip().str.lower().unique())
flipkart_cats = set(flipkart['bb category'].dropna().str.strip().str.lower().unique())
common_cats = amazon_cats & flipkart_cats

print(f"\n📁 Category Analysis:")
print(f"   Amazon Unique Categories: {len(amazon_cats)}")
print(f"   Flipkart Unique Categories: {len(flipkart_cats)}")
print(f"   Common Categories: {len(common_cats)}")

if len(common_cats) > 0:
    print(f"\n   Common Categories Found:")
    for cat in sorted(list(common_cats))[:15]:
        amazon_count = len(amazon[amazon['bb category'].str.lower().str.strip() == cat])
        flipkart_count = len(flipkart[flipkart['bb category'].str.lower().str.strip() == cat])
        print(f"      - {cat.title()}: Amazon({amazon_count}) | Flipkart({flipkart_count})")

# Find products with similar names (common keywords)
print(f"\n🔍 Finding Common Product Keywords...")

# Get all product titles
amazon_titles = amazon['product title'].dropna().str.lower()
flipkart_titles = flipkart['product title'].dropna().str.lower()

# Extract common words (3+ characters)
def extract_words(titles):
    words = set()
    for title in titles:
        words.update([w for w in str(title).split() if len(w) > 3])
    return words

amazon_words = extract_words(amazon_titles)
flipkart_words = extract_words(flipkart_titles)
common_words = amazon_words & flipkart_words

print(f"   Common Keywords Found: {len(common_words)}")

# Test top common keywords
top_keywords = sorted(list(common_words))[:30]
print(f"\n📋 Top 10 Search Terms for Comparison:")

recommendations = []
for keyword in top_keywords:
    amazon_matches = amazon[amazon['product title'].str.contains(keyword, case=False, na=False)]
    flipkart_matches = flipkart[flipkart['product title'].str.contains(keyword, case=False, na=False)]
    
    if len(amazon_matches) > 0 and len(flipkart_matches) > 0:
        recommendations.append({
            'keyword': keyword,
            'amazon': len(amazon_matches),
            'flipkart': len(flipkart_matches),
            'total': len(amazon_matches) + len(flipkart_matches)
        })

# Sort by total matches
recommendations.sort(key=lambda x: x['total'], reverse=True)

for i, rec in enumerate(recommendations[:10], 1):
    print(f"   {i}. '{rec['keyword']}' - Amazon: {rec['amazon']} | Flipkart: {rec['flipkart']} | Total: {rec['total']}")

# Check for exact product matches
print(f"\n🔗 Checking for Exact Product Matches...")
amazon_title_set = set(amazon['product title'].dropna().str.lower().str.strip())
flipkart_title_set = set(flipkart['product title'].dropna().str.lower().str.strip())
exact_matches = amazon_title_set & flipkart_title_set

print(f"   Exact Product Title Matches: {len(exact_matches)}")
if len(exact_matches) > 0:
    print(f"   Sample Matches:")
    for match in list(exact_matches)[:5]:
        print(f"      - {match[:60]}")

print("\n" + "=" * 80)
print("✅ Analysis Complete!")
print("=" * 80)


