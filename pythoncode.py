# -*- coding: utf-8 -*-
"""
Created on Sun May  4 19:03:47 2025

@author: meena
"""

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_sales_data.csv", parse_dates=["Order_Date"])
    return df

df = load_data()

# Sidebar layout
st.sidebar.markdown("## 📌 Dashboard Filters")

# Toggle for filter mode
filter_mode = st.sidebar.radio(
    label="Select Filter Mode:",
    options=["Quick Select", "Custom Range"],
    horizontal=True
)

# Time filters
date_options = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All Time": (df["Order_Date"].max() - df["Order_Date"].min()).days + 1
}

if filter_mode == "Quick Select":
    time_filter = st.sidebar.selectbox("Time Period", list(date_options.keys()))
    end_date = df["Order_Date"].max()
    start_date = end_date - timedelta(days=date_options[time_filter])
else:
    date_range = st.sidebar.date_input("Select Date Range", [df["Order_Date"].min(), df["Order_Date"].max()])
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    time_filter = f"{start_date.strftime('%b %d')} to {end_date.strftime('%b %d')}"

# Category and Marketplace filters
category_filter = st.sidebar.selectbox("Amazon Product Category", ["All Categories"] + sorted(df["Category"].unique()))
marketplace_filter = st.sidebar.selectbox("Amazon Marketplace", ["All Marketplaces"] + sorted(df["Marketplace"].unique()))

# Apply filters
filtered_df = df[(df["Order_Date"] >= start_date) & (df["Order_Date"] <= end_date)]

if category_filter != "All Categories":
    filtered_df = filtered_df[filtered_df["Category"] == category_filter]

if marketplace_filter != "All Marketplaces":
    filtered_df = filtered_df[filtered_df["Marketplace"] == marketplace_filter]

# Display active filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Active Filters")
st.sidebar.markdown(f"📅 **Time Period:** {time_filter}")
st.sidebar.markdown(f"🏷️ **Product Category:** {category_filter}")
st.sidebar.markdown(f"🌍 **Marketplace:** {marketplace_filter}")

# === KPIs ===
# Current period metrics
total_sales = filtered_df["Revenue"].sum()
total_orders = filtered_df["Order_ID"].nunique()
avg_order_value = total_sales / total_orders if total_orders else 0
units_sold = filtered_df["Units_Sold"].sum()

# Mock previous period values
prev_sales = total_sales * 0.85
prev_orders = total_orders - 41
prev_avg_order_value = avg_order_value * 0.66
prev_units_sold = units_sold - 51

# Calculate deltas
delta_sales = total_sales - prev_sales
delta_orders = total_orders - prev_orders
delta_avg_order_value = avg_order_value - prev_avg_order_value
delta_units_sold = units_sold - prev_units_sold

# KPI layout
col1, col2, col3, col4, col5 = st.columns([1.2, 1, 1, 1, 1])

col1.metric("💰 Revenue", f"${total_sales:,.2f}", f"${delta_sales:,.2f} vs. prev")
col2.metric("📦 Orders", total_orders, f"{delta_orders} vs. prev")
col3.metric("💳 Avg Order Value", f"${avg_order_value:,.2f}", f"{delta_avg_order_value:.2f} vs. prev")
col4.metric("🧾 Units Sold", units_sold, f"{delta_units_sold} vs. prev")
col5.metric("📈 Conversion", "68.5%", "↑ 2.3% vs. prev")

# === Sales Trend Chart ===
st.subheader("📈 Sales Trend Over Time")

sales_by_date = (
    filtered_df.groupby("Order_Date")
    .agg({"Revenue": "sum", "Order_ID": "nunique"})
    .reset_index()
)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=sales_by_date["Order_Date"], y=sales_by_date["Revenue"],
    mode='lines+markers', name='Revenue', line=dict(color='royalblue')
))
fig_trend.add_trace(go.Scatter(
    x=sales_by_date["Order_Date"], y=sales_by_date["Order_ID"],
    mode='lines+markers', name='Orders', yaxis="y2", line=dict(color='limegreen')
))
fig_trend.update_layout(
    yaxis=dict(title='Revenue ($)'),
    yaxis2=dict(title='Orders', overlaying='y', side='right'),
    xaxis=dict(title='Date'),
    height=400, margin=dict(l=30, r=30, t=30, b=30)
)
st.plotly_chart(fig_trend, use_container_width=True)

# === Top Revenue by Product ===
st.subheader("💰 Top Revenue by Product")

top_products = (
    filtered_df.groupby("Product")["Revenue"]
    .sum().nlargest(10).sort_values()
)

fig_top = go.Figure(go.Bar(
    x=top_products.values,
    y=top_products.index,
    orientation='h',
    marker_color='dodgerblue'
))
fig_top.update_layout(xaxis_title="Revenue ($)", height=400)
st.plotly_chart(fig_top, use_container_width=True)

# === Marketplace + Category Charts ===
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌍 Sales by Amazon Marketplace")
    sales_marketplace = filtered_df.groupby("Marketplace")["Revenue"].sum()
    fig_marketplace = go.Figure(go.Pie(
        labels=sales_marketplace.index,
        values=sales_marketplace.values,
        hole=0.4
    ))
    fig_marketplace.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_marketplace, use_container_width=True)

with col_right:
    st.subheader("📦 Product Category Distribution")
    sales_category = filtered_df.groupby("Category")["Revenue"].sum().sort_values(ascending=True)
    fig_category = go.Figure(go.Bar(
        x=sales_category.values,
        y=sales_category.index,
        orientation='h',
        marker_color='mediumpurple'
    ))
    fig_category.update_layout(xaxis_title="Revenue ($)", height=400)
    st.plotly_chart(fig_category, use_container_width=True)
