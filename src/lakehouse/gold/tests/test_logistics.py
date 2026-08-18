from unittest.mock import MagicMock
from src.logistics import build_shipment_performance

def test_build_shipment_performance():
    mock_df = MagicMock()
    mock_df.withColumn.return_value.groupBy.return_value.agg.return_value = "gold_logistics"
    result = build_shipment_performance(mock_df)
    assert result == "gold_logistics"
