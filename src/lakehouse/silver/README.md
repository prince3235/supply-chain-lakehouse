# Supply Chain Lakehouse — Silver Layer

The Silver Layer is responsible for transforming raw, immutable Bronze data into clean, standardized, deduplicated, and business-validated datasets.

## Architecture

- **`cleaner.py`**: Trims strings, normalizes NULL literals, and deduplicates records.
- **`transformer.py`**: Casts data types to ensure schema conformity.
- **`validator.py`**: Validates records against data quality constraints (NOT NULL, MIN, ENUM).
- **`quarantine.py`**: Manages the isolation of invalid records.
- **`pipeline.py`**: Orchestrates incremental, idempotent execution via Delta `MERGE`.
- **`schemas.py`**: Defines the data contracts.

## Data Quality Flow

```text
RAW BRONZE DATA
       ↓
   CLEANING
       ↓
TRANSFORMATION
       ↓
  VALIDATION
       ↓
  ┌─────────┐
  │         │
VALID    INVALID
  ↓         ↓
SILVER   QUARANTINE
```

## Testing
Run local mock tests via:
`PYTHONPATH="src/lakehouse/silver" pytest src/lakehouse/silver/tests/`
