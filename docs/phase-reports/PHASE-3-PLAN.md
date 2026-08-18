# Phase 3 — Synthetic Data Generation Plan

## 1. Objective
Develop a completely reproducible, configurable, and realistic Python-based data generation framework to produce a relational supply chain ecosystem (10 datasets). This data must be temporally consistent and ML-friendly for future Lakehouse pipelines.

## 2. Dataset Architecture
The ecosystem will contain 10 datasets divided into reference and transactional data:
- **Reference**: `products`, `stores`, `warehouses`, `suppliers`, `calendar`, `weather`.
- **Transactional**: `sales`, `inventory`, `shipments`, `returns`.

## 3. Entity Relationships
- **products** 1:M **sales, inventory, shipments, returns**
- **stores** 1:M **sales, inventory, returns, weather**
- **warehouses** 1:M **inventory, shipments**
- **suppliers** 1:M **shipments**
- **calendar** 1:M **sales, inventory, shipments, returns**

## 4. Generation Order
1. Calendar & Weather (Temporal baseline)
2. Master Data (Products, Stores, Warehouses, Suppliers)
3. Shipments & Inventory (Supply mechanics)
4. Sales (Demand mechanics based on inventory constraints)
5. Returns (Based on successful sales)

## 5. Primary and Foreign Keys
All relationships will strictly enforce primary/foreign key mappings (e.g. `transaction_id` maps to `returns`). Schemas will strictly match `docs/data/DATA_DICTIONARY.md`.

## 6. Data Volumes (Profiles)
- **Small**: 1 store, 10 products, 1 month (ideal for pytest/local dev).
- **Medium**: 10 stores, 100 products, 6 months (ideal for CI/CD integration testing).
- **Large**: 50 stores, 500 products, 2 years (ideal for performance testing).

## 7. Temporal Design
A continuous calendar dimension will serve as the backbone. All events (shipments, sales, returns) will exist on a realistic timeline (e.g., shipments must arrive before stock becomes available; sales cannot happen if stock is zero; returns occur *after* sales).

## 8. Business Logic
- **Inventory Equations**: `closing_inventory = opening_inventory + received - sold`.
- **Shipments**: Lead times and delivery delays depend on supplier reliability scores.
- **Stockouts**: When `available_quantity` hits zero, `sales` are constrained.

## 9. Demand-Generation Strategy
Demand will not be purely random. It will use a synthetic formula internally:
`Base Demand + Weekly Seasonality + Holiday Lift + Promotion Lift + Random Noise`.
This ensures a learnable signal for future ML forecasting models.

## 10. Data-Quality Injection Strategy
A completely separate "dirty" pipeline will inject controlled anomalies into a copy of the clean data, governed by configurable rates (e.g., `null_rate = 0.01`).

## 11. Reproducibility Strategy
All random number generators (e.g., `np.random.seed()`, `random.seed()`, Faker) will be seeded globally and per-dataset to guarantee deterministic outputs for any given configuration.

## 12. Configuration Strategy
A YAML file (`configs/data_generation.yaml`) will control profiles, seeds, dates, and corruption rates.

## 13. Testing Strategy
- Unit tests (`tests/data/`) will validate FK integrity, PK uniqueness, inventory math, and return logic.
- An automated Quality Gate will output a pass/fail report for the generated dataset.

## 14. Performance Strategy
- Use `pandas` and `numpy` vectorized operations where possible instead of slow nested iterrows.
- Dataframes will be written to Parquet to save disk space and read time.

## 15. Output Structure
```
data/
└── generated/
    ├── clean/
    │   ├── products/
    │   └── ...
    └── dirty/
        ├── products/
        └── ...
```

## 16. Explicit Non-Goals
- No Databricks integration or PySpark yet.
- No S3 uploading.
- No actual ML model training.

## 17. Definition of Done
The generator runs via CLI, outputs 10 parquet datasets across clean/dirty branches, and passes all pytests and the internal Quality Gate while adhering to schemas.
