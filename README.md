# Supply Chain Lakehouse

> **Enterprise-grade Data Engineering + Lakehouse + MLOps platform built on AWS + Databricks.**  
> Transforms fragmented supply-chain data into reliable analytics, demand forecasts, inventory intelligence, and continuously improving machine-learning systems.

<br>

```
          Raw Data  →  Ingest  →  Bronze  →  Silver  →  Gold  →  ML  →  Monitor  →  Retrain
```

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [System Architecture](#3-system-architecture)
4. [Medallion Data Architecture](#4-medallion-data-architecture)
5. [Gold Layer — Data Warehouse Model](#5-gold-layer--data-warehouse-model)
6. [ML & MLOps Pipeline](#6-ml--mlops-pipeline)
7. [Project Structure](#7-project-structure)
8. [Implementation Phases](#8-implementation-phases)
9. [Technology Stack](#9-technology-stack)
10. [Data Sources](#10-data-sources)
11. [Local Development Setup](#11-local-development-setup)
12. [Running Tests](#12-running-tests)
13. [Key Design Decisions](#13-key-design-decisions)
14. [Current Status](#14-current-status)

---

## 1. What Is This Project?

**Supply Chain Lakehouse** is an end-to-end data platform that ingests raw supply-chain data (sales, inventory, suppliers, shipments, weather, etc.) and processes it through a Bronze → Silver → Gold Lakehouse architecture on **AWS S3 + Databricks**, ultimately powering:

- **Business Intelligence** — Dashboards with KPIs, supplier performance, demand trends
- **Demand Forecasting** — ML model to predict product demand at Product × Store × Date grain
- **Inventory Intelligence** — Stockout risk detection, reorder recommendations
- **Anomaly Detection** — Supplier delays, shipment irregularities, demand spikes
- **Automated MLOps** — Drift detection + automated model retraining

This is a **portfolio-grade** project demonstrating production data engineering patterns including idempotent pipelines, Delta Lake MERGE, data quality contracts, schema evolution, and MLflow lifecycle management.

---

## 2. The Problem It Solves

Large supply-chain organizations generate millions of records across disconnected systems. Without a unified platform, teams face:

| Problem | Impact |
|---|---|
| Fragmented data across ERP, POS, WMS | No single source of truth |
| Poor demand forecasting | Stockouts (lost revenue) or overstock (holding cost) |
| No supplier visibility | Missed delivery SLAs |
| Manual ML retraining | Model drift goes undetected for weeks |
| No data quality enforcement | Bad data silently corrupts reports |

**This platform fixes all of the above** with a governed, automated, cloud-native Lakehouse.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
│                                                                              │
│   [Sales/POS]  [Inventory]  [Suppliers]  [Shipments]  [Weather]  [Returns] │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INGESTION LAYER (Phase 2)                          │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Batch Ingestion Engine                                             │   │
│   │  • Schema Validation    • Checksum / Idempotency                   │   │
│   │  • Data Contracts       • Quarantine (invalid records)             │   │
│   │  • Manifest Logging     • Audit Trail                              │   │
│   └─────────────────────────────────┬───────────────────────────────────┘   │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS S3 — DATA LAKE (Phase 5)                       │
│                                                                              │
│   s3://supply-chain-lakehouse/                                               │
│   ├── raw/                    ← original source files                       │
│   ├── bronze/                 ← Delta tables, raw+metadata                  │
│   ├── silver/                 ← Delta tables, cleaned+validated             │
│   └── gold/                   ← Delta tables, business-ready KPIs          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATABRICKS LAKEHOUSE                                  │
│                                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────────┐    │
│  │    BRONZE    │──▶│    SILVER    │──▶│            GOLD              │    │
│  │  (Phase 3)   │   │  (Phase 6)   │   │         (Phase 7)            │    │
│  │              │   │              │   │                              │    │
│  │ Raw Delta    │   │ Cleaned      │   │ Dimensions  Facts  Metrics   │    │
│  │ tables with  │   │ Validated    │   │ dim_product fact_sales        │    │
│  │ ingestion    │   │ Deduplicated │   │ dim_store   fact_inventory    │    │
│  │ metadata     │   │ Type-safe    │   │ dim_supplier fact_shipments   │    │
│  └──────────────┘   └──────────────┘   │             gold_daily_demand│    │
│                                        │             gold_inv_health   │    │
│                                        │             gold_supplier_perf│    │
│                                        └──────────────────────────────┘    │
│                                                       │                     │
│                             ┌─────────────────────────┤                     │
│                             │                         │                     │
│                             ▼                         ▼                     │
│                   ┌──────────────────┐   ┌───────────────────────────┐      │
│                   │   BI / SQL       │   │   ML FEATURE STORE        │      │
│                   │  Dashboards      │   │  (Phase 8 — Planned)      │      │
│                   │  KPI Reports     │   │  Rolling stats, lags,     │      │
│                   └──────────────────┘   │  seasonality, pricing,    │      │
│                                          │  weather signals          │      │
│                                          └─────────────┬─────────────┘      │
└────────────────────────────────────────────────────────┼────────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ML TRAINING + MLFLOW (Phase 9 — Planned)           │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │  Training Pipeline                                                 │    │
│   │  • Demand Forecasting (XGBoost / LightGBM)                       │    │
│   │  • Anomaly Detection                                               │    │
│   │  • MLflow Experiment Tracking                                      │    │
│   │  • Temporal Cross-Validation                                       │    │
│   └──────────────────────────────┬─────────────────────────────────────┘    │
│                                  │                                           │
│                                  ▼                                           │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  MLflow Model Registry                                           │      │
│   │  Staging → Production promotion gate                             │      │
│   └──────────────────────────────┬───────────────────────────────────┘      │
│                                  │                                           │
│              ┌───────────────────┴───────────────────┐                      │
│              ▼                                       ▼                      │
│   ┌──────────────────────┐               ┌──────────────────────────┐       │
│   │  BATCH PREDICTIONS   │               │  REAL-TIME SERVING       │       │
│   │  Scheduled daily     │               │  REST endpoint           │       │
│   │  demand forecasts    │               │  (MLflow serve)          │       │
│   └──────────────────────┘               └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MONITORING + DRIFT DETECTION (Phase 10 — Planned)     │
│                                                                              │
│   Data Quality ──┐                                                          │
│   Data Drift ────┼──▶  Threshold Breach  ──▶  Retraining Trigger           │
│   Model Drift ───┘                                                          │
│   MAPE Degradation                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Medallion Data Architecture

Each layer in the Lakehouse stores data as **Delta Lake** tables (ACID transactions, time travel, schema enforcement).

```
┌────────────────────────────────────────────────────────────────────┐
│                         BRONZE LAYER                                │
│                  "Raw data — source of truth"                       │
│                                                                     │
│  Source ──▶ Parquet/CSV ──▶ Delta table + ingestion metadata        │
│                                                                     │
│  Tables:  bronze_sales, bronze_inventory, bronze_products,          │
│           bronze_stores, bronze_warehouses, bronze_suppliers,       │
│           bronze_shipments, bronze_returns, bronze_weather,         │
│           bronze_calendar                                           │
│                                                                     │
│  Guarantees:  ✓ Source preserved as-is                              │
│               ✓ Batch ID tagged                                     │
│               ✓ Reprocessable                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼  (validates + cleans)
┌────────────────────────────────────────────────────────────────────┐
│                         SILVER LAYER                                │
│              "Cleaned, validated, type-safe data"                   │
│                                                                     │
│  Bronze ──▶ Schema check ──▶ Dedup ──▶ Type cast ──▶ Delta table   │
│                                                                     │
│  Tables:  silver_sales, silver_inventory, silver_products, ...      │
│                                                                     │
│  Guarantees:  ✓ No duplicates                                       │
│               ✓ No nulls in required fields                         │
│               ✓ Valid numeric ranges                                │
│               ✓ Invalid rows → quarantine (not silently dropped)   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼  (aggregates + enriches)
┌────────────────────────────────────────────────────────────────────┐
│                          GOLD LAYER                                 │
│           "Business-ready KPIs and analytical datasets"             │
│                                                                     │
│  Dimensions:  dim_product, dim_store, dim_supplier                  │
│  Facts:       fact_sales, fact_inventory, fact_shipments            │
│  Metrics:     gold_daily_demand, gold_inventory_health,             │
│               gold_supplier_performance, gold_shipment_performance  │
│                                                                     │
│  Write mode:  Delta MERGE (idempotent upserts on primary keys)      │
│                                                                     │
│  Guarantees:  ✓ No duplicate rows (MERGE on primary_keys)          │
│               ✓ Schema contract enforced via get_gold_contract()   │
│               ✓ Re-runnable pipelines                               │
└────────────────────────────────────────────────────────────────────┘
```

---

## 5. Gold Layer — Data Warehouse Model

The Gold layer follows a **star schema** design consumed by BI and ML.

```
                          ┌─────────────────┐
                          │   dim_product    │
                          │  product_id (PK) │
                          │  product_name    │
                          │  category        │
                          │  brand           │
                          │  unit_cost       │
                          └────────┬─────────┘
                                   │
          ┌─────────────┐          │          ┌──────────────────┐
          │  dim_store  │          │          │  dim_supplier    │
          │  store_id   ├──────────┤          │  supplier_id (PK)│
          │  store_name │          │          │  supplier_name   │
          │  city/state │          │          │  lead_time_days  │
          │  region     │          │          └────────┬─────────┘
          └──────┬──────┘          │                   │
                 │                 │                   │
                 │         ┌───────┴───────┐           │
                 └────────▶│  fact_sales   │◀──────────┘
                           │  transaction  │
                           │  quantity     │     ┌──────────────┐
                           │  revenue      │     │  fact_inven  │
                           │  discount     │     │  inventory   │
                           └───────┬───────┘     │  snapshot    │
                                   │             │  available   │
                                   │             │  reserved    │
                           ┌───────┴───────┐     └──────────────┘
                           │   dim_date    │
                           │  date (PK)    │     ┌──────────────────────┐
                           │  day_of_week  │     │  gold_daily_demand   │
                           │  week/month   │     │  product×store×date  │
                           │  holiday_flag │     │  total_quantity      │
                           └───────────────┘     │  total_revenue       │
                                                 └──────────────────────┘

           Analytical KPI Tables:
           ┌──────────────────────────┐   ┌────────────────────────────┐
           │  gold_inventory_health   │   │  gold_supplier_performance │
           │  product_id, store_id    │   │  supplier_id, period       │
           │  total_available         │   │  total_shipments           │
           │  stockout_risk (bool)    │   │  delayed_shipments         │
           │  reorder_recommendation  │   │  on_time_rate              │
           └──────────────────────────┘   │  average_delay_days        │
                                          └────────────────────────────┘
```

---

## 6. ML & MLOps Pipeline

```
Silver / Gold Data
        │
        ▼
┌──────────────────────────────────┐
│        FEATURE ENGINEERING       │
│  • Lag features (1d, 7d, 30d)   │
│  • Rolling mean / std            │
│  • Seasonality (DoW, month)      │
│  • Holiday / weather signals     │
│  • Price / discount features     │
│  • Inventory level features      │
└──────────────────┬───────────────┘
                   │
                   ▼  (temporal split — NO future leakage)
┌──────────────────────────────────┐
│         ML TRAINING              │
│  Grain: Product × Store × Date   │
│  Models: XGBoost / LightGBM      │
│  Evaluation: MAE, RMSE, MAPE     │
│  Tracking: MLflow                │
└──────────────────┬───────────────┘
                   │
                   ▼
┌──────────────────────────────────┐
│       MODEL REGISTRY             │
│  Staging ──▶ MAPE < threshold?   │
│            ──▶ Production        │
│  Versions tracked in MLflow      │
└──────────────────┬───────────────┘
                   │
          ┌────────┴──────────┐
          ▼                   ▼
   BATCH PREDICT        REAL-TIME SERVE
   (scheduled)          (REST endpoint)
          │                   │
          └────────┬──────────┘
                   ▼
┌──────────────────────────────────┐
│         MONITORING               │
│  • MAPE tracking over time       │
│  • Feature distribution drift    │
│  • Prediction distribution drift │
│  • Data quality score            │
└──────────────────┬───────────────┘
                   │  threshold breached?
                   ▼
           RETRAIN TRIGGER
                   │
                   ▼
           Back to training ↑
```

---

## 7. Project Structure

```
supply-chain-lakehouse/
│
├── src/
│   ├── data_generation/          # Synthetic data generator (Phase 1)
│   │   ├── generators/
│   │   │   ├── master_data.py    # Products, stores, suppliers, warehouses
│   │   │   └── transactional_data.py # Sales, inventory, shipments, returns
│   │   ├── quality_injector.py   # Injects realistic data quality issues
│   │   └── validator.py          # Validates generated data
│   │
│   ├── ingestion/                # Batch ingestion engine (Phase 2)
│   │   ├── schema_validator.py   # Schema + type validation
│   │   ├── contract_validator.py # Data contract enforcement
│   │   ├── idempotency.py        # Checksum-based dedup
│   │   ├── quarantine.py         # Invalid record isolation
│   │   ├── manifest.py           # Batch manifest tracking
│   │   └── audit.py              # Audit trail logging
│   │
│   └── lakehouse/
│       ├── bronze/               # Bronze layer (Phase 3)
│       │   ├── src/ingestion.py  # Raw → Delta write
│       │   └── tests/
│       │
│       ├── silver/               # Silver layer (Phase 6)
│       │   ├── src/
│       │   │   ├── cleaner.py    # Dedup, null handling, type casting
│       │   │   ├── validator.py  # Business rule validation
│       │   │   └── pipeline.py   # Silver orchestrator
│       │   └── tests/
│       │
│       └── gold/                 # Gold layer (Phase 7) ← current
│           ├── src/
│           │   ├── dimensions.py # dim_product, dim_store, dim_supplier
│           │   ├── facts.py      # fact_sales, fact_inventory, fact_shipments
│           │   ├── demand.py     # gold_daily_demand aggregation
│           │   ├── inventory.py  # gold_inventory_health (stockout risk)
│           │   ├── logistics.py  # gold_shipment_performance
│           │   ├── suppliers.py  # gold_supplier_performance
│           │   ├── schemas.py    # Gold contract definitions (primary keys, grain)
│           │   └── pipeline.py   # GoldPipeline — idempotent Delta MERGE
│           └── tests/
│               ├── conftest.py   # Local SparkSession fixture (Arrow-based)
│               ├── test_dimensions.py
│               ├── test_facts.py
│               ├── test_demand.py
│               ├── test_inventory.py
│               ├── test_logistics.py
│               ├── test_suppliers.py
│               ├── test_pipeline.py  # Idempotency + MERGE test
│               └── test_schemas.py   # Gold contract validation
│
├── infrastructure/
│   └── terraform/                # IaC for AWS (Phase 5)
│       ├── modules/
│       │   ├── data-lake/        # S3 buckets, lifecycle rules
│       │   ├── iam/              # Roles and policies
│       │   ├── databricks/       # Databricks workspace
│       │   └── budget/           # Cost alerting
│       └── environments/dev/     # Dev environment config
│
├── configs/
│   ├── datasets.yaml             # Dataset schemas and ingestion config
│   ├── ingestion.yaml            # Ingestion pipeline settings
│   └── data_generation.yaml     # Synthetic data parameters
│
├── docs/
│   ├── PROJECT_SPECIFICATION.md  # Full technical specification
│   ├── OVERVIEW.md               # Project overview
│   ├── IMPLEMENTATION_ROADMAP.md # Phase-by-phase roadmap
│   ├── architecture/             # Architecture documents
│   ├── data/                     # Data contracts and dictionary
│   ├── decisions/                # Architecture Decision Records (ADRs)
│   ├── ml/                       # ML specification
│   ├── mlops/                    # MLOps specification
│   └── phase-reports/            # Per-phase completion reports
│
├── tests/
│   ├── test_ingestion.py         # End-to-end ingestion tests
│   └── data/test_generation.py   # Data generation tests
│
├── manifests/ingestion/          # Batch manifests (idempotency)
├── reports/                      # Pipeline run metrics
├── notebooks/                    # Exploratory notebooks (Databricks)
├── pipelines/                    # Databricks job definitions
└── dashboards/                   # BI dashboard definitions
```

---

## 8. Implementation Phases

| Phase | Title | Status | Description |
|---|---|---|---|
| **1** | Synthetic Data Generation | ✅ Done | Generate 10 realistic datasets with clean + dirty variants |
| **2** | Batch Ingestion Engine | ✅ Done | Schema validation, idempotency, quarantine, audit trail |
| **3** | Bronze Layer | ✅ Done | Raw Delta tables with ingestion metadata |
| **4** | Data Quality Framework | ✅ Done | Data contracts, quality metrics, monitoring |
| **5** | AWS + Terraform Infrastructure | ✅ Done | S3 data lake, IAM, Databricks workspace via Terraform |
| **6** | Silver Layer | ✅ Done | Cleaning, deduplication, type casting, validation |
| **7** | Gold Layer | ✅ Done (local) | Dimensions, facts, KPI aggregations, Delta MERGE |
| **8** | ML Feature Engineering | 🔜 Next | Feature store: lags, rolling stats, seasonality |
| **9** | Demand Forecasting Model | 🔜 Planned | XGBoost/LightGBM, MLflow tracking, model registry |
| **10** | MLOps — Monitoring + Retraining | 🔜 Planned | Drift detection, automated retraining pipeline |

> **Note:** Phase 7 (Gold Layer) is **locally validated with 16/16 tests passing**. Cloud deployment on Databricks is pending AWS S3 activation.

---

## 9. Technology Stack

| Layer | Technology |
|---|---|
| **Cloud** | AWS (S3, IAM, Budgets) |
| **Compute** | Databricks (Spark 3.5 / Unity Catalog) |
| **Storage Format** | Delta Lake 3.1 |
| **Orchestration** | Databricks Workflows / scheduled jobs |
| **Infrastructure** | Terraform |
| **Language** | Python 3.12 |
| **ML Framework** | scikit-learn, XGBoost, LightGBM |
| **Experiment Tracking** | MLflow |
| **Data Validation** | Custom contract engine + Great Expectations (planned) |
| **CI/CD** | GitHub Actions |
| **Testing** | pytest + PySpark local mode |
| **BI** | Databricks SQL / dashboards |

---

## 10. Data Sources

The platform uses **10 logical datasets** (synthetic, generated with realistic quality issues):

| Dataset | Description | Key Fields |
|---|---|---|
| **Sales** | POS transactions | `transaction_id`, `product_id`, `store_id`, `quantity`, `total_amount` |
| **Products** | Product catalog | `product_id`, `category`, `brand`, `unit_cost`, `selling_price` |
| **Inventory** | Stock snapshots | `inventory_id`, `product_id`, `store_id`, `available_quantity`, `reorder_point` |
| **Stores** | Retail locations | `store_id`, `city`, `state`, `region`, `store_type` |
| **Warehouses** | Distribution centers | `warehouse_id`, `region`, `capacity`, `utilization` |
| **Suppliers** | Supplier info | `supplier_id`, `product_id`, `lead_time_days`, `reliability_score` |
| **Shipments** | Supplier → WH deliveries | `shipment_id`, `supplier_id`, `order_date`, `actual_delivery_date`, `delay_days` |
| **Returns** | Product returns | `return_id`, `transaction_id`, `reason`, `quantity` |
| **Weather** | External signals | `date`, `location`, `temperature`, `rainfall` |
| **Calendar** | Holiday/event flags | `date`, `holiday_flag`, `festival_flag`, `day_of_week` |

Data is generated with:
- **Clean variant** — for Silver/Gold processing
- **Dirty variant** — with injected nulls, duplicates, type errors (tests the validation pipeline)

---

## 11. Local Development Setup

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12 | |
| Java (JDK) | 17 | Required for PySpark local mode |
| Hadoop winutils | 3.3.x | Windows only — for Spark temp dir handling |
| Git | any | |

### 1. Clone the repo

```bash
git clone https://github.com/prince3235/supply-chain-lakehouse.git
cd supply-chain-lakehouse
```

### 2. Install dependencies

```bash
pip install pyspark==3.5.1 delta-spark==3.1.0 pandas pyarrow pytest
```

### 3. Set environment variables (Windows)

```powershell
$env:JAVA_HOME = "C:\jdk\jdk-17.0.10+7"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path
$env:HADOOP_HOME = "C:\hadoop"
$env:Path = "$env:HADOOP_HOME\bin;" + $env:Path
```

### 4. Generate synthetic data (optional)

```bash
python -m src.data_generation
```

---

## 12. Running Tests

### Gold Layer (Phase 7) — 16 tests

```powershell
$env:JAVA_HOME = "C:\jdk\jdk-17.0.10+7"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path
$env:PYTHONPATH = "src/lakehouse/gold"

pytest src\lakehouse\gold\tests -v
```

**Expected output:**
```
collected 16 items

src\lakehouse\gold\tests\test_demand.py .        [  6%]
src\lakehouse\gold\tests\test_dimensions.py ...  [ 25%]
src\lakehouse\gold\tests\test_facts.py ...       [ 43%]
src\lakehouse\gold\tests\test_inventory.py .     [ 50%]
src\lakehouse\gold\tests\test_logistics.py .     [ 56%]
src\lakehouse\gold\tests\test_pipeline.py .      [ 62%]
src\lakehouse\gold\tests\test_schemas.py .....   [ 93%]
src\lakehouse\gold\tests\test_suppliers.py .     [100%]

================= 16 passed in 96.42s ==================
```

### Silver Layer (Phase 6)

```powershell
$env:PYTHONPATH = "src/lakehouse/silver"
pytest src\lakehouse\silver\tests -v
```

### Ingestion Engine (Phase 2)

```bash
pytest tests/test_ingestion.py -v
```

---

## 13. Key Design Decisions

### Why Delta Lake?

Delta Lake provides ACID transactions, schema enforcement, time travel, and `MERGE` semantics — essential for idempotent pipelines that can be re-run safely without producing duplicates.

### Why MERGE for Gold writes?

```python
# Every Gold write is an upsert — safe to re-run
dt.alias("target").merge(
    df.alias("source"),
    "target.product_id = source.product_id AND target.demand_date = source.demand_date"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

This means pipelines can fail and be retried without duplicating data.

### Why Arrow for local testing?

`createDataFrame(pandas_df)` with Arrow enabled bypasses Python worker process spawning — which consistently crashes on Windows + Python 3.12 with PySpark 3.5.x due to socket binding issues.

### Why pyspark==3.5.1 + delta-spark==3.1.0?

PySpark 4.x introduced a breaking change in how Python workers communicate. The 3.5.1 + 3.1.0 combination is the most stable locally on Windows + Python 3.12.

### Temporal split for ML (no leakage)

```
Training data:   all records where date <= cutoff
Validation data: records where date > cutoff
Test data:       future records (hold-out)
```

Random splits are **not used** — using future data to predict the past is a form of data leakage that inflates model performance metrics.

---

## 14. Current Status

```
Phase 1  ████████████████████  ✅ DONE  — Synthetic data generation
Phase 2  ████████████████████  ✅ DONE  — Ingestion engine
Phase 3  ████████████████████  ✅ DONE  — Bronze layer
Phase 4  ████████████████████  ✅ DONE  — Data quality
Phase 5  ████████████████████  ✅ DONE  — AWS infrastructure (Terraform)
Phase 6  ████████████████████  ✅ DONE  — Silver layer
Phase 7  ████████████████████  ✅ DONE  — Gold layer (16/16 tests passing locally)
Phase 8  ░░░░░░░░░░░░░░░░░░░░  🔜 NEXT — ML feature engineering
Phase 9  ░░░░░░░░░░░░░░░░░░░░  🔜 PLAN — Demand forecasting model
Phase 10 ░░░░░░░░░░░░░░░░░░░░  🔜 PLAN — MLOps monitoring + retraining
```

> **Cloud deployment:** AWS S3 + Databricks runtime validation is **PENDING** (AWS account activation in progress). All local tests pass. Cloud validation will be added once infrastructure is available.

---

## Branches

| Branch | Purpose |
|---|---|
| `main` | Stable, reviewed code |
| `feature/phase-6-silver` | Silver layer implementation |
| `feature/phase-7-gold` | Gold layer implementation ← current |

---

## License

This project is for portfolio and educational purposes.

---

*Built by [prince3235](https://github.com/prince3235) — Supply Chain Lakehouse | Data Engineering + MLOps Portfolio Project*
