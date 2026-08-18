# Phase 6 — Silver Layer (Hardened)

## Status
IMPLEMENTATION COMPLETE 
(Live AWS/Databricks Validation: PENDING — AWS infrastructure unavailable)

## Overview
The Silver Layer has been hardened into a production-grade component. It acts as a strict data quality gate between the Bronze data lake and downstream analytical/ML layers.

## Architecture & Components
1. **`cleaner.py`**: Deterministic whitespace trimming and configurable NULL normalization. Ensures idempotency via window-function deduplication.
2. **`transformer.py`**: Safe type casting and structural transformations according to the defined schema.
3. **`validator.py`**: Robust constraint validation (NOT NULL, MIN, ENUM). Appends detailed quarantine metadata to invalid records (`validation_rule`, `failure_reason`).
4. **`quarantine.py`**: Handles safe append-only writes to the Quarantine Delta tables, ensuring no valid data is lost while isolating corrupt records.
5. **`pipeline.py`**: Orchestrates the process. Validates strict schema presence before execution. Uses Delta `MERGE` semantics for idempotent Silver table updates.
6. **`schemas.py`**: Centralized data contracts derived from `DATA_CONTRACT.md`.

## Data Quality & Quarantine Strategy
- Invalid records are separated via `validator.py`.
- Valid records → Silver Delta Table
- Invalid records → Quarantine Delta Table (with augmented failure metadata)

## Idempotency
- The pipeline utilizes `DeltaTable.merge()` against primary keys to ensure that re-running the same Bronze data does not result in duplicate Silver records.
- If primary keys are absent in the contract, a fallback append is used, with a warning logged.

## Local Validation
- A deterministic testing strategy using `unittest.mock` has been implemented in `tests/`.
- True local PySpark execution is blocked by the missing local Java Runtime Environment (`[JAVA_GATEWAY_EXITED]`).
- Live Delta validation cannot be performed until the Phase 5 AWS unblock occurs.

## Remaining Work
- End-to-end execution on live Databricks cluster (blocked).
- Integration with an orchestration tool (e.g., Apache Airflow or Databricks Workflows).
