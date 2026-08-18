from unittest.mock import MagicMock, patch
import pytest
from src.pipeline import GoldPipeline

@patch("src.pipeline.DeltaTable")
@patch("src.pipeline.get_gold_contract")
def test_write_gold_table_overwrite(mock_get_contract, mock_delta_table):
    mock_get_contract.return_value = {"primary_keys": ["id"]}
    mock_delta_table.isDeltaTable.return_value = False
    
    mock_spark = MagicMock()
    pipeline = GoldPipeline(mock_spark, "dev", "test-bucket")
    
    mock_df = MagicMock()
    mock_df.count.return_value = 100
    
    pipeline.write_gold_table("test_dataset", mock_df)
    
    # Assert it creates table
    assert mock_df.write.format.called
    mock_df.write.format.assert_called_with("delta")
    mock_df.write.format.return_value.mode.assert_called_with("overwrite")

@patch("src.pipeline.DeltaTable")
@patch("src.pipeline.get_gold_contract")
def test_write_gold_table_merge(mock_get_contract, mock_delta_table):
    mock_get_contract.return_value = {"primary_keys": ["id"]}
    mock_delta_table.isDeltaTable.return_value = True
    
    mock_spark = MagicMock()
    pipeline = GoldPipeline(mock_spark, "dev", "test-bucket")
    
    mock_df = MagicMock()
    mock_df.count.return_value = 100
    
    pipeline.write_gold_table("test_dataset", mock_df)
    
    # Assert it merges
    assert mock_delta_table.forName.called
    mock_dt = mock_delta_table.forName.return_value
    assert mock_dt.alias.return_value.merge.called
