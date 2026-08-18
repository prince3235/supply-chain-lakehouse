from unittest.mock import MagicMock, patch
import pytest

from src.cleaner import SilverCleaner

def test_normalize_strings_and_nulls():
    """Test that cleaner correctly identifies string columns and applies transformations."""
    cleaner = SilverCleaner(null_literals=["NA"])
    
    # Mock PySpark DataFrame
    mock_df = MagicMock()
    mock_field1 = MagicMock()
    mock_field1.name = "col1"
    mock_field1.dataType.typeName.return_value = "string"
    
    mock_field2 = MagicMock()
    mock_field2.name = "col2"
    mock_field2.dataType.typeName.return_value = "integer"
    
    mock_df.schema.fields = [mock_field1, mock_field2]
    
    # Mock withColumn to just return self for chaining
    mock_df.withColumn.return_value = mock_df
    
    # Execute
    result_df = cleaner.normalize_strings_and_nulls(mock_df)
    
    # Verify that withColumn was called for the string column (col1) but not the int column (col2)
    assert mock_df.withColumn.call_count == 1
    call_args = mock_df.withColumn.call_args[0]
    assert call_args[0] == "col1"

def test_deduplicate_with_keys():
    """Test deduplication logic with primary keys."""
    cleaner = SilverCleaner(primary_keys=["id"], order_by_col="ts")
    mock_df = MagicMock()
    mock_df.columns = ["id", "val", "ts"]
    
    # Setup mock chain
    mock_df.withColumn.return_value = mock_df
    mock_df.filter.return_value = mock_df
    mock_df.drop.return_value = mock_df
    
    result = cleaner.deduplicate(mock_df)
    
    # Verify the chain was executed
    assert mock_df.withColumn.called
    assert mock_df.filter.called
    assert mock_df.drop.called

def test_deduplicate_fallback():
    """Test deduplication fallback when primary keys or order_by are missing."""
    # No order_by col in df
    cleaner = SilverCleaner(primary_keys=["id"], order_by_col="missing_ts")
    mock_df = MagicMock()
    mock_df.columns = ["id", "val"]
    
    cleaner.deduplicate(mock_df)
    assert mock_df.dropDuplicates.called
