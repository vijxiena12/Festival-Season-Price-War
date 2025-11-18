# 🎉 Festival Season Price War: Amazon vs Flipkart – Data Analysis  
### By: Anika Kaushik & Xiena Vi

A complete data analysis and visualization project comparing **Amazon** and **Flipkart** prices during India’s festive season.

The system includes:
- ✔ Data Cleaning & Preprocessing  
- ✔ Interactive Dashboard (Streamlit + Plotly)  
- ✔ Product Search & Keyword Recommendation  
- ✔ Amazon vs Flipkart Price Comparison Tool  
- ✔ Website Interface (HTML/CSS/JS)  
- ✔ Visual Insights (Histograms, Line Charts, Heatmaps, Bar Graphs)

---

## 📌 Project Overview

During India's festive months (Aug–Nov), platforms like Amazon and Flipkart launch massive sales such as the **Great Indian Festival** and **Big Billion Days**, leading to dynamic price fluctuations.  
Manually comparing thousands of products across platforms becomes extremely difficult.

This project provides a complete solution by:
- Cleaning raw datasets from both platforms  
- Performing exploratory data analysis  
- Building an interactive analytical dashboard  
- Providing product-level price comparison  
- Offering smart search recommendations  
- Displaying results through a polished website interface  

---

## 📁 Project Structure



ADS Project/
│
├── dashboard.py # Streamlit dashboard (graphs & insights)
├── price_api.py # Price comparison backend API
├── simple_api.py # Simplified API version
├── datacleanning.py # Cleaning raw datasets
├── analyze_updated_dataset.py # Full EDA analysis
├── get_search_recommendations.py # Search suggestion engine
├── find_common_products.py # Common items across platforms
├── check_updated_products.py # Dataset validation
│
├── combined_amazon_flipkart_with_timestamps.csv
├── amazon_flipkart_cleaned.csv
│
├── website/
│ ├── index.html
│ ├── login.html
│ ├── signup.html
│ ├── features.html
│ ├── insights.html
│ ├── price_comparison.html
│ ├── contact.html
│ └── assets/ (CSS, JS)
│
└── report_screenshots/
├── hist_amazon.png
├── hist_flipkart.png
├── monthly_trends.png
├── top_categories.png
└── heatmap_categories.png


---

## 🚀 Features

### 🔹 1. Interactive Dashboard (Streamlit)
Displays:
- Price Distribution  
- Monthly Price Trends  
- Category-wise Bar Graph  
- Category vs Platform Heatmap  
- Dynamic Filters (Platform, Category, Price Range)

### 🔹 2. Price Comparison Tool
- Enter product name  
- Select date  
- View **Amazon vs Flipkart** price comparison  
- Supports partial matches and auto-suggestions  
- Displays friendly “Product Not Found” message if needed  

### 🔹 3. Search Recommendation System
- Suggests closest product names  
- Works with partial keywords  
- Makes product search faster & accurate  

### 🔹 4. Website Interface
Built using **HTML, CSS, JavaScript**, including:
- Login  
- Signup  
- Home  
- Features  
- Insights  
- Price Comparison  
- Contact  

---

## 🛠 Requirements

### Install Dependencies
Run the following:

```bash
pip install pandas numpy plotly streamlit flask flask-cors


OR install individually:

pip install pandas
pip install numpy
pip install plotly
pip install streamlit
pip install flask
pip install flask-cors

🖥 How to Run the Project
1️⃣ Run the Dashboard
streamlit run dashboard.py


Visit:

http://localhost:8501

2️⃣ Run the Price Comparison API
python simple_api.py


or

python price_api.py


API runs at:

http://127.0.0.1:5000

3️⃣ Open Website Pages

Right-click any HTML file → Open with Browser
Examples:

website/index.html
website/login.html
website/signup.html
website/price_comparison.html

📊 Sample Visual Outputs

(Add screenshots in your GitHub repo)

hist_amazon.png

hist_flipkart.png

monthly_trends.png

top_categories.png

heatmap_categories.png

price comparison screenshots

login/signup/home/dashboard UI

📌 Future Enhancements

Real-time API integration

Machine Learning–based price prediction

Cloud deployment (AWS / Heroku)

Multi-platform comparison (Myntra, Ajio, Nykaa, Meesho)

Chrome extension for instant price comparison

User accounts with saved searches and alerts

🏁 Conclusion

This project demonstrates how data science and web technologies can be combined to analyze e-commerce pricing behavior during India’s festive season.
It provides powerful insights, dynamic dashboards, and user-friendly tools, making it useful for consumers, researchers, and analysts.

⭐ Authors

Anika Kaushik
Xiena Vi
