from unittest.mock import MagicMock
import pytest

from src.transformer import SilverTransformer

def test_apply_type_casts():
    contract = {
        "validation_rules": {
            "col_num": {"type": "numeric"},
            "col_str": {"type": "string"},
            "col_date": {"type": "date"}
        }
    }
    
    mock_df = MagicMock()
    mock_df.columns = ["col_num", "col_str", "col_date", "other_col"]
    mock_df.withColumn.return_value = mock_df
    
    transformer = SilverTransformer(contract)
    result = transformer.transform(mock_df)
    
    # Check that withColumn was called for the 3 typed columns
    assert mock_df.withColumn.call_count == 3
