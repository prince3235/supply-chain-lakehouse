from unittest.mock import MagicMock
from src.facts import build_fact_sales, build_fact_inventory, build_fact_shipments

def test_build_fact_sales():
    mock_df = MagicMock()
    mock_df.select.return_value = "fact_sales_df"
    result = build_fact_sales(mock_df)
    assert result == "fact_sales_df"

def test_build_fact_inventory():
    mock_df = MagicMock()
    mock_df.select.return_value = "fact_inventory_df"
    result = build_fact_inventory(mock_df)
    assert result == "fact_inventory_df"

def test_build_fact_shipments():
    mock_df = MagicMock()
    mock_df.select.return_value = "fact_shipments_df"
    result = build_fact_shipments(mock_df)
    assert result == "fact_shipments_df"
