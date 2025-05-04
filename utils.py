import pandas as pd
import datetime

def format_currency(value):
    """
    Format a numeric value as currency.
    
    Args:
        value: The numeric value to format
        
    Returns:
        str: Formatted currency string
    """
    return f"${value:,.2f}"

def apply_filters(df, start_date, end_date, category, region):
    """
    Apply Amazon seller data filters to the DataFrame based on user selections.
    
    Args:
        df: The original DataFrame containing Amazon seller data
        start_date: Start date for filtering sales data
        end_date: End date for filtering sales data
        category: Selected Amazon product category
        region: Selected Amazon marketplace
        
    Returns:
        DataFrame: Filtered DataFrame with Amazon seller data
    """
    # Create a copy of the DataFrame to avoid modifying the original
    filtered_df = df.copy()
    
    # Apply date filter
    filtered_df = filtered_df[(filtered_df['date'] >= start_date) & 
                             (filtered_df['date'] <= end_date)]
    
    # Apply category filter if not "All Categories"
    if category != "All Categories":
        filtered_df = filtered_df[filtered_df['category'] == category]
    
    # Apply marketplace filter if not "All Marketplaces"
    if region != "All Marketplaces" and region != "All Regions":
        filtered_df = filtered_df[filtered_df['region'] == region]
    
    return filtered_df
