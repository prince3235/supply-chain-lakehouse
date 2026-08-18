import pandas as pd
import numpy as np
from faker import Faker
import random

faker = Faker()

def generate_calendar(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame({'date': dates})
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_name'] = df['date'].dt.day_name()
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    df['quarter'] = df['date'].dt.quarter
    df['year'] = df['date'].dt.year
    df['weekend_flag'] = df['day_of_week'].isin([5, 6])
    
    # Generate random holidays for simulation purposes
    np.random.seed(42) # Deterministic holidays
    df['holiday_flag'] = np.random.choice([True, False], size=len(df), p=[0.05, 0.95])
    df['holiday_name'] = df['holiday_flag'].apply(lambda x: 'Synthetic Holiday' if x else None)
    df['festival_flag'] = np.random.choice([True, False], size=len(df), p=[0.02, 0.98])
    return df

def generate_products(num_products):
    categories = ['Electronics', 'Clothing', 'Food', 'Home', 'Sports']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'Generic']
    
    data = []
    for i in range(num_products):
        cat = random.choice(categories)
        unit_cost = round(random.uniform(5.0, 500.0), 2)
        selling_price = round(unit_cost * random.uniform(1.2, 2.5), 2)
        
        data.append({
            'product_id': f'PRD-{i+1:05d}',
            'product_name': f'{cat} Product {i+1}',
            'category': cat,
            'subcategory': f'Sub-{cat}',
            'brand': random.choice(brands),
            'unit_cost': unit_cost,
            'selling_price': selling_price,
            'shelf_life_days': random.choice([None, 30, 90, 180, 365]) if cat == 'Food' else None,
            'active_flag': True,
            'created_at': pd.Timestamp.now(),
            'updated_at': None
        })
    return pd.DataFrame(data)

def generate_stores(num_stores):
    store_types = ['Flagship', 'Standard', 'Express']
    regions = ['North', 'South', 'East', 'West']
    
    data = []
    for i in range(num_stores):
        data.append({
            'store_id': f'STR-{i+1:03d}',
            'store_name': f'Store {faker.city()}',
            'city': faker.city(),
            'state': faker.state(),
            'country': 'USA',
            'region': random.choice(regions),
            'store_type': random.choice(store_types),
            'latitude': float(faker.latitude()),
            'longitude': float(faker.longitude()),
            'opening_date': pd.Timestamp('2020-01-01').date(),
            'active_flag': True
        })
    return pd.DataFrame(data)

def generate_warehouses(num_warehouses):
    regions = ['North', 'South', 'East', 'West']
    types = ['Distribution Center', 'Fulfillment Center']
    
    data = []
    for i in range(num_warehouses):
        cap = random.randint(10000, 100000)
        data.append({
            'warehouse_id': f'WH-{i+1:03d}',
            'warehouse_name': f'Warehouse {faker.city()}',
            'city': faker.city(),
            'state': faker.state(),
            'region': random.choice(regions),
            'capacity_units': cap,
            'current_utilization_units': int(cap * random.uniform(0.1, 0.5)),
            'warehouse_type': random.choice(types),
            'active_flag': True
        })
    return pd.DataFrame(data)

def generate_suppliers(num_suppliers, product_df):
    data = []
    product_ids = product_df['product_id'].tolist()
    
    for i in range(num_suppliers):
        supp_id = f'SUP-{i+1:03d}'
        supp_name = faker.company()
        # Each supplier supplies a random subset of products
        supplied_products = random.sample(product_ids, k=max(1, len(product_ids) // num_suppliers))
        
        for pid in supplied_products:
            data.append({
                'supplier_id': supp_id,
                'supplier_name': supp_name,
                'product_id': pid,
                'lead_time_days': random.randint(2, 14),
                # Cost varies slightly by supplier
                'unit_cost': round(product_df.loc[product_df['product_id'] == pid, 'unit_cost'].values[0] * random.uniform(0.9, 1.1), 2),
                'reliability_score': round(random.uniform(0.7, 0.99), 2),
                'minimum_order_quantity': random.choice([50, 100, 500]),
                'active_flag': True
            })
    return pd.DataFrame(data)

def generate_weather(calendar_df, stores_df):
    data = []
    for _, store in stores_df.iterrows():
        base_temp = 20.0
        for _, cal in calendar_df.iterrows():
            # Add seasonal variation based on month
            month_effect = -10 if cal['month'] in [12, 1, 2] else (10 if cal['month'] in [6, 7, 8] else 0)
            temp = base_temp + month_effect + random.uniform(-5, 5)
            rain = random.uniform(0, 20) if random.random() > 0.8 else 0.0
            
            cond = 'Clear'
            if rain > 10: cond = 'Heavy Rain'
            elif rain > 0: cond = 'Light Rain'
            elif temp < 0: cond = 'Snow'
            
            data.append({
                'weather_date': cal['date'].date(),
                'city': store['city'],
                'temperature_avg': round(temp, 1),
                'temperature_max': round(temp + 5, 1),
                'temperature_min': round(temp - 5, 1),
                'rainfall_mm': round(rain, 1),
                'humidity': round(random.uniform(30, 90), 1),
                'weather_condition': cond
            })
    return pd.DataFrame(data)

def generate_all_master_data(config):
    # Set seed for reproducibility
    Faker.seed(config['seed'])
    random.seed(config['seed'])
    np.random.seed(config['seed'])
    
    cal_df = generate_calendar(config['start_date'], config['end_date'])
    prod_df = generate_products(config['num_products'])
    store_df = generate_stores(config['num_stores'])
    wh_df = generate_warehouses(config['num_warehouses'])
    sup_df = generate_suppliers(config['num_suppliers'], prod_df)
    wea_df = generate_weather(cal_df, store_df)
    
    return {
        'calendar': cal_df,
        'products': prod_df,
        'stores': store_df,
        'warehouses': wh_df,
        'suppliers': sup_df,
        'weather': wea_df
    }
