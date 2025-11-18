from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS


FESTIVE_WINDOWS: Tuple[Dict[str, Any], ...] = (
    {
        "name": "Republic Day Specials",
        "start": (1, 15),
        "end": (1, 31),
    },
    {
        "name": "Holi Dhamaka",
        "start": (3, 1),
        "end": (3, 15),
    },
    {
        "name": "Summer Savings",
        "start": (5, 1),
        "end": (5, 15),
    },
    {
        "name": "Independence Day Mega Deals",
        "start": (8, 1),
        "end": (8, 31),
    },
    {
        "name": "Navratri Savings",
        "start": (10, 1),
        "end": (10, 20),
    },
    {
        "name": "Diwali & Big Billion Days",
        "start": (10, 21),
        "end": (11, 15),
    },
    {
        "name": "Black Friday & Cyber Week",
        "start": (11, 16),
        "end": (11, 30),
    },
    {
        "name": "Christmas & New Year Offers",
        "start": (12, 1),
        "end": (12, 31),
    },
)


def identify_festive_event(ts: Optional[pd.Timestamp]) -> Optional[str]:
    if pd.isna(ts):
        return None

    current_date = ts.date()
    for window in FESTIVE_WINDOWS:
        start = date(current_date.year, *window["start"])
        end = date(current_date.year, *window["end"])
        if start <= current_date <= end:
            return window["name"]
    return None


def load_dataset() -> pd.DataFrame:
    try:
        print("Loading dataset...")
        df = pd.read_csv(
            "combined_amazon_flipkart_with_timestamps.csv", parse_dates=["timestamp"]
        )
        print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")

        # Normalize column names (handle case variations)
        df.columns = df.columns.str.strip()
        
        # Try different possible column name variations
        price_cols = []
        for col in df.columns:
            col_lower = col.lower()
            if 'price' in col_lower and 'final' not in col_lower and 'mrp' not in col_lower:
                price_cols.append(col)
            elif 'final_price' in col_lower or 'final price' in col_lower:
                if 'final_price' not in df.columns:
                    df['final_price'] = df[col]
            elif 'mrp' in col_lower:
                if 'mrp' not in df.columns:
                    df['mrp'] = df[col]

        # Ensure required columns exist
        if 'final_price' not in df.columns:
            # Try to find price column
            for col in df.columns:
                if 'price' in col.lower() and 'final' not in col.lower():
                    df['final_price'] = df[col]
                    break
        
        if 'mrp' not in df.columns:
            df['mrp'] = df.get('final_price', pd.Series([0] * len(df)))
        
        if 'price' not in df.columns:
            df['price'] = df.get('final_price', pd.Series([0] * len(df)))

        # Convert to numeric
        for col in ("price", "final_price", "mrp"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Calculate discount
        if 'mrp' in df.columns and 'final_price' in df.columns:
            df["discount_pct"] = ((df["mrp"] - df["final_price"]) / df["mrp"]) * 100
            df["discount_pct"] = df["discount_pct"].replace([np.inf, -np.inf], pd.NA)
        else:
            df["discount_pct"] = pd.NA

        # Add festive event
        if "festive_event" not in df.columns or df["festive_event"].isna().all():
            if 'timestamp' in df.columns:
                df["festive_event"] = df["timestamp"].apply(identify_festive_event)
            else:
                df["festive_event"] = None

        # Create search blob
        product_title_col = None
        for col in df.columns:
            if 'product' in col.lower() and 'title' in col.lower():
                product_title_col = col
                break
        
        product_desc_col = None
        for col in df.columns:
            if 'product' in col.lower() and 'description' in col.lower():
                product_desc_col = col
                break
        
        brand_col = None
        for col in df.columns:
            if col.lower() == 'brand':
                brand_col = col
                break

        df["search_blob"] = (
            df.get(product_title_col or "product title", pd.Series([""] * len(df)))
            .fillna("")
            .astype(str)
            .str.cat(df.get(product_desc_col or "product description", pd.Series([""] * len(df))).fillna("").astype(str), sep=" ")
            .str.cat(df.get(brand_col or "brand", pd.Series([""] * len(df))).fillna("").astype(str), sep=" ")
        )

        print("Dataset processing completed successfully!")
        return df
    except FileNotFoundError:
        print("ERROR: CSV file 'combined_amazon_flipkart_with_timestamps.csv' not found!")
        print("Please make sure the file exists in the same directory as price_api.py")
        raise
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        import traceback
        traceback.print_exc()
        raise


try:
    DATAFRAME = load_dataset()
    print(f"✅ Dataset ready: {len(DATAFRAME)} rows loaded")
except Exception as e:
    print(f"❌ Failed to load dataset: {e}")
    DATAFRAME = pd.DataFrame()  # Empty dataframe as fallback

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Custom JSON encoder to handle NaN values
import json
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        if pd.isna(obj):
            return None
        return super().default(obj)

app.json = CustomJSONProvider(app)


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, (float, int, np.floating, np.integer)):
            if math.isnan(float(value)):
                return None
            return float(value)
        parsed = float(str(value))
        if math.isnan(parsed):
            return None
        return parsed
    except (TypeError, ValueError):
        return None


def _format_currency(value: Optional[float]) -> Optional[float]:
    clean = _safe_float(value)
    if clean is None:
        return None
    return round(clean, 2)


def clean_json_value(val):
    """Convert NaN, None, and invalid values to None for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if pd.isna(val):
        return None
    return val

def build_platform_summary(filtered_df: pd.DataFrame) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for platform, group in filtered_df.groupby("platform"):
        candidates = group.dropna(subset=["final_price"])
        if candidates.empty:
            continue
        best_row = candidates.loc[candidates["final_price"].idxmin()]
        mrp = _safe_float(best_row.get("mrp"))
        final_price = _safe_float(best_row.get("final_price"))
        discount_pct = _safe_float(best_row.get("discount_pct"))
        discount_abs = None
        if mrp is not None and final_price is not None:
            discount_abs = round(mrp - final_price, 2)

        # Find product title column
        product_title_col = None
        for col in best_row.index:
            if 'product' in col.lower() and 'title' in col.lower():
                product_title_col = col
                break

        summaries.append(
            {
                "platform": platform,
                "best_final_price": _format_currency(final_price),
                "mrp": _format_currency(mrp),
                "discount_absolute": _format_currency(discount_abs),
                "discount_percent": round(discount_pct, 2) if discount_pct is not None else None,
                "festive_window": clean_json_value(best_row.get("festive_event")),
                "sample_date": best_row.get("timestamp").date().isoformat()
                if pd.notnull(best_row.get("timestamp"))
                else None,
                "product_match": clean_json_value(best_row.get(product_title_col or "product title")),
                "offers": clean_json_value(best_row.get("offers")) or "",
                "combo_offers": clean_json_value(best_row.get("combo offers")) or "",
                "direct_link": clean_json_value(best_row.get("url")) or "",
            }
        )
    return summaries


def build_match_rows(filtered_df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    try:
        if filtered_df.empty or 'final_price' not in filtered_df.columns:
            return []
        
        # Find column names (case-insensitive)
        col_map = {}
        for col in filtered_df.columns:
            col_lower = col.lower()
            if 'timestamp' in col_lower:
                col_map['timestamp'] = col
            elif col_lower == 'platform':
                col_map['platform'] = col
            elif 'product' in col_lower and 'title' in col_lower:
                col_map['product_title'] = col
            elif col_lower == 'brand':
                col_map['brand'] = col
            elif 'bb category' in col_lower or (col_lower == 'category' or 'category' in col_lower):
                col_map['category'] = col
            elif col_lower == 'mrp':
                col_map['mrp'] = col
            elif 'final_price' in col_lower or 'final price' in col_lower:
                col_map['final_price'] = col
            elif 'discount' in col_lower and 'pct' in col_lower:
                col_map['discount_pct'] = col
            elif 'offers' in col_lower and 'combo' not in col_lower:
                col_map['offers'] = col
            elif 'combo' in col_lower and 'offers' in col_lower:
                col_map['combo_offers'] = col
            elif 'festive' in col_lower:
                col_map['festive_event'] = col
            elif 'url' in col_lower or 'link' in col_lower:
                col_map['url'] = col

        # Sort and limit
        sorted_df = filtered_df.sort_values(col_map.get('final_price', 'final_price')).head(limit)
        
        rows = []
        for _, row in sorted_df.iterrows():
            # Get timestamp
            date_val = None
            if 'timestamp' in col_map:
                ts = row.get(col_map['timestamp'])
                if pd.notnull(ts):
                    try:
                        if hasattr(ts, 'date'):
                            date_val = ts.date().isoformat()
                        else:
                            date_val = str(ts)
                    except:
                        date_val = None
            
            # Get product title
            product = None
            if 'product_title' in col_map:
                product = row.get(col_map['product_title'])
            
            # Helper function to clean NaN values
            def clean_value(val):
                if val is None:
                    return None
                if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                    return None
                if pd.isna(val):
                    return None
                return val
            
            # Get combo_offers and clean it
            combo_offers_col = col_map.get('combo_offers', 'combo offers')
            combo_offers_val = row.get(combo_offers_col) if combo_offers_col in row.index else ""
            # Check if it's NaN using pandas
            if pd.isna(combo_offers_val) or (isinstance(combo_offers_val, float) and math.isnan(combo_offers_val)):
                combo_offers_val = ""
            else:
                combo_offers_val = str(combo_offers_val) if combo_offers_val is not None else ""
            
            # Get offers and clean it
            offers_col = col_map.get('offers', 'offers')
            offers_val = row.get(offers_col) if offers_col in row.index else ""
            # Check if it's NaN using pandas
            if pd.isna(offers_val) or (isinstance(offers_val, float) and math.isnan(offers_val)):
                offers_val = ""
            else:
                offers_val = str(offers_val) if offers_val is not None else ""
            
            rows.append({
                "date": date_val,
                "platform": row.get(col_map.get('platform', 'platform'), 'Unknown'),
                "product": product or "Unknown",
                "brand": clean_value(row.get(col_map.get('brand', 'brand'), None)),
                "category": clean_value(row.get(col_map.get('category', 'category'), None)),
                "mrp": _format_currency(row.get(col_map.get('mrp', 'mrp'))),
                "final_price": _format_currency(row.get(col_map.get('final_price', 'final_price'))),
                "discount_percent": round(_safe_float(row.get(col_map.get('discount_pct', 'discount_pct'))), 2)
                if _safe_float(row.get(col_map.get('discount_pct', 'discount_pct'))) is not None
                else None,
                "offers": offers_val or "",
                "combo_offers": combo_offers_val or "",
                "festive_window": clean_value(row.get(col_map.get('festive_event', 'festive_event'), None)),
                "link": row.get(col_map.get('url', 'url'), "") or "",
            })
        return rows
    except Exception as e:
        print(f"Error in build_match_rows: {e}")
        import traceback
        traceback.print_exc()
        return []


def compute_gap(platform_summaries: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if len(platform_summaries) < 2:
        return None

    filtered = [
        s
        for s in platform_summaries
        if s.get("best_final_price") is not None and s.get("platform")
    ]
    if len(filtered) < 2:
        return None

    sorted_by_price = sorted(filtered, key=lambda item: item["best_final_price"])
    cheapest = sorted_by_price[0]
    runner_up = sorted_by_price[1]

    price_gap = (
        round(runner_up["best_final_price"] - cheapest["best_final_price"], 2)
        if runner_up["best_final_price"] is not None
        else None
    )

    return {
        "cheapest_platform": cheapest["platform"],
        "cheapest_price": cheapest["best_final_price"],
        "next_best_platform": runner_up["platform"],
        "price_gap": price_gap,
    }


@app.get("/api/filters")
def get_filters() -> Any:
    """Get unique categories and brands for filtering, plus date range."""
    try:
        if DATAFRAME.empty:
            return jsonify({"categories": [], "brands": [], "date_range": {"start": None, "end": None}})
        
        categories = []
        brands = []
        date_range = {"start": None, "end": None}
        
        # Get date range from dataset
        if 'timestamp' in DATAFRAME.columns and len(DATAFRAME) > 0:
            try:
                date_range = {
                    "start": DATAFRAME["timestamp"].min().date().isoformat(),
                    "end": DATAFRAME["timestamp"].max().date().isoformat(),
                }
            except:
                pass
        
        # Try to find category column (case-insensitive)
        # Check for 'bb category' first (common in this dataset), then 'category'
        category_col = None
        for col in DATAFRAME.columns:
            col_lower = col.lower()
            if 'bb category' in col_lower or col_lower == 'bb category':
                category_col = col
                break
        # If not found, try regular 'category'
        if not category_col:
            for col in DATAFRAME.columns:
                if 'category' in col.lower() and 'bb' not in col.lower():
                    category_col = col
                    break
        
        if category_col:
            categories = sorted(DATAFRAME[category_col].dropna().unique().tolist())
        
        # Try to find brand column
        brand_col = None
        for col in DATAFRAME.columns:
            if col.lower() == 'brand':
                brand_col = col
                break
        
        if brand_col:
            brands = sorted(DATAFRAME[brand_col].dropna().unique().tolist())
        
        return jsonify({
            "categories": categories,
            "brands": brands,
            "date_range": date_range
        })
    except Exception as e:
        print(f"Error in get_filters: {e}")
        return jsonify({"categories": [], "brands": [], "date_range": {"start": None, "end": None}})


@app.get("/api/price-comparison")
def price_comparison() -> Any:
    try:
        if DATAFRAME.empty:
            return jsonify({
                "error": "Dataset not loaded. Please check the server logs.",
                "query": request.args.get("q", ""),
                "results": [],
                "platform_summary": [],
                "platform_gap": None,
                "best_overall": None,
                "metadata": {"total_matches": 0, "date_range": {"start": None, "end": None}}
            }), 500

        search_term = request.args.get("q", "").strip()
        if not search_term:
            return (
                jsonify({"error": "Missing required query parameter 'q'."}),
                400,
            )

        start_date_str = request.args.get("start")
        end_date_str = request.args.get("end")
        category_filter = request.args.get("category", "").strip()
        brand_filter = request.args.get("brand", "").strip()

        df_subset = DATAFRAME.copy()

        # Date filtering
        if start_date_str and 'timestamp' in df_subset.columns:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
                df_subset = df_subset[df_subset["timestamp"].dt.date >= start_date]
            except (ValueError, AttributeError):
                pass  # Skip date filter if invalid

        if end_date_str and 'timestamp' in df_subset.columns:
            try:
                end_date = datetime.fromisoformat(end_date_str).date()
                df_subset = df_subset[df_subset["timestamp"].dt.date <= end_date]
            except (ValueError, AttributeError):
                pass  # Skip date filter if invalid

        # Find category column (check for 'bb category' first)
        category_col = None
        for col in df_subset.columns:
            col_lower = col.lower()
            if 'bb category' in col_lower or col_lower == 'bb category':
                category_col = col
                break
        # If not found, try regular 'category'
        if not category_col:
            for col in df_subset.columns:
                if 'category' in col.lower() and 'bb' not in col.lower():
                    category_col = col
                    break
        
        # Apply category filter
        if category_filter and category_col:
            df_subset = df_subset[df_subset[category_col].fillna("").astype(str).str.contains(category_filter, case=False, na=False)]
        
        # Find brand column
        brand_col = None
        for col in df_subset.columns:
            if col.lower() == 'brand':
                brand_col = col
                break
        
        # Apply brand filter
        if brand_filter and brand_col:
            df_subset = df_subset[df_subset[brand_col].fillna("").astype(str).str.contains(brand_filter, case=False, na=False)]

        # Find product title column
        product_title_col = None
        for col in df_subset.columns:
            if 'product' in col.lower() and 'title' in col.lower():
                product_title_col = col
                break

        # Build search mask - handle brand variations (boAt/Boat, Nestlé/Nestle, etc.)
        # Normalize search term for better matching
        normalized_search = search_term.strip().lower()
        
        # Handle common brand and product variations
        search_variations = {
            'boat': ['boat', 'bo at', 'bo-at', 'bo_at'],
            'airdropes': ['airdopes', 'air dropes', 'air-dropes'],
            '131': ['131', 'one thirty one', 'one-three-one'],
            'boat airdopes 131': ['boat airdopes 131', 'bo-at airdopes 131', 'boat airdropes 131', 'boat airdopes one three one', 'bo at airdopes 131'],
            'nestle': ['nestle', 'nestlé'],
            'samsung': ['samsung'],
            'mi': ['mi', 'xiaomi'],
            'dove': ['dove'],
            'nivea': ['nivea'],
            'himalaya': ['himalaya'],
            'cadbury': ['cadbury'],
            'harpic': ['harpic'],
            'surf excel': ['surf excel', 'surfexcel', 'surf']
        }
        
        # Get variations for the search term
        search_terms = [normalized_search]
        
        # Add variations for the search term if it matches any key in the variations
        for key, variations in search_variations.items():
            if key in normalized_search:
                for variation in variations:
                    if variation not in search_terms:
                        search_terms.append(variation)
        
        # Also add the individual words as separate search terms
        for word in normalized_search.split():
            if word not in search_terms and len(word) > 2:  # Only add words longer than 2 characters
                search_terms.append(word)
        
        # Build search mask - search in multiple fields
        mask = pd.Series([False] * len(df_subset))
        
        # Search in product titles - boost matches in title by adding them multiple times
        if product_title_col:
            for term in search_terms:
                if len(term) > 2:  # Only search for terms longer than 2 characters
                    title_match = df_subset[product_title_col].fillna("").astype(str).str.contains(term, case=False, na=False, regex=False)
                    mask = mask | title_match
        
        # Search in brands
        if brand_col:
            for term in search_terms:
                if len(term) > 2:  # Only search for terms longer than 2 characters
                    brand_match = df_subset[brand_col].fillna("").astype(str).str.contains(term, case=False, na=False, regex=False)
                    mask = mask | brand_match
        
        # Create a temporary search blob if it doesn't exist
        if 'search_blob' not in df_subset.columns and product_title_col and 'product description' in df_subset.columns and brand_col:
            df_subset['search_blob'] = (
                df_subset[product_title_col].fillna('').astype(str) + ' ' +
                df_subset['product description'].fillna('').astype(str) + ' ' +
                df_subset[brand_col].fillna('').astype(str)
            )
        
        # Search in search blob (title + description + brand) if available
        if 'search_blob' in df_subset.columns:
            for term in search_terms:
                if len(term) > 2:  # Only search for terms longer than 2 characters
                    blob_match = df_subset['search_blob'].fillna("").astype(str).str.contains(term, case=False, na=False, regex=False)
                    mask = mask | blob_match

        filtered = df_subset.loc[mask].copy()
        
        # Debug logging
        print(f"Search term: '{search_term}'")
        print(f"Date filter: start={start_date_str}, end={end_date_str}")
        print(f"After date filter: {len(df_subset)} rows")
        print(f"After search filter: {len(filtered)} rows")
        if len(filtered) > 0:
            print(f"Platforms found: {filtered['platform'].value_counts().to_dict()}")

        if filtered.empty:
            date_range = {"start": None, "end": None}
            if 'timestamp' in DATAFRAME.columns and len(DATAFRAME) > 0:
                try:
                    date_range = {
                        "start": start_date_str or DATAFRAME["timestamp"].min().date().isoformat(),
                        "end": end_date_str or DATAFRAME["timestamp"].max().date().isoformat(),
                    }
                except:
                    pass
            
            return jsonify({
                "query": search_term,
                "results": [],
                "platform_summary": [],
                "platform_gap": None,
                "best_overall": None,
                "metadata": {
                    "total_matches": 0,
                    "date_range": date_range,
                },
            })

        # Filter out rows without final_price
        if 'final_price' in filtered.columns:
            filtered = filtered.dropna(subset=["final_price"])
        else:
            return jsonify({
                "error": "Dataset missing 'final_price' column",
                "query": search_term,
                "results": [],
                "platform_summary": [],
                "platform_gap": None,
                "best_overall": None,
                "metadata": {"total_matches": 0, "date_range": {"start": None, "end": None}}
            }), 500

        platform_summary = build_platform_summary(filtered)
        platform_gap = compute_gap(platform_summary)

        best_row = None
        if not filtered.empty and 'final_price' in filtered.columns:
            try:
                best_idx = filtered["final_price"].idxmin()
                best_row_df = filtered.loc[[best_idx]]
                if not best_row_df.empty:
                    best_row_data = best_row_df.iloc[0]
                    
                    # Get product title
                    product_title = None
                    if product_title_col:
                        product_title = best_row_data.get(product_title_col)
                    
                    # Get platform
                    platform = best_row_data.get("platform", "Unknown")
                    
                    best_row = {
                        "platform": platform,
                        "product": product_title or "Unknown",
                        "final_price": _format_currency(best_row_data.get("final_price")),
                        "mrp": _format_currency(best_row_data.get("mrp")),
                        "discount_absolute": _format_currency(
                            (
                                _safe_float(best_row_data.get("mrp"))
                                - _safe_float(best_row_data.get("final_price"))
                            )
                            if _safe_float(best_row_data.get("mrp")) is not None
                            and _safe_float(best_row_data.get("final_price")) is not None
                            else None
                        ),
                        "discount_percent": round(_safe_float(best_row_data.get("discount_pct")), 2)
                        if _safe_float(best_row_data.get("discount_pct")) is not None
                        else None,
                        "festive_window": best_row_data.get("festive_event"),
                        "date": best_row_data.get("timestamp").date().isoformat()
                        if 'timestamp' in best_row_data and pd.notnull(best_row_data.get("timestamp"))
                        else None,
                        "offers": best_row_data.get("offers") or "",
                    }
            except Exception as e:
                print(f"Error building best_row: {e}")

        matches = build_match_rows(filtered)

        # Get date range
        date_range = {"start": None, "end": None}
        if 'timestamp' in filtered.columns and len(filtered) > 0:
            try:
                date_range = {
                    "start": start_date_str or filtered["timestamp"].min().date().isoformat(),
                    "end": end_date_str or filtered["timestamp"].max().date().isoformat(),
                }
            except:
                pass

        response = {
            "query": search_term,
            "metadata": {
                "total_matches": len(filtered),
                "date_range": date_range,
            },
            "best_overall": best_row,
            "platform_summary": platform_summary,
            "platform_gap": platform_gap,
            "results": matches,
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in price_comparison: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "query": request.args.get("q", ""),
            "results": [],
            "platform_summary": [],
            "platform_gap": None,
            "best_overall": None,
            "metadata": {"total_matches": 0, "date_range": {"start": None, "end": None}}
        }), 500


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🚀 Starting Flask API Server...")
        print("=" * 60)
        
        if DATAFRAME.empty:
            print("⚠️  WARNING: Dataset is empty! Server will start but searches may not work.")
        else:
            print(f"✅ Dataset loaded: {len(DATAFRAME)} rows")
            print(f"📊 Columns: {list(DATAFRAME.columns)[:5]}...")
        
        print("\n🌐 Server will run on:")
        print("   - http://localhost:5000")
        print("   - http://127.0.0.1:5000")
        print("\n📡 API Endpoints:")
        print("   - GET /api/filters")
        print("   - GET /api/price-comparison?q=<search_term>")
        print("\n" + "=" * 60)
        print("Press CTRL+C to stop the server")
        print("=" * 60 + "\n")
        
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

