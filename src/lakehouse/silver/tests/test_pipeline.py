from unittest.mock import MagicMock, patch
import pytest

from src.pipeline import SilverPipeline

@patch("src.pipeline.SilverCleaner")
@patch("src.pipeline.SilverValidator")
@patch("src.pipeline.SilverTransformer")
@patch("src.pipeline.QuarantineHandler")
@patch("src.pipeline.DeltaTable")
@patch("src.pipeline.get_contract")
def test_pipeline_happy_path(
    mock_get_contract,
    mock_delta_table,
    mock_quarantine,
    mock_transformer,
    mock_validator,
    mock_cleaner
):
    """Test full execution of the silver pipeline."""
    mock_get_contract.return_value = {
        "primary_keys": ["id"],
        "required_columns": ["id", "val"]
    }
    
    mock_spark = MagicMock()
    mock_spark.catalog.tableExists.return_value = True
    
    mock_df = MagicMock()
    mock_df.count.return_value = 100
    mock_df.columns = ["id", "val", "ts"]
    mock_spark.table.return_value = mock_df
    
    # Mock components
    mock_cleaner_instance = mock_cleaner.return_value
    mock_cleaner_instance.execute.return_value = "cleaned_df"
    
    mock_transformer_instance = mock_transformer.return_value
    mock_transformer_instance.transform.return_value = "transformed_df"
    
    mock_validator_instance = mock_validator.return_value
    mock_valid_df = MagicMock()
    mock_valid_df.count.return_value = 90
    mock_invalid_df = MagicMock()
    mock_invalid_df.count.return_value = 10
    mock_validator_instance.validate.return_value = (mock_valid_df, mock_invalid_df)
    
    # Run
    pipeline = SilverPipeline(mock_spark, "dev", "test-bucket")
    pipeline.process("sales")
    
    # Assert
    assert mock_cleaner_instance.execute.called
    assert mock_transformer_instance.transform.called
    assert mock_validator_instance.validate.called
    
    # Verify quarantine was called
    quarantine_instance = mock_quarantine.return_value
    quarantine_instance.quarantine_records.assert_called_with("sales", mock_invalid_df)
    
    # Verify silver write was called
    assert mock_delta_table.isDeltaTable.called

@patch("src.pipeline.get_contract")
def test_pipeline_schema_mismatch(mock_get_contract):
    """Test that pipeline aborts if strict schema is violated."""
    mock_get_contract.return_value = {
        "required_columns": ["id", "missing_col"]
    }
    
    mock_spark = MagicMock()
    mock_spark.catalog.tableExists.return_value = True
    
    mock_df = MagicMock()
    mock_df.columns = ["id"] # missing_col is absent
    mock_spark.table.return_value = mock_df
    
    pipeline = SilverPipeline(mock_spark, "dev", "test-bucket")
    
    with pytest.raises(ValueError, match="Schema mismatch: Missing required columns"):
        pipeline.process("sales")
