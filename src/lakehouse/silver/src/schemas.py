"""
Centralized schema and data contract definitions for the Silver Layer.
"""

DATA_CONTRACTS = {
    "sales": {
        "primary_keys": ["transaction_id"],
        "required_columns": [
            "transaction_id",
            "product_id",
            "store_id",
            "quantity",
            "transaction_date"
        ],
        "validation_rules": {
            "transaction_id": {"not_null": True, "type": "string"},
            "product_id": {"not_null": True, "type": "string"},
            "store_id": {"not_null": True, "type": "string"},
            "quantity": {"not_null": True, "type": "numeric", "min": 1},
            "unit_price": {"type": "numeric", "min": 0},
            "transaction_date": {"not_null": True, "type": "date"}
        }
    },
    "products": {
        "primary_keys": ["product_id"],
        "required_columns": [
            "product_id",
            "product_name",
            "category"
        ],
        "validation_rules": {
            "product_id": {"not_null": True, "type": "string"},
            "product_name": {"not_null": True, "type": "string"},
            "category": {"not_null": True, "type": "string"}
        }
    },
    "inventory": {
        "primary_keys": ["inventory_id"],
        "required_columns": [
            "inventory_id",
            "product_id",
            "warehouse_id",
            "current_stock"
        ],
        "validation_rules": {
            "inventory_id": {"not_null": True, "type": "string"},
            "product_id": {"not_null": True, "type": "string"},
            "warehouse_id": {"not_null": True, "type": "string"},
            "current_stock": {"not_null": True, "type": "numeric", "min": 0}
        }
    }
}

def get_contract(dataset_name: str) -> dict:
    """Returns the data contract for a given dataset."""
    return DATA_CONTRACTS.get(dataset_name, {})
