import pandas as pd
from .exceptions import DataQualityError

def validate_quality(file_path, registry_entry):
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)
        
    pk = registry_entry.get("primary_key")
    if pk and pk in df.columns:
        if df[pk].isnull().any():
            raise DataQualityError(f"Primary key {pk} contains nulls.")
    return True
