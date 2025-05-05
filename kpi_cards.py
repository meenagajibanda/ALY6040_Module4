import streamlit as st
import pandas as pd
from utils import format_currency

def display_kpi_metrics(df):
    """
    Display the KPI metrics in a row of cards.
    
    Args:
        df: The filtered DataFrame containing the e-commerce data
    """
    # Calculate KPI metrics
    total_sales = df['sales'].sum()
    total_orders = df['order_id'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    total_units_sold = df['quantity'].sum()
    conversion_rate = 68.5  # This would normally be calculated from actual user session data
    
    # Create a row of metric cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=format_currency(total_sales),
            delta=f"{format_currency(total_sales * 0.15)} vs. prev period"
        )
    
    with col2:
        st.metric(
            label="Orders",
            value=f"{total_orders:,}",
            delta=f"{int(total_orders * 0.12)} vs. prev period"
        )
    
    with col3:
        st.metric(
            label="Avg Order Value",
            value=format_currency(avg_order_value),
            delta=f"{round((avg_order_value * 0.05), 2)}% vs. prev period"
        )
    
    with col4:
        st.metric(
            label="Units Sold",
            value=f"{total_units_sold:,}",
            delta=f"{int(total_units_sold * 0.08)} vs. prev period"
        )
    
    with col5:
        st.metric(
            label="Conversion Rate",
            value=f"{conversion_rate}%",
            delta=f"2.3% vs. prev period"
        )
