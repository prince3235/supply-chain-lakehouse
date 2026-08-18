# Phase 6 — Silver Layer Implementation Plan

## Objective
Build a robust, PySpark-based data cleaning and validation layer that ingests raw Bronze Delta tables, cleanses the data (standardizing types, null handling, deduplication), applies business rules and referential integrity checks, and loads the output into Silver Delta tables.

## Architecture
- **Source**: `supply_chain_dev.bronze.<dataset>`
- **Target**: `supply_chain_dev.silver.<dataset>`
- **Processing Framework**: PySpark
- **Format**: Delta Lake
- **Execution Pattern**: Incremental Delta Merge (Idempotent)

## Core Components
1. **Cleaner (`cleaner.py`)**: Responsible for:
   - Deduplication (keeping the most recent record per primary key)
   - Null handling (e.g., standardizing string nulls, providing defaults where appropriate)
   - Data type casting (e.g., ensuring dates are properly formatted)
2. **Validator (`validator.py`)**: Responsible for:
   - Applying Data Quality gates: Completeness, Uniqueness, Validity.
   - Separating valid records from invalid records (Quarantine path).
3. **Pipeline Orchestrator (`pipeline.py`)**: Responsible for:
   - Coordinating the read stream from Bronze, passing through `Cleaner` and `Validator`, and writing to Silver.

## Data Quality Rules
- *Primary Keys*: Must be completely unique and non-null (e.g., `transaction_id`, `product_id`).
- *Foreign Keys*: (Future) Checked against master datasets.
- *Date ranges*: Standardized to `yyyy-MM-dd`.
