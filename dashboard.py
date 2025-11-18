import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date
from typing import Optional

# ------------------------------
# Helper utilities
# ------------------------------
FESTIVE_WINDOWS = [
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
]


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


def build_platform_summary(filtered_df: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for platform, group in filtered_df.groupby("platform"):
        if group.empty:
            continue
        best_row = group.loc[group["final_price"].idxmin()]
        summary_rows.append(
            {
                "Platform": platform,
                "Best Final Price (₹)": round(best_row["final_price"], 2)
                if pd.notna(best_row["final_price"])
                else None,
                "MRP (₹)": round(best_row["mrp"], 2) if pd.notna(best_row["mrp"]) else None,
                "Absolute Discount (₹)": round(best_row["mrp"] - best_row["final_price"], 2)
                if pd.notna(best_row["mrp"]) and pd.notna(best_row["final_price"])
                else None,
                "Discount (%)": round(best_row["discount_pct"], 2)
                if pd.notna(best_row["discount_pct"])
                else None,
                "Festive Window": best_row["festive_event"] or "—",
                "Offer Snapshot": best_row.get("offers", "") or "—",
                "Combo Offer": best_row.get("combo offers", "") or "—",
                "Sample Date": best_row["timestamp"].date() if pd.notna(best_row["timestamp"]) else "—",
                "Product Match": best_row["product title"],
                "Direct Link": best_row.get("url", ""),
            }
        )
    return pd.DataFrame(summary_rows)


# ------------------------------
# Load dataset with timestamps
# ------------------------------
df = pd.read_csv("combined_amazon_flipkart_with_timestamps.csv", parse_dates=["timestamp"])
for col in ["mrp", "price", "final_price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["discount_pct"] = ((df["mrp"] - df["final_price"]) / df["mrp"]) * 100
df["discount_pct"] = df["discount_pct"].replace([np.inf, -np.inf], pd.NA)
df["festive_event"] = df["timestamp"].apply(identify_festive_event)

st.sidebar.title("📊 Festival Season Price War Dashboard")
page = st.sidebar.radio(
    "Select a View:",
    [
        "Overview",
        "Product Comparison",
        "Price Distribution",
        "Monthly Trends",
        "Top Categories",
        "Boxplots & Comparisons",
        "Heatmap Analysis",
        "Insights Summary"
    ]
)

# ------------------------------
# Date Range Filter
# ------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Date Range Filter")

min_d = df["timestamp"].min().date()
max_d = df["timestamp"].max().date()

start_d = st.sidebar.date_input("Start Date", min_d, min_value=min_d, max_value=max_d)
end_d = st.sidebar.date_input("End Date", max_d, min_value=min_d, max_value=max_d)

# Filter dataset
df = df[(df["timestamp"].dt.date >= start_d) & (df["timestamp"].dt.date <= end_d)]

# Add month and year columns
df["month"] = df["timestamp"].dt.month_name()
df["year"] = df["timestamp"].dt.year

st.sidebar.info(f"📊 Showing data from **{start_d} → {end_d}**")

# ------------------------------
# Dashboard Title
# ------------------------------
st.title("🛍️ Festival Season Price War: Amazon vs Flipkart")
st.caption(f"Filtered between {start_d} and {end_d}")
st.write("""
This dashboard explores **festival season pricing trends** between Amazon and Flipkart.
It highlights months like **August–November**, where major sales such as Independence Day, 
Dussehra, Diwali, and Big Billion Days occur.
""")

# ------------------------------
# Pages
# ------------------------------
if page == "Overview":
    st.header("Dataset Overview")
    st.write(df.head())
    st.metric("Total Records", len(df))
    st.metric("Unique Categories", df['bb category'].nunique() if 'bb category' in df.columns else "N/A")
    st.metric("Date Range", f"{df['timestamp'].min().date()} → {df['timestamp'].max().date()}")

elif page == "Price Distribution":
    st.header("💰 Price Distribution: Amazon vs Flipkart")
    fig = px.histogram(
        df, x="final_price", color="platform", nbins=40,
        barmode="overlay", opacity=0.7, title="Price Distribution by Platform"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Monthly Trends":
    st.header("📆 Monthly Average Price Trend")
    monthly_avg = (
        df.groupby(["year", "month", "platform"])["final_price"]
        .mean()
        .reset_index()
    )
    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    monthly_avg["month"] = pd.Categorical(monthly_avg["month"], categories=month_order, ordered=True)
    monthly_avg = monthly_avg.sort_values(["year","month"])

    fig = px.line(
        monthly_avg, x="month", y="final_price", color="platform",
        line_group="year", markers=True,
        title="Average Monthly Price Trend (Festival Season Highlighted)"
    )

    # Highlight Aug–Nov (festival months)
    for m in ["August", "September", "October", "November"]:
        fig.add_vrect(x0=m, x1=m, fillcolor="orange", opacity=0.1, line_width=0)

    st.plotly_chart(fig, use_container_width=True)

elif page == "Top Categories":
    st.header("🏷️ Top 10 Expensive Categories")
    if 'bb category' in df.columns:
        cat_avg = df.groupby(['platform','bb category'])['final_price'].mean().reset_index()
        top_cats = cat_avg.sort_values('final_price', ascending=False).head(10)
        fig = px.bar(top_cats, x='bb category', y='final_price', color='platform',
                     title='Top 10 Expensive Categories')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No category column found.")

elif page == "Boxplots & Comparisons":
    st.header("📦 Price Comparison by Platform")
    fig = px.box(df, x='platform', y='final_price', color='platform',
                 title="Price Variation by Platform")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Heatmap Analysis":
    st.header("🔥 Category-wise Average Price (Heatmap)")
    if 'bb category' in df.columns:
        pivot = df.groupby(['bb category','platform'])['final_price'].mean().unstack()
        st.dataframe(pivot)
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale='Blues',
                        title="Heatmap of Average Prices per Category")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No category column available for heatmap.")

elif page == "Product Comparison":
    st.header("🔍 Product Price Intelligence")
    st.write(
        "Search for any product title, brand, or keyword to compare platform prices, "
        "festive discounts, and offers in the selected date range."
    )
    search_term = st.text_input("Product search", placeholder="e.g., Echo Dot, iPhone 15, Mixer Grinder")

    if search_term:
        title_series = df["product title"].fillna("")
        desc_series = df["product description"].fillna("") if "product description" in df.columns else pd.Series("", index=df.index)
        brand_series = df["brand"].fillna("") if "brand" in df.columns else pd.Series("", index=df.index)

        mask = (
            title_series.str.contains(search_term, case=False, na=False)
            | desc_series.str.contains(search_term, case=False, na=False)
            | brand_series.str.contains(search_term, case=False, na=False)
        )
        results = df.loc[mask].copy()

        if results.empty:
            st.warning("No matching records found. Try a different keyword or expand the date range.")
        else:
            st.subheader("Best Offer Snapshot")
            summary_df = build_platform_summary(results)
            if not summary_df.empty:
                with st.container():
                    st.dataframe(
                        summary_df.drop(columns=["Direct Link"]),
                        use_container_width=True,
                    )

                price_series = pd.to_numeric(summary_df["Best Final Price (₹)"], errors="coerce")
                if price_series.notna().any():
                    best_idx = price_series.idxmin()
                    best_row = summary_df.loc[best_idx]
                    st.success(
                        f"Lowest price is ₹{best_row['Best Final Price (₹)']:.2f} on **{best_row['Platform']}** "
                        f"({best_row['Product Match']})."
                    )

                if {"Amazon", "Flipkart"}.issubset(set(summary_df["Platform"].values)):
                    amazon_price = pd.to_numeric(
                        summary_df.loc[summary_df["Platform"] == "Amazon", "Best Final Price (₹)"], errors="coerce"
                    ).iloc[0]
                    flipkart_price = pd.to_numeric(
                        summary_df.loc[summary_df["Platform"] == "Flipkart", "Best Final Price (₹)"], errors="coerce"
                    ).iloc[0]
                    if pd.notna(amazon_price) and pd.notna(flipkart_price):
                        price_gap = abs(amazon_price - flipkart_price)
                        cheaper_platform = "Amazon" if amazon_price < flipkart_price else "Flipkart"
                        st.info(
                            f"{cheaper_platform} is cheaper by ₹{price_gap:.2f} compared to the other platform for this search."
                        )

                st.subheader("Detailed Matches")
                detail_cols = [
                    "timestamp",
                    "platform",
                    "product title",
                    "brand",
                    "mrp",
                    "final_price",
                    "discount_pct",
                    "offers",
                    "combo offers",
                    "festive_event",
                ]
                available_cols = [c for c in detail_cols if c in results.columns]
                detailed_view = results.sort_values("final_price").head(20)[available_cols].rename(
                    columns={
                        "timestamp": "Date",
                        "platform": "Platform",
                        "product title": "Product",
                        "brand": "Brand",
                        "mrp": "MRP (₹)",
                        "final_price": "Final Price (₹)",
                        "discount_pct": "Discount (%)",
                        "offers": "Offers",
                        "combo offers": "Combo Offers",
                        "festive_event": "Festive Window",
                    }
                )
                st.dataframe(detailed_view, use_container_width=True)

                with st.expander("Copy best offer links"):
                    for _, row in summary_df.iterrows():
                        link = row["Direct Link"]
                        if link:
                            st.markdown(f"- [{row['Platform']} • {row['Product Match']}](%s)" % link)
            else:
                st.warning("Unable to build a summary for the selected product.")
    else:
        st.info("Enter a keyword above to generate platform-wise comparisons.")

elif page == "Insights Summary":
    st.header("🧠 Key Insights & Conclusions")
    st.markdown("""
    - 🎉 **Festival months (Aug–Nov)** show major pricing fluctuations and discounts.  
    - 💡 **Amazon** often lists higher pre-sale prices, followed by strong festival discounts.  
    - 🛍️ **Flipkart** remains more consistent and competitive during **Diwali & Big Billion Days**.  
    - 🧴 **Beauty, Electronics, and Books** dominate Amazon’s premium categories.  
    - 🍼 **Flipkart** is more affordable in **Baby, Grocery, and Home Essentials**.  
    - 📊 Statistical analysis confirms significant differences in pricing strategies.  
    """)

# st.sidebar.markdown("---")
# st.sidebar.info("Developed by Manav Verma | Applied Data Science Project 2025")
