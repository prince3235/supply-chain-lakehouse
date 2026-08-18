import pandas as pd
import numpy as np
import random

def inject_quality_issues(datasets, config):
    """
    Takes clean datasets and injects controlled data quality issues based on configuration rates.
    """
    dirty_datasets = {}
    null_rate = config['quality'].get('null_rate', 0.01)
    duplicate_rate = config['quality'].get('duplicate_rate', 0.005)
    outlier_rate = config['quality'].get('outlier_rate', 0.002)
    
    np.random.seed(config['seed'] + 100) # Deterministic but different from clean seed
    
    for name, df in datasets.items():
        if df is None or df.empty:
            dirty_datasets[name] = df
            continue
            
        dirty_df = df.copy()
        
        # 1. Inject Nulls (Randomly drop values in random columns)
        if null_rate > 0:
            # We don't want to break PKs usually, but for dirty data, we can corrupt some FKs or metrics
            cols_to_corrupt = [
                c for c in dirty_df.columns 
                if c not in ['date', 'transaction_id', 'product_id'] 
                and dirty_df[c].dtype != 'bool'
            ]
            if cols_to_corrupt:
                for col in cols_to_corrupt:
                    # Create a mask for rows to set to None/NaN
                    mask = np.random.random(len(dirty_df)) < null_rate
                    dirty_df.loc[mask, col] = np.nan
                    
        # 2. Inject Duplicates
        if duplicate_rate > 0 and len(dirty_df) > 0:
            num_dups = int(len(dirty_df) * duplicate_rate)
            if num_dups > 0:
                dups = dirty_df.sample(n=num_dups, replace=True)
                dirty_df = pd.concat([dirty_df, dups], ignore_index=True)
                
        # 3. Inject Outliers (Only in numeric columns)
        if outlier_rate > 0:
            num_cols = dirty_df.select_dtypes(include=[np.number]).columns
            for col in num_cols:
                if col in ['day_of_week', 'month', 'year', 'quarter']: continue # Skip calendar int IDs
                mask = np.random.random(len(dirty_df)) < outlier_rate
                # Multiply by 100 or -100 to make obvious outliers
                dirty_df.loc[mask, col] = dirty_df.loc[mask, col] * np.random.choice([100, -100])
                
        dirty_datasets[name] = dirty_df
        
    return dirty_datasets
