from unittest.mock import MagicMock
from src.inventory import build_inventory_health

def test_build_inventory_health():
    mock_df = MagicMock()
    mock_df.withColumn.return_value.groupBy.return_value.agg.return_value.withColumn.return_value = "gold_inventory"
    
    result = build_inventory_health(mock_df)
    
    assert result == "gold_inventory"
    assert mock_df.withColumn.called
