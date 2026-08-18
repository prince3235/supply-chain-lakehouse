import pytest
import os
import pandas as pd
from src.data_generation.config_loader import load_config
from src.data_generation.generators.master_data import generate_all_master_data
from src.data_generation.generators.transactional_data import generate_transactional_data

@pytest.fixture(scope="module")
def config():
    # Use small profile for quick tests
    return load_config(profile="small")

@pytest.fixture(scope="module")
def datasets(config):
    master = generate_all_master_data(config)
    txn = generate_transactional_data(config, master)
    return {**master, **txn}

def test_deterministic_generation():
    """Test that same config + seed produces identical outputs"""
    cfg = load_config(profile="small")
    d1 = generate_all_master_data(cfg)
    d2 = generate_all_master_data(cfg)
    
    cols_to_drop = ['created_at', 'updated_at']
    assert d1['products'].drop(columns=cols_to_drop).equals(d2['products'].drop(columns=cols_to_drop))
    assert d1['stores'].equals(d2['stores'])

def test_primary_key_uniqueness(datasets):
    assert not datasets['products']['product_id'].duplicated().any()
    assert not datasets['stores']['store_id'].duplicated().any()
    if not datasets['sales'].empty:
        assert not datasets['sales']['transaction_id'].duplicated().any()

def test_foreign_key_validity(datasets):
    if not datasets['sales'].empty:
        sales = datasets['sales']
        products = datasets['products']
        stores = datasets['stores']
        
        # All sales must have valid product and store
        assert sales['product_id'].isin(products['product_id']).all()
        assert sales['store_id'].isin(stores['store_id']).all()

def test_revenue_calculation(datasets):
    if not datasets['sales'].empty:
        sales = datasets['sales']
        calculated_total = (sales['quantity'] * sales['unit_price']) - sales['discount_amount']
        # Floating point precision check
        assert (sales['total_amount'] - calculated_total).abs().max() < 0.01

def test_return_quantity_validity(datasets):
    if not datasets['returns'].empty and not datasets['sales'].empty:
        returns = datasets['returns']
        sales = datasets['sales']
        
        merged = returns.merge(sales, on='transaction_id', suffixes=('_ret', '_sale'))
        # Return quantity should not exceed sale quantity
        assert (merged['quantity_ret'] <= merged['quantity_sale']).all()
        # Return date should be >= sale date
        assert (pd.to_datetime(merged['return_date']) >= merged['transaction_timestamp'].dt.date).all()

def test_shipment_date_validity(datasets):
    if not datasets['shipments'].empty:
        ship = datasets['shipments']
        # Actual delivery >= order date
        assert (pd.to_datetime(ship['actual_delivery_date']) >= pd.to_datetime(ship['order_date'])).all()
        # Delay days >= 0
        assert (ship['delay_days'] >= 0).all()
