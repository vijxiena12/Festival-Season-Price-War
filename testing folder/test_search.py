import pandas as pd

# Load the dataset
df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')

print("Total rows:", len(df))
print("\nSearching for 'Maggi'...")

# Test search
query = 'maggi'
mask = (
    df['product title'].str.lower().str.contains(query, na=False, regex=False) |
    df['product description'].str.lower().str.contains(query, na=False, regex=False) |
    df['brand'].str.lower().str.contains(query, na=False, regex=False)
)

results = df[mask]
print(f"Found {len(results)} results")
print("\nResults:")
print(results[['product title', 'brand', 'price', 'site name']])

print("\n\nSearching for 'Himalaya'...")
query = 'himalaya'
mask = (
    df['product title'].str.lower().str.contains(query, na=False, regex=False) |
    df['product description'].str.lower().str.contains(query, na=False, regex=False) |
    df['brand'].str.lower().str.contains(query, na=False, regex=False)
)

results = df[mask]
print(f"Found {len(results)} results")
print("\nResults:")
print(results[['product title', 'brand', 'price', 'site name']])

print("\n\nSearching for 'Dove'...")
query = 'dove'
mask = (
    df['product title'].str.lower().str.contains(query, na=False, regex=False) |
    df['product description'].str.lower().str.contains(query, na=False, regex=False) |
    df['brand'].str.lower().str.contains(query, na=False, regex=False)
)

results = df[mask]
print(f"Found {len(results)} results")
print("\nResults:")
print(results[['product title', 'brand', 'price', 'site name']])
