import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from data_generator import generate_ecommerce_data
from components.kpi_cards import display_kpi_metrics
from components.filters import create_filters
from components.visualizations import (
    create_sales_trend_chart,
    create_product_performance_chart,
    create_regional_sales_chart,
    create_category_distribution_chart
)
from utils import format_currency, apply_filters

# Page configuration
st.set_page_config(
    page_title="Amazon Seller Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling with Amazon-inspired colors
st.markdown("""
<style>
    .theme-toggle {
        float: right;
        margin-top: -60px;
        margin-right: 15px;
    }
    .stButton button {
        border-radius: 20px;
        padding: 5px 15px;
    }
    .header-container {
        padding-bottom: 20px;
        background-color: #232F3E;
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 2rem;
        margin-bottom: 0;
        color: white;
    }
    .header-description {
        font-size: 1rem;
        margin-top: 0;
        opacity: 0.9;
        color: #FF9900;
    }
    /* Make download buttons more visible */
    .stDownloadButton button {
        background-color: transparent !important;
        border: none !important;
        color: #FF9900 !important;
        font-size: 24px !important;
    }
    .stDownloadButton button:hover {
        color: #FF9900 !important;
        background-color: rgba(255, 153, 0, 0.1) !important;
    }
    /* Style for KPI cards */
    div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {
        border-top: 3px solid #FF9900 !important;
    }
    /* Amazon-specific dark sidebar - ensure consistent styling */
    section[data-testid="stSidebar"], 
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] .stMarkdown,
    div[data-testid="stSidebarUserContent"] {
        background-color: #232F3E !important;
    }
    
    /* Style sidebar elements consistently with light text */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown strong,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stDateInput label {
        color: white !important;
    }
    
    /* Ensure filter controls have consistent dark background */
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stMultiSelect > div,
    [data-testid="stSidebar"] .stDateInput > div,
    [data-testid="stSidebar"] .stRadio > div {
        background-color: #232F3E !important;
    }
    
    /* Override any default styling for dropdowns in dark theme */
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #232F3E !important;
    }
    
    /* Style dropdown menus */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] div {
        background-color: #131921 !important;
        color: white !important;
        border-color: #3F4B58 !important;
    }
    
    /* Date input styling for dark theme */
    [data-testid="stSidebar"] .stDateInput input {
        background-color: #131921 !important;
        color: white !important;
        border-color: #3F4B58 !important;
    }
    
    /* Radio buttons in dark theme */
    [data-testid="stSidebar"] .stRadio label span p {
        color: white !important;
    }
    /* Amazon button styling */
    div.stButton > button {
        background-color: #FF9900;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #e88a00;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data (this would typically come from a database)
data = generate_ecommerce_data()
df = pd.DataFrame(data)

# Header with theme toggle
col1, col2, col3 = st.columns([1, 5, 1])

with col2:
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="header-title">📊 Amazon Seller Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-description">An interactive analytics dashboard for tracking your Amazon seller performance metrics.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    # Theme toggle button
    if 'light_theme' not in st.session_state:
        st.session_state.light_theme = True
    
    # Toggle theme function
    def toggle_theme():
        st.session_state.light_theme = not st.session_state.light_theme
        
        # Get the current config file content
        config_path = ".streamlit/config.toml"
        
        # Update theme in config.toml (this will require a reload to take effect)
        if st.session_state.light_theme:
            # Light theme settings (Amazon inspired)
            theme_config = """
[theme]
primaryColor = "#FF9900"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#232F3E"
"""
            with open(config_path, "r") as file:
                content = file.read()
                # Keep the server config, replace theme config
                server_config = content.split("[theme]")[0]
                with open(config_path, "w") as out_file:
                    out_file.write(server_config + theme_config)
            
            st.info("🌞 Light theme applied. Refresh to see changes.")
        else:
            # Dark theme settings (Amazon inspired)
            theme_config = """
[theme]
primaryColor = "#FF9900"
backgroundColor = "#0F1111"
secondaryBackgroundColor = "#232F3E"
textColor = "#FAFAFA"
"""
            with open(config_path, "r") as file:
                content = file.read()
                # Keep the server config, replace theme config
                server_config = content.split("[theme]")[0]
                with open(config_path, "w") as out_file:
                    out_file.write(server_config + theme_config)
            
            st.info("🌙 Dark theme applied. Refresh to see changes.")
    
    # Display toggle button
    st.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
    if st.session_state.light_theme:
        st.button("🌙 Dark Mode", on_click=toggle_theme)
    else:
        st.button("🌞 Light Mode", on_click=toggle_theme)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("📌 Dashboard Filters")

# Create filters in sidebar
filtered_df, selected_timeframe, selected_category, selected_region = create_filters(df)

# Main dashboard layout
# Row 1: Summary Stats
st.markdown("""
<div style="background-color: rgba(255,153,0,0.05); border-left: 5px solid #FF9900; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <h3 style="margin-top: 0;">📊 Amazon Sales Overview</h3>
    <p>Viewing data for <b>{timeframe}</b> {category} {region}</p>
</div>
""".format(
    timeframe=selected_timeframe,
    category=f"in category <b>{selected_category}</b>" if selected_category != "All Categories" else "across all categories",
    region=f"in marketplace <b>{selected_region}</b>" if selected_region != "All Regions" else "across all marketplaces"
), unsafe_allow_html=True)

# Row 2: KPI metrics cards
st.subheader("📈 Key Performance Indicators")
display_kpi_metrics(filtered_df)

# Row 2: Sales Trend and Product Performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("📆 Sales Trend")
    sales_chart = create_sales_trend_chart(filtered_df, selected_timeframe)
    st.plotly_chart(sales_chart, use_container_width=True)

with col2:
    st.subheader("💰 Top Revenue by Product")
    product_chart = create_product_performance_chart(filtered_df)
    st.plotly_chart(product_chart, use_container_width=True)

# Row 3: Regional Sales and Category Distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌎 Sales by Amazon Marketplace")
    region_chart = create_regional_sales_chart(filtered_df)
    st.plotly_chart(region_chart, use_container_width=True)

with col2:
    st.subheader("📊 Product Category Distribution")
    category_chart = create_category_distribution_chart(filtered_df)
    st.plotly_chart(category_chart, use_container_width=True)

# Row 4: Top selling products table
col1, col2 = st.columns([9, 1])
with col1:
    st.subheader("🔝 Amazon Best Sellers")
with col2:
    # Get the raw data for download
    download_products = filtered_df.groupby('product_name').agg({
        'quantity': 'sum',
        'sales': 'sum',
        'order_id': 'nunique'
    }).sort_values('sales', ascending=False).reset_index().head(10)
    
    # Create a download button
    csv = download_products.to_csv(index=False)
    st.download_button(
        label="📥",
        data=csv,
        file_name="amazon_best_sellers.csv",
        mime="text/csv",
        help="Download data as CSV"
    )

top_products = filtered_df.groupby('product_name').agg({
    'quantity': 'sum',
    'sales': 'sum',
    'order_id': 'nunique'
}).sort_values('sales', ascending=False).reset_index().head(10)

# Format the display data
display_products = top_products.copy()
display_products['sales'] = display_products['sales'].apply(format_currency)

# Display the dataframe
st.dataframe(
    display_products.rename(columns={
        'product_name': 'Product',
        'quantity': 'Units Sold',
        'sales': 'Revenue',
        'order_id': 'Order Count'
    }),
    use_container_width=True,
    hide_index=True
)

# Row 5: Recent orders
col1, col2 = st.columns([9, 1])
with col1:
    st.subheader("🕒 Recent Orders")
with col2:
    # Get raw data for download
    download_orders = filtered_df.sort_values('date', ascending=False).head(20).copy()
    # Format date for CSV
    download_orders['date'] = download_orders['date'].dt.strftime('%Y-%m-%d')
    # Create download button
    csv = download_orders.to_csv(index=False)
    st.download_button(
        label="📥",
        data=csv,
        file_name="recent_orders.csv",
        mime="text/csv",
        help="Download data as CSV"
    )

# Get display data
recent_orders = filtered_df.sort_values('date', ascending=False).head(5)
recent_orders['sales'] = recent_orders['sales'].apply(format_currency)
recent_orders['date'] = recent_orders['date'].dt.strftime('%Y-%m-%d')

# Create a display dataframe
display_columns = ['date', 'order_id', 'product_name', 'quantity', 'sales', 'region']
display_df = recent_orders[display_columns].rename(columns={
    'date': 'Date',
    'order_id': 'Order ID',
    'product_name': 'Product',
    'quantity': 'Quantity',
    'sales': 'Revenue',
    'region': 'Marketplace'
})

# Display the dataframe
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("---")
st.caption("Amazon Seller Analytics Dashboard - Based on Amazon Seller Central")
