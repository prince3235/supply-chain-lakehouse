from unittest.mock import MagicMock
from src.dimensions import build_dim_product, build_dim_store, build_dim_supplier

def test_build_dim_product():
    mock_df = MagicMock()
    mock_df.select.return_value.dropDuplicates.return_value = "dim_product_df"
    
    result = build_dim_product(mock_df)
    
    assert result == "dim_product_df"
    assert mock_df.select.called
    assert mock_df.select.return_value.dropDuplicates.called

def test_build_dim_store():
    mock_df = MagicMock()
    mock_df.select.return_value.dropDuplicates.return_value = "dim_store_df"
    
    result = build_dim_store(mock_df)
    
    assert result == "dim_store_df"
    assert mock_df.select.called

def test_build_dim_supplier():
    mock_df = MagicMock()
    mock_df.select.return_value.dropDuplicates.return_value = "dim_supplier_df"
    
    result = build_dim_supplier(mock_df)
    
    assert result == "dim_supplier_df"
    assert mock_df.select.called
