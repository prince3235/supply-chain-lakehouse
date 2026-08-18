from unittest.mock import MagicMock, patch
import pytest

from src.validator import SilverValidator

def test_validator_no_rules():
    """Test validator when no rules are provided."""
    validator = SilverValidator("test_ds", {})
    mock_df = MagicMock()
    mock_df.schema = MagicMock()
    mock_df.sparkSession.createDataFrame.return_value = "empty_df"
    
    valid, invalid = validator.validate(mock_df, "run-123")
    
    assert valid == mock_df
    assert invalid == "empty_df"

def test_validator_with_rules():
    """Test validator successfully applies rules and generates valid/invalid splits."""
    contract = {
        "validation_rules": {
            "col1": {"not_null": True},
            "col2": {"min": 0}
        }
    }
    validator = SilverValidator("test_ds", contract)
    mock_df = MagicMock()
    mock_df.columns = ["col1", "col2"]
    
    mock_df.filter.side_effect = ["valid_df", "invalid_raw_df"]
    
    # We need to mock invalid_raw_df's withColumn for metadata
    mock_invalid_raw = MagicMock()
    mock_invalid_raw.withColumn.return_value = "invalid_df_with_meta"
    
    # Override filter to return our mock for the second call
    mock_df.filter.side_effect = ["valid_df", mock_invalid_raw]
    
    valid, invalid = validator.validate(mock_df, "run-123")
    
    assert mock_df.filter.call_count == 2
    assert valid == "valid_df"
    assert invalid == "invalid_df_with_meta"
    assert mock_invalid_raw.withColumn.call_count == 1
