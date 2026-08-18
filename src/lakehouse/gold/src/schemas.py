"""
Gold Layer Schemas & Contracts
Defines expected schema characteristics for aggregated gold tables.
"""

GOLD_CONTRACTS = {
    "dim_product": {
        "primary_keys": ["product_id"],
        "grain": "product"
    },
    "dim_supplier": {
        "primary_keys": ["supplier_id"],
        "grain": "supplier"
    },
    "dim_store": {
        "primary_keys": ["store_id"],
        "grain": "store"
    },
    "fact_sales": {
        "primary_keys": ["transaction_id"],
        "grain": "transaction_line"
    },
    "gold_inventory_health": {
        "primary_keys": ["product_id", "store_id", "warehouse_id", "snapshot_date"],
        "grain": "product_location_date"
    },
    "gold_supplier_performance": {
        "primary_keys": ["supplier_id", "performance_period"],
        "grain": "supplier_period"
    },
    "gold_daily_demand": {
        "primary_keys": ["product_id", "store_id", "demand_date"],
        "grain": "product_store_date"
    },
    "gold_shipment_performance": {
        "primary_keys": ["warehouse_id", "delivery_date"],
        "grain": "warehouse_date"
    }
}

def get_gold_contract(dataset_name: str) -> dict:
    """Returns the contract mapping for a gold dataset."""
    return GOLD_CONTRACTS.get(dataset_name, {})
