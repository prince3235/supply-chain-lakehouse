"""
Mock Data Generator for Streamlit Command Center.
Supplies realistic dynamic data for dashboard demonstrations when lakehouse is offline.
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_mock_dashboard_data():
    """Generates complete mock datasets for the Supply Chain Command Center."""
    products = [
        {"id": "P1001", "name": "Wireless Ergonomic Mouse", "category": "Electronics", "unit_price": 45.0},
        {"id": "P1002", "name": "Mechanical Keyboard RGB", "category": "Electronics", "unit_price": 95.0},
        {"id": "P1003", "name": "Ultra HD 4K Monitor", "category": "Electronics", "unit_price": 320.0},
        {"id": "P2001", "name": "Organic Arabica Coffee 1kg", "category": "Grocery", "unit_price": 18.5},
        {"id": "P2002", "name": "Green Tea Matcha Pack", "category": "Grocery", "unit_price": 12.0},
        {"id": "P3001", "name": "Cotton Crewneck T-Shirt", "category": "Apparel", "unit_price": 24.0},
        {"id": "P3002", "name": "Thermal Running Jacket", "category": "Apparel", "unit_price": 78.0},
    ]
    stores = [
        {"id": "S001", "name": "Downtown Megastore", "city": "Seattle"},
        {"id": "S002", "name": "Bay Area Hub", "city": "San Francisco"},
        {"id": "S003", "name": "Metro Distribution", "city": "Austin"},
    ]
    suppliers = [
        {"id": "SUP_01", "name": "Global Tech Logistics", "lead_time": 5.0, "reliability": 96.5},
        {"id": "SUP_02", "name": "Apex Manufacturing", "lead_time": 9.0, "reliability": 91.2},
        {"id": "SUP_03", "name": "Direct Agro Imports", "lead_time": 4.0, "reliability": 98.0},
        {"id": "SUP_04", "name": "Textile Horizon Ltd", "lead_time": 12.0, "reliability": 85.4},
    ]

    base_date = datetime.now() - timedelta(days=60)
    history_records = []
    
    for p in products:
        for s in stores:
            base_demand = np.random.uniform(15.0, 50.0)
            for d in range(60):
                curr_date = base_date + timedelta(days=d)
                day_of_week = curr_date.weekday()
                weekend_boost = 1.3 if day_of_week in [5, 6] else 1.0
                noise = np.random.normal(0, 3.0)
                demand = max(2.0, (base_demand + noise) * weekend_boost)
                
                history_records.append({
                    "product_id": p["id"],
                    "product_name": p["name"],
                    "category": p["category"],
                    "store_id": s["id"],
                    "store_name": s["name"],
                    "demand_date": curr_date.strftime("%Y-%m-%d"),
                    "daily_demand": round(demand, 1),
                    "unit_price": p["unit_price"],
                    "total_available": max(10, int(np.random.normal(120, 30))),
                    "current_safety_stock": 25.0,
                })

    df_history = pd.DataFrame(history_records)
    df_products = pd.DataFrame(products)
    df_stores = pd.DataFrame(stores)
    df_suppliers = pd.DataFrame(suppliers)

    return {
        "history": df_history,
        "products": df_products,
        "stores": df_stores,
        "suppliers": df_suppliers,
    }
