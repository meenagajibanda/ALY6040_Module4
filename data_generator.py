import pandas as pd
import numpy as np
import datetime
import random

def generate_ecommerce_data(num_records=1000):
    """
    Generate synthetic Amazon seller data for demonstration purposes.
    Returns a pandas DataFrame with realistic Amazon marketplace metrics.
    """
    # Set a seed for reproducibility
    np.random.seed(42)
    
    # Date range for the past 90 days
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=90)
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')
    
    # Product categories
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Beauty', 'Sports', 'Books']
    
    # Amazon products for each category
    products = {
        'Electronics': ['Echo Dot (4th Gen)', 'Fire TV Stick 4K', 'Kindle Paperwhite', 'Ring Video Doorbell', 'Bose QuietComfort Earbuds'],
        'Clothing': ['Amazon Essentials T-Shirt', 'Levi\'s 501 Original Jeans', 'Under Armour Hoodie', 'Adidas Running Shoes', 'Columbia Fleece Jacket'],
        'Home & Kitchen': ['Instant Pot Duo', 'Ninja Air Fryer', 'Keurig K-Slim Coffee Maker', 'Lodge Cast Iron Skillet', 'iRobot Roomba'],
        'Beauty': ['CeraVe Moisturizer', 'Olaplex Hair Perfector', 'Revlon One-Step Hair Dryer', 'Neutrogena Sunscreen', 'The Ordinary Serum'],
        'Sports': ['Fitbit Charge 5', 'Bowflex Adjustable Dumbbells', 'Hydro Flask Water Bottle', 'Manduka Yoga Mat', 'Coleman Camping Tent'],
        'Books': ['Atomic Habits', 'The Psychology of Money', 'Where the Crawdads Sing', 'It Ends with Us', 'The Body Keeps the Score']
    }
    
    # Price ranges for each category
    price_ranges = {
        'Electronics': (100, 1500),
        'Clothing': (15, 200),
        'Home & Kitchen': (20, 300),
        'Beauty': (10, 150),
        'Sports': (15, 250),
        'Books': (8, 50)
    }
    
    # Amazon Marketplaces
    regions = ['Amazon.com (US)', 'Amazon.co.uk (UK)', 'Amazon.de (Germany)', 'Amazon.co.jp (Japan)', 'Amazon.ca (Canada)', 'Amazon.com.au (Australia)']
    
    # Generate data
    data = []
    
    for _ in range(num_records):
        # Random date from the date range
        date = np.random.choice(date_range)
        
        # Random category and product
        category = np.random.choice(categories, p=[0.3, 0.25, 0.15, 0.1, 0.1, 0.1])
        product = np.random.choice(products[category])
        
        # Region with some regions having higher probability
        region = np.random.choice(regions, p=[0.4, 0.25, 0.2, 0.08, 0.05, 0.02])
        
        # Price based on category
        base_price = np.random.uniform(price_ranges[category][0], price_ranges[category][1])
        
        # Quantity (most orders are for 1-2 items)
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.3, 0.1, 0.07, 0.03])
        
        # Random discount between 0-20%
        discount = np.random.uniform(0, 0.2)
        
        # Calculate final price
        price = base_price * (1 - discount)
        sales = price * quantity
        
        # Amazon Order ID (format: XXX-XXXXXXX-XXXXXXX)
        order_id = ''.join(random.choices('0123456789', k=3)) + '-' + \
                   ''.join(random.choices('0123456789', k=7)) + '-' + \
                   ''.join(random.choices('0123456789', k=7))
        
        # Add to data
        data.append({
            'date': date,
            'order_id': order_id,
            'category': category,
            'product_name': product,
            'quantity': quantity,
            'unit_price': round(price, 2),
            'sales': round(sales, 2),
            'region': region
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add some time-based patterns to make data more realistic
    
    # 1. Weekend boost
    weekend_mask = df['date'].dt.dayofweek.isin([5, 6])  # Saturday and Sunday
    df.loc[weekend_mask, 'sales'] = df.loc[weekend_mask, 'sales'] * np.random.uniform(1.1, 1.3, size=weekend_mask.sum())
    
    # 2. Holiday season boost (assume last 15 days are holiday season)
    holiday_mask = df['date'] >= (end_date - datetime.timedelta(days=15))
    df.loc[holiday_mask, 'sales'] = df.loc[holiday_mask, 'sales'] * np.random.uniform(1.2, 1.5, size=holiday_mask.sum())
    
    # 3. Time of day patterns
    # More sales during business hours
    business_hours_mask = df['date'].dt.hour.between(9, 19)
    df.loc[business_hours_mask, 'sales'] = df.loc[business_hours_mask, 'sales'] * np.random.uniform(1.05, 1.2, size=business_hours_mask.sum())
    
    return df.sort_values('date')
