from flask import Flask, jsonify, request
import pandas as pd
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the dataset
print("Loading dataset...")
try:
    df = pd.read_csv('combined_amazon_flipkart_with_timestamps.csv')
    df['timestamp'] = pd.to_datetime(df.get('timestamp', '2024-01-01'))  # Add default date if missing
    print(f"✅ Dataset loaded: {len(df)} rows")
    print("Columns:", df.columns.tolist())
    print(f"Platforms: {df['site name'].unique()}")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    df = pd.DataFrame()

@app.route('/api/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify({"error": "Please provide a search term (q parameter)"}), 400

        print(f"\n🔍 Searching for: '{query}'")
        
        # Search in title, description, and brand (case-insensitive, partial match)
        mask = (
            df['product title'].str.lower().str.contains(query, na=False, regex=False) |
            df['product description'].str.lower().str.contains(query, na=False, regex=False) |
            df['brand'].str.lower().str.contains(query, na=False, regex=False)
        )
        
        results = df[mask].copy()
        print(f"✅ Found {len(results)} results for query: '{query}'")
        if len(results) > 0:
            breakdown = results['site name'].value_counts().to_dict()
            print(f"   Breakdown: {breakdown}")
            print(f"   Amazon: {breakdown.get('amazon_com', 0)}, Flipkart: {breakdown.get('flipkart_com', 0)}")
        else:
            print(f"   ⚠️  No results found!")
        
        # Format the response - include all necessary fields
        # Convert to dict and clean up any problematic characters
        results_list = []
        for _, row in results.iterrows():
            results_list.append({
                'product title': str(row.get('product title', '')).replace('\n', ' ').replace('\r', ''),
                'product description': str(row.get('product description', '')).replace('\n', ' ').replace('\r', ''),
                'brand': str(row.get('brand', '')).replace('\n', ' ').replace('\r', ''),
                'price': float(row.get('price', 0)) if pd.notna(row.get('price')) else 0,
                'site name': str(row.get('site name', '')).replace('\n', ' ').replace('\r', ''),
                'url': str(row.get('url', '')).replace('\n', ' ').replace('\r', ''),
                'offers': str(row.get('offers', '')).replace('\n', ' ').replace('\r', '') if pd.notna(row.get('offers')) else '',
                'combo offers': str(row.get('combo offers', '')).replace('\n', ' ').replace('\r', '') if pd.notna(row.get('combo offers')) else ''
            })
        
        response = {
            "query": query,
            "results": results_list
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in search_products: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🌐 Starting server on http://localhost:{port}")
    print("Endpoints:")
    print(f"  - GET /api/search?q=your+search+term")
    print("\nPress Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=port, debug=True)
