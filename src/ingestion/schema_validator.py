import pandas as pd
from .exceptions import SchemaValidationError

def validate_schema(file_path, registry_entry):
    try:
        if file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            df = pd.read_csv(file_path)
            
        required_cols = set(registry_entry["required_columns"])
        actual_cols = set(df.columns)
        
        missing = required_cols - actual_cols
        if missing:
            raise SchemaValidationError(f"Missing required columns: {missing}")
            
        return len(df)
    except Exception as e:
        raise SchemaValidationError(f"Error reading file {file_path}: {e}")
