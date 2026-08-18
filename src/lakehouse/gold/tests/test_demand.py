from unittest.mock import MagicMock
from src.demand import build_daily_demand

def test_build_daily_demand():
    mock_df = MagicMock()
    mock_df.withColumn.return_value.groupBy.return_value.agg.return_value = "gold_demand"
    result = build_daily_demand(mock_df)
    assert result == "gold_demand"
