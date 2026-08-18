from unittest.mock import MagicMock
from src.suppliers import build_supplier_performance

def test_build_supplier_performance():
    mock_df = MagicMock()
    mock_df.withColumn.return_value.groupBy.return_value.agg.return_value.withColumn.return_value = "gold_suppliers"
    result = build_supplier_performance(mock_df)
    assert result == "gold_suppliers"
