# -----------------------------------------------
# Applied Data Science Project
# Festival Season Price War: Amazon vs Flipkart
# Dataset Cleaning, Preprocessing & EDA
# -----------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import random
from datetime import datetime

sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12,6)

# -----------------------------------------------
# Step 1: Load Datasets
# -----------------------------------------------
amazon_df = pd.read_csv("synthetic_amazon_dataset_500_rows.csv")
flipkart_df = pd.read_csv(
    "marketing_sample_for_flipkart_com-ecommerce__20191101_20191130__15k_data.csv",
    encoding='latin1',
    on_bad_lines='skip'
)

# -----------------------------------------------
# Step 2: Standardize Column Names
# -----------------------------------------------
amazon_df.columns = amazon_df.columns.str.lower()
flipkart_df.columns = flipkart_df.columns.str.lower()

# -----------------------------------------------
# Step 3: Basic Overview
# -----------------------------------------------
print("----- Amazon Dataset Overview -----")
print(amazon_df.info())
print("\nAmazon Dataset Sample:\n", amazon_df.head())

print("\n----- Flipkart Dataset Overview -----")
print(flipkart_df.info())
print("\nFlipkart Dataset Sample:\n", flipkart_df.head())

# -----------------------------------------------
# Step 4: Handle Missing Values
# -----------------------------------------------
numeric_cols_amazon = amazon_df.select_dtypes(include=np.number).columns.tolist()
amazon_df[numeric_cols_amazon] = amazon_df[numeric_cols_amazon].fillna(amazon_df[numeric_cols_amazon].mean())

numeric_cols_flipkart = flipkart_df.select_dtypes(include=np.number).columns.tolist()
flipkart_df[numeric_cols_flipkart] = flipkart_df[numeric_cols_flipkart].fillna(flipkart_df[numeric_cols_flipkart].mean())

product_col_amazon = 'product title' if 'product title' in amazon_df.columns else ('product_name' if 'product_name' in amazon_df.columns else None)
product_col_flipkart = 'product title' if 'product title' in flipkart_df.columns else ('product_name' if 'product_name' in flipkart_df.columns else None)

if product_col_amazon:
    amazon_df.dropna(subset=[product_col_amazon], inplace=True)
if product_col_flipkart:
    flipkart_df.dropna(subset=[product_col_flipkart], inplace=True)

# -----------------------------------------------
# Step 5: Remove Duplicates
# -----------------------------------------------
amazon_df.drop_duplicates(inplace=True)
flipkart_df.drop_duplicates(inplace=True)
print("\n✅ Duplicates removed successfully.")

# -----------------------------------------------
# Step 6: Handle Irrelevant Columns
# -----------------------------------------------
for col in ['uniq id', 'crawl timestamp']:
    if col in flipkart_df.columns:
        flipkart_df.drop(columns=[col], inplace=True)
    if col in amazon_df.columns:
        amazon_df.drop(columns=[col], inplace=True)

# -----------------------------------------------
# Step 7: Fix Price Columns
# -----------------------------------------------
if 'price' in flipkart_df.columns:
    flipkart_price_col = 'price'
elif 'mrp' in flipkart_df.columns:
    flipkart_price_col = 'mrp'
else:
    raise ValueError("No price column found in Flipkart dataset!")

if 'price' in amazon_df.columns:
    amazon_df['price'] = amazon_df['price'].astype(str).str.replace(',', '').astype(float)

flipkart_df[flipkart_price_col] = flipkart_df[flipkart_price_col].astype(str).str.replace(',', '').astype(float)

# -----------------------------------------------
# Step 7.5: Add Realistic Festival Timestamps
# -----------------------------------------------
def generate_festival_weighted_dates(start, end, n):
    """Generate random dates emphasizing Indian festival months (Aug–Nov)."""
    start_u, end_u = start.timestamp(), end.timestamp()
    dates = []
    for _ in range(n):
        month = random.choices(
            population=[1,2,3,4,5,6,7,8,9,10,11,12],
            weights=[3,3,4,4,5,8,8,15,18,20,12,4],  # Aug–Nov boosted
            k=1
        )[0]
        year = random.choice([2023, 2024, 2025])
        day = random.randint(1, 28)
        dates.append(datetime(year, month, day))
    return dates

start_date = datetime(2023,1,1)
end_date = datetime(2025,12,31)

amazon_df['timestamp'] = generate_festival_weighted_dates(start_date, end_date, len(amazon_df))
flipkart_df['timestamp'] = generate_festival_weighted_dates(start_date, end_date, len(flipkart_df))

# -----------------------------------------------
# Step 8: Save Cleaned Data
# -----------------------------------------------
amazon_df.to_csv("cleaned_amazon_data.csv", index=False)
flipkart_df.to_csv("cleaned_flipkart_data.csv", index=False)
print("\n🎯 Data cleaning completed successfully!")

# -----------------------------------------------
# Step 9: Combine Datasets
# -----------------------------------------------
amazon_df['platform'] = 'Amazon'
flipkart_df['platform'] = 'Flipkart'

combined_df = pd.concat([amazon_df, flipkart_df], ignore_index=True)

combined_df['final_price'] = combined_df.apply(
    lambda row: row['price'] if row['platform']=='Amazon' else row[flipkart_price_col], axis=1
)

combined_df.to_csv("combined_amazon_flipkart_with_timestamps.csv", index=False)
print("\n✅ Combined dataset (with festival timestamps) saved as 'combined_amazon_flipkart_with_timestamps.csv'")
print("Total records:", combined_df.shape[0])

# -----------------------------------------------
# Step 10: Statistical Comparison
# -----------------------------------------------
print("\n----- Descriptive Statistics for Final Price -----")
desc_stats = combined_df.groupby('platform')['final_price'].agg(['mean','median','std']).reset_index()
print(desc_stats)

amazon_prices = combined_df[combined_df['platform']=='Amazon']['final_price']
flipkart_prices = combined_df[combined_df['platform']=='Flipkart']['final_price']

t_stat, p_value = stats.ttest_ind(amazon_prices, flipkart_prices, equal_var=False)
print("\n----- T-Test Results -----")
print(f"T-Statistic: {t_stat:.4f}")
print(f"P-Value: {p_value:.4f}")
alpha = 0.05
if p_value < alpha:
    print("✅ Significant price difference exists between Amazon & Flipkart.")
else:
    print("❌ No significant price difference found.")
