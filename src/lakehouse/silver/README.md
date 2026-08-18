# Silver Layer

## Overview
The Silver Layer provides clean, standardized, deduplicated, and business-validated datasets. It ingests data incrementally from the Bronze layer and ensures data quality.

## Execution
The Silver pipeline is executed via `pipeline.py`.

## Data Quality
- Schema tracking
- Deduplication by Primary Key
- Strict Not Null constraints for critical fields
- Invalid records routed to `s3://<bucket>/quarantine/silver`
