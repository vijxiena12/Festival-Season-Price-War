import pandas as pd

# Load the dataset
df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

products = [
    'Samsung 10000mAh Power Bank',
    'boAt Airdopes 131',
    'Mi 3A Fast Charger',
    'Dove Intense Repair Shampoo 650ml',
    'Nivea Soft Light Moisturizer 200ml',
    'Himalaya Purifying Neem Face Wash 150ml',
    'Cadbury Dairy Milk Silk 60g',
    'Nestlé Maggi 12 Pack',
    'Harpic Bathroom Cleaner 1L',
    'Surf Excel Matic Detergent 2kg'
]

search_terms = [
    'samsung',
    'boat',
    'mi 3a',
    'dove',
    'nivea',
    'himalaya',
    'cadbury',
    'maggi',
    'harpic',
    'surf'
]

for search_term in search_terms:
    query = search_term.lower()
    mask = (
        df['product title'].str.lower().str.contains(query, na=False, regex=False) |
        df['product description'].str.lower().str.contains(query, na=False, regex=False) |
        df['brand'].str.lower().str.contains(query, na=False, regex=False)
    )
    
    results = df[mask]
    amazon_count = len(results[results['site name'] == 'amazon_com'])
    flipkart_count = len(results[results['site name'] == 'flipkart_com'])
    
    print(f"✅ '{search_term}': {len(results)} total results (Amazon: {amazon_count}, Flipkart: {flipkart_count})")
