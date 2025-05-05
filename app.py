import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

from data_generator import generate_ecommerce_data
from utils import format_currency, apply_filters

# Import all functions from the combined components file
from components_combined import (
    create_filters,
    display_kpi_metrics,
    create_sales_trend_chart,
    create_product_performance_chart,
    create_regional_sales_chart,
    create_category_distribution_chart
)

# Page configuration
st.set_page_config(
    page_title="Amazon Seller Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Generate sample data
df = generate_ecommerce_data()

# Header
st.markdown("""
<div style='background-color: #232F3E; padding: 20px; border-radius: 5px; margin-bottom: 20px;'>
    <h1 style='color: white; margin-bottom: 0;'>📊 Amazon Seller Analytics Dashboard</h1>
    <p style='color: #FF9900; margin-top: 0;'>An interactive analytics dashboard for tracking your Amazon seller performance metrics.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("📌 Dashboard Filters")
filtered_df, selected_timeframe, selected_category, selected_region = create_filters(df)

# Sales Overview
st.markdown(f"""
<div style="background-color: rgba(255,153,0,0.05); border-left: 5px solid #FF9900; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <h3 style="margin-top: 0;">📊 Amazon Sales Overview</h3>
    <p>Viewing data for <b>{selected_timeframe}</b> {f'in category <b>{selected_category}</b>' if selected_category != 'All Categories' else 'across all categories'} {f'in marketplace <b>{selected_region}</b>' if selected_region != 'All Marketplaces' else 'across all marketplaces'}</p>
</div>
""", unsafe_allow_html=True)

# KPI metrics
st.subheader("📈 Key Performance Indicators")
display_kpi_metrics(filtered_df)

# Sales Trend and Product Performance
col1, col2 = st.columns(2)
with col1:
    st.subheader("📆 Sales Trend")
    st.plotly_chart(create_sales_trend_chart(filtered_df, selected_timeframe), use_container_width=True)
with col2:
    st.subheader("💰 Top Revenue by Product")
    st.plotly_chart(create_product_performance_chart(filtered_df), use_container_width=True)

# Regional Sales and Category Distribution
col1, col2 = st.columns(2)
with col1:
    st.subheader("🌎 Sales by Amazon Marketplace")
    st.plotly_chart(create_regional_sales_chart(filtered_df), use_container_width=True)
with col2:
    st.subheader("📊 Product Category Distribution")
    st.plotly_chart(create_category_distribution_chart(filtered_df), use_container_width=True)

# Top selling products table
col1, col2 = st.columns([9, 1])
with col1:
    st.subheader("🔝 Amazon Best Sellers")
with col2:
    top_products = filtered_df.groupby('product_name').agg({
        'quantity': 'sum',
        'sales': 'sum',
        'order_id': 'nunique'
    }).sort_values('sales', ascending=False).reset_index().head(10)
    
    csv = top_products.to_csv(index=False)
    st.download_button(
        label="📥",
        data=csv,
        file_name="amazon_best_sellers.csv",
        mime="text/csv",
        help="Download data as CSV"
    )

# Display top sellers table
top_products['sales'] = top_products['sales'].apply(format_currency)
st.dataframe(
    top_products.rename(columns={
        'product_name': 'Product',
        'quantity': 'Units Sold',
        'sales': 'Revenue',
        'order_id': 'Order Count'
    }),
    use_container_width=True,
    hide_index=True
)

# Recent orders section
col1, col2 = st.columns([9, 1])
with col1:
    st.subheader("🕒 Recent Orders")
with col2:
    download_orders = filtered_df.sort_values('date', ascending=False).head(20).copy()
    download_orders['date'] = download_orders['date'].dt.strftime('%Y-%m-%d')
    csv = download_orders.to_csv(index=False)
    st.download_button(
        label="📥",
        data=csv,
        file_name="recent_orders.csv",
        mime="text/csv",
        help="Download data as CSV"
    )

recent_orders = filtered_df.sort_values('date', ascending=False).head(5)
recent_orders['sales'] = recent_orders['sales'].apply(format_currency)
recent_orders['date'] = recent_orders['date'].dt.strftime('%Y-%m-%d')

display_df = recent_orders[[
    'date', 'order_id', 'product_name', 'quantity', 'sales', 'region'
]].rename(columns={
    'date': 'Date',
    'order_id': 'Order ID',
    'product_name': 'Product',
    'quantity': 'Quantity',
    'sales': 'Revenue',
    'region': 'Marketplace'
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("Amazon Seller Analytics Dashboard - Based on Amazon Seller Central")
