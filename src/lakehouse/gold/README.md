# Gold Layer

The Gold Layer is the final stage of the Supply Chain Lakehouse data processing pipeline. It transforms trusted, validated Silver data into business-ready analytical datasets, serving both traditional Business Intelligence (BI) and advanced Machine Learning (ML) use cases.

## Key Datasets

### Dimensions
- `dim_product`: Product attributes
- `dim_store`: Store attributes
- `dim_supplier`: Supplier attributes

### Facts
- `fact_sales`: Transactional sales lines
- `fact_inventory`: Inventory snapshots
- `fact_shipments`: Shipment records

### Business Analytics
- `gold_inventory_health`: Stockout risks and inventory valuations
- `gold_supplier_performance`: Supplier delays and on-time rates
- `gold_daily_demand`: Core analytical dataset for ML demand forecasting
- `gold_shipment_performance`: Warehouse incoming shipment logistics

## Execution
The pipeline leverages Delta `MERGE` to remain strictly idempotent. Duplicate executions on the same batch will result in matched updates rather than appended duplicates.
