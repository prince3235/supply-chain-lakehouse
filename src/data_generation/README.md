# Synthetic Data Generation

This module generates a realistic, relational, ML-ready synthetic supply chain dataset.

## Features
- Generates 10 interconnected datasets: Products, Stores, Warehouses, Suppliers, Calendar, Weather, Sales, Inventory, Shipments, Returns.
- Simulates realistic demand curves (seasonality, holiday lifts, store multipliers).
- Simulates inventory mechanics (stockouts, reorder points, delays based on supplier reliability).
- Generates a `clean` dataset and a configurable `dirty` dataset.

## Setup
Ensure requirements are installed:
```bash
pip install pandas numpy faker pyarrow pyyaml
```

## Configuration
Edit `configs/data_generation.yaml` to change:
- `profiles` (small, medium, large)
- `seed`
- Data quality corruption rates.

## Usage
Run the generator using Python's module execution from the project root:

```bash
python -m src.data_generation --profile small
```

This will:
1. Generate master and transactional data.
2. Inject data quality issues to create a dirty copy.
3. Run internal Data Quality Gates.
4. Output parquet files and manifests to `data/generated/`.
