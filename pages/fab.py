import pandas as pd
import streamlit as st
import plotly.express as px

################USER AUTHETICATION ##########


# --- Check Authentication ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Please login first.")
    st.stop()

user = st.session_state.user_info
if user["user_type"] != "A" or user["Menu_type"] != "A":
    st.error("🚫 You are not authorized to view this dashboard.")
    st.stop()

st.title(" Fashion Sales Dashboard ")

# =====================
# Load dataset
# =====================
df = pd.read_csv("fashion_sales_dataset_300.csv")



# Ensure Order_Date is in datetime format
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Order_Date'] = df['Order_Date'].dt.date   

st.title("👗 Fashion Sales Dashboard ")

# =====================
# Sidebar Instructions
# =====================
st.sidebar.markdown("### 📌 Instructions")
st.sidebar.info(
    """
    Use the slider below to filter data by date range.  
    All visualizations will update accordingly.  
    Scroll down to see insights for each chart.
    """
)

# =====================
# Date Range Slider
# =====================
min_date = df['Order_Date'].min()
max_date = df['Order_Date'].max()
date_range = st.sidebar.slider(
    "📅 Select Date Range for Analysis",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter data by date
filtered_df = df[(df['Order_Date'] >= date_range[0]) & (df['Order_Date'] <= date_range[1])]

# =====================
# 1. Interactive Line Chart: Revenue Trend
# =====================
st.subheader("📈 Revenue Trend Over Time (Interactive)")

# Dropdown for product selection
products = ["All"] + sorted(df["Product"].unique().tolist())
selected_product = st.selectbox("🔍 Select Product for Trend Analysis", products)

if selected_product != "All":
    chart_df = filtered_df[filtered_df["Product"] == selected_product]
else:
    chart_df = filtered_df

# Aggregate by date
revenue_trend = chart_df.groupby("Order_Date")["Revenue"].sum().reset_index()

# Plotly interactive line chart
fig = px.line(
    revenue_trend,
    x="Order_Date",
    y="Revenue",
    title=f"Revenue Trend Over Time ({selected_product})",
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

if not revenue_trend.empty:
    st.write(f"📝 Insight: Between **{date_range[0]}** and **{date_range[1]}**, "
             f"the highest revenue recorded was **{revenue_trend['Revenue'].max()}**, "
             f"and the lowest was **{revenue_trend['Revenue'].min()}**.")
else:
    st.warning("⚠️ No data available for the selected product in this date range.")

# =====================
# 2. Interactive Bar Chart: Sales by Product
# =====================
st.subheader("👗 Sales by Product")
product_sales = filtered_df.groupby("Product")["Quantity"].sum().reset_index()
fig = px.bar(product_sales, x="Product", y="Quantity", title="Product-wise Sales (Quantity)", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

if not product_sales.empty:
    top_product = product_sales.loc[product_sales["Quantity"].idxmax(), "Product"]
    st.write(f"📝 Insight: The **{top_product}** product had the highest sales in this period.")

# =====================
# 3. Interactive Pie Chart: Sales by Season
# =====================
st.subheader("🌦️ Seasonal Sales Distribution")
season_sales = filtered_df.groupby("Season")["Revenue"].sum().reset_index()
fig = px.pie(season_sales, names="Season", values="Revenue", title="Revenue Contribution by Season", hole=0.3)
st.plotly_chart(fig, use_container_width=True)

if not season_sales.empty:
    top_season = season_sales.loc[season_sales["Revenue"].idxmax(), "Season"]
    st.write(f"📝 Insight: The **{top_season}** season generated the most revenue.")

# =====================
# 4. Interactive Bar Chart: Profit by Fabric
# =====================
st.subheader("🧵 Profit by Fabric Type")
fabric_profit = filtered_df.groupby("Fabric")["Profit"].sum().reset_index()
fig = px.bar(fabric_profit, x="Fabric", y="Profit", title="Fabric-wise Profit", text_auto=True, color="Profit")
st.plotly_chart(fig, use_container_width=True)

if not fabric_profit.empty:
    top_fabric = fabric_profit.loc[fabric_profit["Profit"].idxmax(), "Fabric"]
    st.write(f"📝 Insight: The **{top_fabric}** fabric was the most profitable overall.")

# =====================
# 5. Interactive Bar Chart: Top 10 Locations by Revenue
# =====================
st.subheader("🌍 Top 10 Locations by Revenue")
location_sales = (filtered_df.groupby("Location")["Revenue"]
                  .sum()
                  .reset_index()
                  .sort_values(by="Revenue", ascending=False)
                  .head(10))
fig = px.bar(location_sales, x="Revenue", y="Location", orientation="h",
             title="Top 10 Locations by Revenue", text_auto=True, color="Revenue")
st.plotly_chart(fig, use_container_width=True)

if not location_sales.empty:
    top_city = location_sales.iloc[0]["Location"]
    st.write(f"📝 Insight: The city with the highest revenue is **{top_city}**.")

# ================= KPI Calculations =================
total_revenue = filtered_df['Revenue'].sum()
total_quantity = filtered_df['Quantity'].sum()

# Avoid dividing by zero
average_order_value = (
    total_revenue / len(filtered_df) if len(filtered_df) > 0 else 0
)

# Highest selling product
if not filtered_df.empty:
    highest_selling_product = (
        filtered_df.groupby('Product')['Quantity'].sum().idxmax()
    )
else:
    highest_selling_product = "N/A"

# Customer retention rate (approx: repeat customers / total customers)
repeat_customers = filtered_df['Order_ID'].duplicated().sum()
total_customers = filtered_df['Order_ID'].nunique()
if total_customers > 0:
    retention_rate = (repeat_customers / total_customers) * 100
else:
    retention_rate = 0

# ================= Helper Function =================
def format_inr(num):
    """
    Format number in Indian style with Lakhs (L) and Crores (Cr)
    """
    if num >= 1e7:
        return f"{num/1e7:.2f} Cr"
    elif num >= 1e5:
        return f"{num/1e5:.2f} L"
    else:
        return f"{num:,.0f}"



# ================= Streamlit UI =================
st.subheader("📊 Key Performance Indicators")

# KPI Cards in 5 Columns
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"💰 **Total Revenue**<br>₹ {total_revenue:,.0f}", unsafe_allow_html=True)

with kpi2:
    st.markdown(f"📦 **Total Quantity Sold**<br>{total_quantity:,}", unsafe_allow_html=True)

with kpi3:
    st.markdown(f"📊 **Avg. Order Value (AOV)**<br>₹ {average_order_value:,.0f}", unsafe_allow_html=True)

with kpi4:
    st.markdown(f"🏆 **Best Selling Product**<br>{highest_selling_product}", unsafe_allow_html=True)
