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

# Sidebar filters
st.sidebar.header("📌 Dashboard Filters")
date_options = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All Time": (df["Order_Date"].max() - df["Order_Date"].min()).days + 1
}
time_filter = st.sidebar.selectbox("Time Period", list(date_options.keys()))
category_filter = st.sidebar.selectbox("Product Category", ["All"] + sorted(df["Category"].unique()))
marketplace_filter = st.sidebar.selectbox("Marketplace", ["All"] + sorted(df["Marketplace"].unique()))

# Filter data
end_date = df["Order_Date"].max()
start_date = end_date - timedelta(days=date_options[time_filter])
filtered_df = df[(df["Order_Date"] >= start_date) & (df["Order_Date"] <= end_date)]

if category_filter != "All":
    filtered_df = filtered_df[filtered_df["Category"] == category_filter]

if marketplace_filter != "All":
    filtered_df = filtered_df[filtered_df["Marketplace"] == marketplace_filter]

# KPIs
total_sales = filtered_df["Revenue"].sum()
total_orders = filtered_df["Order_ID"].nunique()
avg_order_value = total_sales / total_orders if total_orders else 0
units_sold = filtered_df["Units_Sold"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("📦 Orders", total_orders)
col3.metric("💳 Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("🧾 Units Sold", units_sold)

# Sales Trend
st.subheader("📈 Sales Trend")
sales_by_date = filtered_df.groupby("Order_Date").agg({"Revenue": "sum", "Order_ID": "nunique"}).reset_index()
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=sales_by_date["Order_Date"], y=sales_by_date["Revenue"],
                               mode='lines+markers', name='Revenue', line=dict(color='royalblue')))
fig_trend.add_trace(go.Scatter(x=sales_by_date["Order_Date"], y=sales_by_date["Order_ID"],
                               mode='lines+markers', name='Orders', yaxis="y2", line=dict(color='limegreen')))
fig_trend.update_layout(
    yaxis=dict(title='Revenue ($)'),
    yaxis2=dict(title='Orders', overlaying='y', side='right'),
    xaxis=dict(title='Date'),
    height=400, margin=dict(l=30, r=30, t=30, b=30)
)
st.plotly_chart(fig_trend, use_container_width=True)

# Top Products
st.subheader("🏆 Top Revenue by Product")
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

# Sales by Marketplace
col_pie, col_bar = st.columns(2)
with col_pie:
    st.subheader("🌍 Sales by Marketplace")
    sales_marketplace = filtered_df.groupby("Marketplace")["Revenue"].sum()
    fig_marketplace = go.Figure(go.Pie(
        labels=sales_marketplace.index,
        values=sales_marketplace.values,
        hole=0.4
    ))
    st.plotly_chart(fig_marketplace, use_container_width=True)

# Product Category Distribution
with col_bar:
    st.subheader("🧩 Product Category Distribution")
    cat_stats = filtered_df.groupby("Category").agg({
        "Revenue": "sum",
        "Price_per_Unit": "mean"
    }).sort_values("Revenue", ascending=False)
    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(
        x=cat_stats.index,
        y=cat_stats["Revenue"],
        name="Revenue",
        marker_color="skyblue"
    ))
    fig_cat.add_trace(go.Scatter(
        x=cat_stats.index,
        y=cat_stats["Price_per_Unit"],
        name="Avg Price per Item",
        mode="markers+lines",
        yaxis="y2",
        marker=dict(color="orange", size=10)
    ))
    fig_cat.update_layout(
        yaxis=dict(title="Revenue"),
        yaxis2=dict(title="Avg Price", overlaying='y', side='right'),
        barmode='group',
        height=400
    )
    st.plotly_chart(fig_cat, use_container_width=True)
