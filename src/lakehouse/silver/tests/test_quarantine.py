from unittest.mock import MagicMock
import pytest

from src.quarantine import QuarantineHandler

def test_quarantine_handler():
    mock_spark = MagicMock()
    handler = QuarantineHandler(mock_spark, "dev", "test-bucket")
    
    mock_invalid_df = MagicMock()
    mock_invalid_df.count.return_value = 5
    
    handler.quarantine_records("sales", mock_invalid_df)
    
    # Assert write was called with correct format and mode
    assert mock_invalid_df.write.format.called
    mock_invalid_df.write.format.assert_called_with("delta")
    mock_invalid_df.write.format.return_value.mode.assert_called_with("append")

def test_quarantine_handler_empty():
    mock_spark = MagicMock()
    handler = QuarantineHandler(mock_spark, "dev", "test-bucket")
    
    mock_invalid_df = MagicMock()
    mock_invalid_df.count.return_value = 0
    
    handler.quarantine_records("sales", mock_invalid_df)
    
    # Assert write was NOT called
    assert not mock_invalid_df.write.format.called
