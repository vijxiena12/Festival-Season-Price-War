"""Verify the dataset is ready for search comparison"""
import pandas as pd

print("=" * 80)
print("VERIFYING DATASET FOR SEARCH COMPARISON")
print("=" * 80)

try:
    df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')
    
    print(f"\n✅ Dataset loaded successfully!")
    print(f"   Total rows: {len(df)}")
    
    # Check required columns
    required_cols = ['platform', 'product title', 'final_price', 'mrp']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"\n❌ Missing required columns: {missing_cols}")
    else:
        print(f"\n✅ All required columns present")
    
    # Check platform distribution
    if 'platform' in df.columns:
        platform_counts = df['platform'].value_counts()
        print(f"\n📊 Platform Distribution:")
        for platform, count in platform_counts.items():
            print(f"   {platform}: {count} products")
        
        # Check if both platforms exist
        platforms = set(platform_counts.index)
        if 'Amazon' in platforms and 'Flipkart' in platforms:
            print(f"\n✅ Both Amazon and Flipkart data present")
        else:
            print(f"\n⚠️  Missing platforms. Found: {platforms}")
    
    # Check price columns
    if 'final_price' in df.columns:
        price_valid = df['final_price'].notna().sum()
        print(f"\n💰 Price Data:")
        print(f"   Products with valid final_price: {price_valid} / {len(df)}")
    
    if 'mrp' in df.columns:
        mrp_valid = df['mrp'].notna().sum()
        print(f"   Products with valid mrp: {mrp_valid} / {len(df)}")
    
    # Check search columns
    search_cols = ['product title', 'brand']
    print(f"\n🔍 Search Capabilities:")
    for col in search_cols:
        if col in df.columns:
            non_empty = df[col].notna().sum()
            print(f"   {col}: {non_empty} non-empty values")
        else:
            print(f"   ❌ Missing: {col}")
    
    print(f"\n" + "=" * 80)
    print("✅ Dataset verification complete!")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. Restart your API server: python price_api.py")
    print("   2. Test search with: 'Stick' or 'Essential'")
    print("   3. Check the dashboard for comparison results")
    
except FileNotFoundError:
    print(f"\n❌ ERROR: Dataset file not found!")
    print("   Make sure 'combined_amazon_flipkart_with_timestamps.csv' exists")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()


