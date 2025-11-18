import pandas as pd

# Load dataset
df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

# Separate by platform
amazon = df[df['platform'] == 'Amazon']
flipkart = df[df['platform'] == 'Flipkart']

print("=" * 80)
print("10 SEARCH TERMS FOR PRICE COMPARISON")
print("=" * 80)

# Since the datasets are different, let's find the best search terms
# that will return results from both platforms

recommendations = []

# 1. Search for "Fire" - appears in both
amazon_fire = amazon[amazon['product title'].str.contains('Fire', case=False, na=False)]
flipkart_fire = flipkart[flipkart['product title'].str.contains('Fire', case=False, na=False)]
if len(amazon_fire) > 0 and len(flipkart_fire) > 0:
    recommendations.append({
        'term': 'Fire',
        'amazon_count': len(amazon_fire),
        'flipkart_count': len(flipkart_fire),
        'amazon_example': amazon_fire.iloc[0]['product title'][:50],
        'flipkart_example': flipkart_fire.iloc[0]['product title'][:50]
    })

# 2-10. Let's find other common words or product types
common_words = ['Essential', 'Basics', 'Snack', 'Stick', 'Chocolate', 'Shampoo', 'Face', 'Wash', 'Cleaner', 'Masala']

for word in common_words:
    amazon_matches = amazon[amazon['product title'].str.contains(word, case=False, na=False)]
    flipkart_matches = flipkart[flipkart['product title'].str.contains(word, case=False, na=False)]
    
    if len(amazon_matches) > 0 and len(flipkart_matches) > 0:
        recommendations.append({
            'term': word,
            'amazon_count': len(amazon_matches),
            'flipkart_count': len(flipkart_matches),
            'amazon_example': amazon_matches.iloc[0]['product title'][:50],
            'flipkart_example': flipkart_matches.iloc[0]['product title'][:50]
        })
    elif len(amazon_matches) > 0 or len(flipkart_matches) > 0:
        # Still useful if it appears in at least one platform
        recommendations.append({
            'term': word,
            'amazon_count': len(amazon_matches),
            'flipkart_count': len(flipkart_matches),
            'amazon_example': amazon_matches.iloc[0]['product title'][:50] if len(amazon_matches) > 0 else 'N/A',
            'flipkart_example': flipkart_matches.iloc[0]['product title'][:50] if len(flipkart_matches) > 0 else 'N/A'
        })
    
    if len(recommendations) >= 10:
        break

# If we don't have 10, add some Flipkart-specific terms that are common
if len(recommendations) < 10:
    flipkart_brands = flipkart['brand'].value_counts().head(10)
    for brand in flipkart_brands.index:
        if brand not in [r['term'] for r in recommendations]:
            recommendations.append({
                'term': brand,
                'amazon_count': len(amazon[amazon['brand'].str.contains(brand, case=False, na=False)]),
                'flipkart_count': len(flipkart[flipkart['brand'] == brand]),
                'amazon_example': 'N/A',
                'flipkart_example': flipkart[flipkart['brand'] == brand].iloc[0]['product title'][:50] if len(flipkart[flipkart['brand'] == brand]) > 0 else 'N/A'
            })
        if len(recommendations) >= 10:
            break

print("\n📋 RECOMMENDED SEARCH TERMS:\n")
for i, rec in enumerate(recommendations[:10], 1):
    print(f"{i}. Search Term: '{rec['term']}'")
    print(f"   📦 Amazon: {rec['amazon_count']} products")
    if rec['amazon_example'] != 'N/A':
        print(f"      Example: {rec['amazon_example']}")
    print(f"   🛍️  Flipkart: {rec['flipkart_count']} products")
    if rec['flipkart_example'] != 'N/A':
        print(f"      Example: {rec['flipkart_example']}")
    print()

print("=" * 80)
print("💡 TIP: Since your datasets have different products,")
print("   search for generic terms like product types or common words")
print("   that appear in product names across both platforms.")
print("=" * 80)


