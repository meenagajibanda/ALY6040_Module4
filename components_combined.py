# Combined Components Module

# ---------- filters.py ----------

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


# ---------- kpi_cards.py ----------

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


# ---------- visualizations.py ----------

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_sales_trend_chart(df, timeframe):
    """
    Create a time series chart showing sales trends over time.
    
    Args:
        df: The filtered DataFrame containing the e-commerce data
        timeframe: The selected time period
        
    Returns:
        fig: A Plotly figure object
    """
    # Determine appropriate time grouping based on timeframe
    if timeframe == "Last 7 days":
        # Group by day and hour
        df_grouped = df.groupby(pd.Grouper(key='date', freq='4h')).agg({
            'sales': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        x_title = 'Date and Hour'
    elif timeframe == "Last 30 days":
        # Group by day
        df_grouped = df.groupby(pd.Grouper(key='date', freq='D')).agg({
            'sales': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        x_title = 'Date'
    else:
        # Group by week
        df_grouped = df.groupby(pd.Grouper(key='date', freq='W')).agg({
            'sales': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        x_title = 'Week'
    
    # Create figure with dual y-axis
    fig = go.Figure()
    
    # Add sales line
    fig.add_trace(go.Scatter(
        x=df_grouped['date'],
        y=df_grouped['sales'],
        name='Revenue',
        line=dict(color='#007bff', width=3),
        mode='lines+markers'
    ))
    
    # Add orders line on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df_grouped['date'],
        y=df_grouped['order_id'],
        name='Orders',
        line=dict(color='#28a745', width=3, dash='dash'),
        mode='lines+markers',
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title=x_title),
        yaxis=dict(
            title=dict(text='Revenue ($)', font=dict(color='#007bff')),
            tickfont=dict(color='#007bff')
        ),
        yaxis2=dict(
            title=dict(text='Number of Orders', font=dict(color='#28a745')),
            tickfont=dict(color='#28a745'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    return fig

def create_product_performance_chart(df):
    """
    Create a chart showing top-performing products.
    
    Args:
        df: The filtered DataFrame containing the e-commerce data
        
    Returns:
        fig: A Plotly figure object
    """
    # Group by product and calculate metrics
    product_performance = df.groupby('product_name').agg({
        'sales': 'sum',
        'quantity': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    
    # Calculate average order value for each product
    product_performance['avg_price'] = product_performance['sales'] / product_performance['quantity']
    
    # Sort by sales and take top 10
    top_products = product_performance.sort_values('sales', ascending=False).head(10)
    
    # Create horizontal bar chart
    fig = px.bar(
        top_products,
        y='product_name',
        x='sales',
        orientation='h',
        color='sales',
        color_continuous_scale='Blues',
        # Remove the text labels
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Revenue ($)',
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),  # Highest value at the top
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        # Remove the title completely
    )
    
    # Only set hover template, no text display
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
    )
    
    return fig

def create_regional_sales_chart(df):
    """
    Create a chart showing sales breakdown by region.
    
    Args:
        df: The filtered DataFrame containing the e-commerce data
        
    Returns:
        fig: A Plotly figure object
    """
    # Group by region
    region_sales = df.groupby('region').agg({
        'sales': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    
    # Sort by sales
    region_sales = region_sales.sort_values('sales', ascending=False)
    
    # Calculate percentage of total
    total_sales = region_sales['sales'].sum()
    region_sales['percentage'] = region_sales['sales'] / total_sales * 100
    
    # Create a pie chart
    fig = px.pie(
        region_sales,
        values='sales',
        names='region',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data=['percentage']
    )
    
    # Update traces for better hover info
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig

def create_category_distribution_chart(df):
    """
    Create a chart showing sales distribution by product category.
    
    Args:
        df: The filtered DataFrame containing the e-commerce data
        
    Returns:
        fig: A Plotly figure object
    """
    # Group by category
    category_sales = df.groupby('category').agg({
        'sales': 'sum',
        'quantity': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    
    # Calculate average price per item in each category
    category_sales['avg_price'] = category_sales['sales'] / category_sales['quantity']
    
    # Sort by sales
    category_sales = category_sales.sort_values('sales', ascending=True)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Add bars for sales
    fig.add_trace(go.Bar(
        y=category_sales['category'],
        x=category_sales['sales'],
        name='Revenue',
        orientation='h',
        marker_color='#4e73df',
        # Remove text values
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
    ))
    
    # Add markers for average price
    fig.add_trace(go.Scatter(
        y=category_sales['category'],
        x=category_sales['avg_price'] * 50,  # Scale for visibility
        name='Avg Price per Item',
        mode='markers',
        marker=dict(
            size=12,
            symbol='circle',
            color='#f6c23e',
            line=dict(width=2, color='#e0aa0b')
        ),
        hovertemplate='<b>%{y}</b><br>Avg Price: $%{text:.2f}<extra></extra>',
        text=category_sales['avg_price']
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title='Revenue ($)',
        yaxis_title=None,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        xaxis2=dict(
            overlaying='x',
            side='top',
            range=[0, category_sales['avg_price'].max() * 100],
            showticklabels=False
        )
    )
    
    return fig
