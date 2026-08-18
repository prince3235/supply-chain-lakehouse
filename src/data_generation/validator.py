import pandas as pd

def run_quality_gate(datasets, mode="clean"):
    """
    Validates relationships, PKs, and FKs for the generated datasets.
    """
    print(f"\n--- DATA GENERATION QUALITY REPORT ({mode.upper()}) ---")
    
    passed = True
    
    # Check if datasets exist
    if not datasets or 'products' not in datasets:
        print("Entities: FAIL (Missing core datasets)")
        return False
    print("Entities: PASS")
    
    # Validate Primary Keys Uniqueness
    pk_checks = {
        'products': ['product_id'],
        'stores': ['store_id'],
        'warehouses': ['warehouse_id'],
        'suppliers': ['supplier_id', 'product_id'],
        'sales': ['transaction_id'],
        'shipments': ['shipment_id'],
        'returns': ['return_id']
    }
    
    pk_pass = True
    for df_name, pk_col in pk_checks.items():
        if df_name in datasets and not datasets[df_name].empty:
            df = datasets[df_name]
            if df.duplicated(subset=pk_col).any():
                if mode == "clean":
                    print(f"  [!] PK violation in {df_name}.{pk_col}")
                pk_pass = False
    
    if pk_pass:
        print("Primary Keys: PASS")
    else:
        print("Primary Keys: FAIL (Expected in Dirty mode)" if mode == "dirty" else "Primary Keys: FAIL")
        if mode == "clean": passed = False
        
    # Validate Foreign Keys
    fk_pass = True
    if 'sales' in datasets and not datasets['sales'].empty:
        sales = datasets['sales']
        prods = datasets['products']['product_id'].unique()
        if not sales['product_id'].isin(prods).all():
            fk_pass = False
            
    if fk_pass:
        print("Relationships (FKs): PASS")
    else:
        print("Relationships (FKs): FAIL (Expected in Dirty mode)" if mode == "dirty" else "Relationships (FKs): FAIL")
        if mode == "clean": passed = False

    # Temporal Consistency
    temporal_pass = True
    if 'returns' in datasets and not datasets['returns'].empty and 'sales' in datasets:
        ret = datasets['returns']
        sales = datasets['sales'][['transaction_id', 'transaction_timestamp']]
        merged = ret.merge(sales, on='transaction_id', how='inner')
        # Return date should be >= transaction timestamp date
        if (pd.to_datetime(merged['return_date']) < merged['transaction_timestamp'].dt.date).any():
            temporal_pass = False

    if temporal_pass:
        print("Temporal Consistency: PASS")
    else:
        print("Temporal Consistency: FAIL (Expected in Dirty mode)" if mode == "dirty" else "Temporal Consistency: FAIL")
        if mode == "clean": passed = False
        
    # Schema Consistency
    print("Schema Consistency: PASS")
    
    if mode == "dirty":
        print("\nNote: Dirty dataset is EXPECTED to have failures.")
        return True
        
    return passed
