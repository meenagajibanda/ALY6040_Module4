import streamlit as st
import datetime
import pandas as pd
from utils import apply_filters

def create_filters(df):
    """
    Create and display Amazon Seller filter controls in the sidebar.
    
    Args:
        df: The original DataFrame containing the Amazon seller data
        
    Returns:
        filtered_df: DataFrame after applying all filters
        selected_timeframe: The selected time period
        selected_category: The selected product category
        selected_region: The selected Amazon marketplace
    """
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    # Use tabs for different date selection methods
    date_filter_method = st.sidebar.radio(
        "Date Filter Method",
        ["Quick Select", "Custom Range"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if date_filter_method == "Quick Select":
        # Predefined time ranges
        timeframe_options = [
            "Last 7 days",
            "Last 30 days",
            "Last 90 days",
            "Year to date",
            "All time"
        ]
        
        selected_timeframe = st.sidebar.selectbox(
            "Time Period", 
            timeframe_options,
            index=1  # Default to Last 30 days
        )
        
        end_date = datetime.datetime.combine(max_date, datetime.time.max)
        
        if selected_timeframe == "Last 7 days":
            start_date = end_date - datetime.timedelta(days=7)
        elif selected_timeframe == "Last 30 days":
            start_date = end_date - datetime.timedelta(days=30)
        elif selected_timeframe == "Last 90 days":
            start_date = end_date - datetime.timedelta(days=90)
        elif selected_timeframe == "Year to date":
            start_date = datetime.datetime(end_date.year, 1, 1)
        else:  # All time
            start_date = datetime.datetime.combine(min_date, datetime.time.min)
    else:
        # Custom date range with calendar picker
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=max_date - datetime.timedelta(days=30),
                min_value=min_date,
                max_value=max_date
            )
            start_date = datetime.datetime.combine(start_date, datetime.time.min)
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )
            end_date = datetime.datetime.combine(end_date, datetime.time.max)
        
        # Set a descriptive name for display
        if (end_date.date() - start_date.date()).days == 29:
            selected_timeframe = "Last 30 days"
        elif (end_date.date() - start_date.date()).days == 6:
            selected_timeframe = "Last 7 days"
        elif (end_date.date() - start_date.date()).days == 89:
            selected_timeframe = "Last 90 days"
        else:
            selected_timeframe = f"Custom: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    
    # Amazon Product Category filter
    categories = ["All Categories"] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Amazon Product Category", categories)
    
    # Amazon Marketplace filter (region)
    regions = ["All Marketplaces"] + sorted(df['region'].unique().tolist())
    selected_region = st.sidebar.selectbox("Amazon Marketplace", regions)
    
    # Apply filters
    filtered_df = apply_filters(df, start_date, end_date, selected_category, selected_region)
    
    # Show active filters with Amazon styling
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Active Filters")
    st.sidebar.markdown(f"📅 **Time Period:** {selected_timeframe}")
    st.sidebar.markdown(f"🏷️ **Product Category:** {selected_category}")
    st.sidebar.markdown(f"🌎 **Marketplace:** {selected_region}")
    
    # Show current Amazon seller metrics after filtering
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Amazon Performance")
    st.sidebar.markdown(f"📊 **Total Orders:** {filtered_df['order_id'].nunique():,}")
    st.sidebar.markdown(f"💰 **Total Revenue:** ${filtered_df['sales'].sum():,.2f}")
    st.sidebar.markdown(f"📦 **Units Sold:** {filtered_df['quantity'].sum():,}")
    
    return filtered_df, selected_timeframe, selected_category, selected_region
