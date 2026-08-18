# Supply Chain Lakehouse — Project Overview

> An end-to-end AWS + Databricks Lakehouse and MLOps platform for transforming fragmented supply-chain data into reliable analytics, demand forecasts, inventory intelligence, and continuously improving machine-learning systems.

---

# 1. What Is Supply Chain Lakehouse?

Supply Chain Lakehouse is an industry-oriented Data Engineering, Cloud, Lakehouse, Machine Learning, and MLOps platform designed to solve real-world supply-chain intelligence problems.

The platform brings together data from multiple supply-chain domains such as:

- Sales
- Products
- Inventory
- Stores
- Warehouses
- Suppliers
- Shipments
- Returns
- Weather
- Calendar and seasonal information

Instead of keeping these datasets isolated, the platform creates a unified data ecosystem using:

```text
AWS
 +
Amazon S3
 +
Databricks
 +
Delta Lake
 +
Unity Catalog
 +
Databricks SQL
 +
MLflow
 +
MLOps
 +
Business Intelligence
```

The ultimate goal is not simply to train an ML model.

The goal is to build a complete production-oriented platform that can:

```text
INGEST
   ↓
STORE
   ↓
VALIDATE
   ↓
TRANSFORM
   ↓
ANALYZE
   ↓
FEATURE ENGINEER
   ↓
TRAIN
   ↓
REGISTER
   ↓
DEPLOY
   ↓
PREDICT
   ↓
MONITOR
   ↓
DETECT DRIFT
   ↓
RETRAIN
   ↓
VALIDATE
   ↓
IMPROVE
```

---

# 2. Why This Project Exists

Modern supply-chain organizations generate huge amounts of data across different operational systems.

For example:
- POS Systems
- ERP Systems
- Inventory Systems
- Warehouse Systems
- Supplier Systems
- Logistics Systems
- External APIs

However, these systems often produce fragmented data.

This creates problems such as:
- Poor visibility into supply-chain operations.
- Difficulty combining data from different systems.
- Slow analytical workflows.
- Inconsistent business metrics.
- Poor demand forecasting.
- Stockouts.
- Overstocking.
- Supplier delays.
- Shipment anomalies.
- Difficulty monitoring ML models in production.
- Manual model retraining.
- Lack of centralized governance and lineage.

Supply Chain Lakehouse addresses these problems by creating a unified cloud-native data and ML platform.

---

# 3. Core Business Problem

The primary business problem can be summarized as:

> How can we transform fragmented supply-chain data into a scalable, reliable, governed, and continuously improving intelligence platform that helps organizations understand demand, optimize inventory, identify operational risks, and make better decisions?

---

# 4. Main Business Objectives

The platform focuses on several major objectives.

## 4.1 Demand Forecasting

Predict future product demand at:

`Product × Store × Date`

Forecast horizons:
- 7 Days
- 14 Days
- 30 Days

---

## 4.2 Inventory Intelligence

Identify:
- Stockout risks
- Overstock risks
- Low inventory
- Excess inventory
- Reorder opportunities

The system can combine predicted demand with current inventory to generate inventory recommendations.

Conceptually:

```text
Forecasted Demand
        +
Safety Stock
        -
Current Inventory
        =
Recommended Reorder Quantity
```

---

## 4.3 Supply Chain Visibility

Provide a unified view of:
- Sales
- Products
- Inventory
- Stores
- Warehouses
- Suppliers
- Shipments
- Returns

---

## 4.4 Anomaly Detection

Identify abnormal behavior such as:
- Demand spikes
- Demand drops
- Inventory anomalies
- Supplier delays
- Shipment delays
- Unusual return behavior

---

## 4.5 Data Reliability

Automatically monitor:
- Schema validity
- Missing values
- Duplicate records
- Invalid values
- Referential integrity
- Data freshness
- Data volume

---

## 4.6 Production ML Reliability

Monitor deployed models for:
- Data drift
- Feature drift
- Model performance degradation
- Prediction distribution changes
- Inference failures

---

## 4.7 Automated ML Lifecycle

Reduce manual ML operations through:
- Experiment tracking
- Model versioning
- Model validation
- Model deployment
- Monitoring
- Drift detection
- Automated retraining
- Champion/challenger comparison

---

# 5. High-Level System Architecture

The complete platform follows this architecture:

```text
                         ┌─────────────────────┐
                         │     DATA SOURCES    │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
               Sales            Inventory          Suppliers
               Stores           Products            Shipments
               Returns          Warehouse           External APIs
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   INGESTION LAYER   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      AWS S3         │
                         │    DATA LAKE        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     DATABRICKS      │
                         │      LAKEHOUSE      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
                 BRONZE          SILVER           GOLD
                    │               │               │
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             DATA WAREHOUSE                    ML FEATURES
                    │                               │
                    ▼                               ▼
               BI / SQL                       ML TRAINING
                                                    │
                                                    ▼
                                                  MLflow
                                                    │
                                                    ▼
                                             MODEL REGISTRY
                                                    │
                                                    ▼
                                            MODEL DEPLOYMENT
                                                    │
                                      ┌─────────────┴─────────────┐
                                      │                           │
                                      ▼                           ▼
                                BATCH PREDICTION          REAL-TIME SERVING
                                      │                           │
                                      └─────────────┬─────────────┘
                                                    │
                                                    ▼
                                             PREDICTIONS
                                                    │
                                                    ▼
                                              MONITORING
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              │                     │                     │
                              ▼                     ▼                     ▼
                         Data Quality          Data Drift          Model Performance
                              │                     │                     │
                              └─────────────────────┼─────────────────────┘
                                                    │
                                                    ▼
                                           RETRAINING TRIGGER
                                                    │
                                                    ▼
                                             NEW ML TRAINING
                                                    │
                                                    ▼
                                            MODEL VALIDATION
                                                    │
                                                    ▼
                                           CHAMPION / CHALLENGER
                                                    │
                                                    ▼
                                             PRODUCTION MODEL
```

---

# 6. End-to-End Workflow

The complete system lifecycle is:

```text
1. Data Sources
       ↓
2. Data Ingestion
       ↓
3. AWS S3 Data Lake
       ↓
4. Bronze Layer
       ↓
5. Data Validation
       ↓
6. Silver Layer
       ↓
7. Business Transformations
       ↓
8. Gold Layer
       ↓
9. Data Warehouse
       ↓
10. Business Intelligence
       ↓
11. Feature Engineering
       ↓
12. ML Training
       ↓
13. MLflow Experiment Tracking
       ↓
14. Model Validation
       ↓
15. Model Registry
       ↓
16. Model Deployment
       ↓
17. Batch / Real-Time Predictions
       ↓
18. Monitoring
       ↓
19. Drift Detection
       ↓
20. Automated Retraining
       ↓
21. Model Revalidation
       ↓
22. Production Promotion
```

---

# 7. Data Sources

The initial platform contains ten logical datasets.

1. Sales
2. Products
3. Inventory
4. Stores
5. Warehouses
6. Suppliers
7. Shipments
8. Returns
9. Weather
10. Calendar

---

# 8. Core Data Model

The major entities are:
- Product
- Store
- Warehouse
- Supplier
- Sales
- Inventory
- Shipment
- Return
- Weather
- Calendar

Logical relationships:

```text
                         PRODUCT
                            |
              +-------------+-------------+
              |             |             |
              ▼             ▼             ▼
            SALES       INVENTORY      SUPPLIER
              |             |             |
              ▼             ▼             ▼
           RETURNS      WAREHOUSE      SHIPMENT
              |
            STORE
              |
           CALENDAR

WEATHER
   |
   └──── STORE / LOCATION
```

---

# 9. Forecasting Data Grain

The primary ML grain is:

`Product × Store × Date`

For example:
- Product: P1001
- Store:   S001
- Date:    2026-08-16
- Demand:  127

Raw transaction data is aggregated into this grain before forecasting.

```text
Raw Transactions
       ↓
Transaction Lines
       ↓
Product × Store × Date
       ↓
Daily Demand
```

This dataset becomes the foundation of the demand forecasting system.

---

# 10. Lakehouse Architecture

The Lakehouse follows the Medallion Architecture.

```text
              ┌─────────────┐
              │   BRONZE    │
              │ Raw Data    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   SILVER    │
              │ Clean Data  │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │    GOLD     │
              │ Business    │
              │ Ready Data  │
              └──────┬──────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     Data Warehouse        ML Features
```

---

# 11. Bronze Layer

The Bronze layer stores raw source data.

Responsibilities:
- Raw ingestion
- Source preservation
- Ingestion metadata
- Batch identification
- Schema capture
- Reprocessing support

Example tables:
- `bronze_sales`
- `bronze_products`
- `bronze_inventory`
- `bronze_stores`
- `bronze_warehouses`
- `bronze_suppliers`
- `bronze_shipments`
- `bronze_returns`
- `bronze_weather`
- `bronze_calendar`

The Bronze layer should remain as close to the source representation as practical.

---

# 12. Silver Layer

The Silver layer contains cleaned and validated data.

Typical operations:

```text
Schema Validation
      ↓
Type Casting
      ↓
Deduplication
      ↓
Null Handling
      ↓
Standardization
      ↓
Business Validation
      ↓
Referential Integrity
```

Example tables:
- `silver_sales`
- `silver_products`
- `silver_inventory`
- `silver_stores`
- `silver_warehouses`
- `silver_suppliers`
- `silver_shipments`
- `silver_returns`
- `silver_weather`
- `silver_calendar`

---

# 13. Gold Layer

The Gold layer contains business-ready datasets.

Examples:
- `gold_daily_sales`
- `gold_product_demand`
- `gold_inventory_health`
- `gold_supplier_performance`
- `gold_shipment_performance`
- `gold_store_performance`
- `gold_supply_chain_metrics`

Gold is consumed by:
- BI
- Analytics
- ML
- Business Applications

---

# 14. Data Warehouse

The analytical warehouse follows a star-schema-oriented design.

**Fact Tables**
- `fact_sales`
- `fact_inventory`
- `fact_shipments`
- `fact_returns`

**Dimension Tables**
- `dim_product`
- `dim_store`
- `dim_warehouse`
- `dim_supplier`
- `dim_customer`
- `dim_date`

Example:

```text
                  dim_product
                         |
                         |
dim_store ─────── fact_sales ─────── dim_customer
                         |
                         |
                     dim_date
```

This layer supports analytical workloads such as:
- Revenue analysis
- Product performance
- Store performance
- Inventory analysis
- Supplier performance
- Shipment analysis
- Forecast analysis

---

# 15. Data Quality

Data quality is a first-class component of the platform.

The system checks:

**Completeness**
- Required fields
- Null rates
- Missing partitions

**Uniqueness**
- Primary keys
- Duplicate records

**Validity**
- Numeric ranges
- Dates
- Categorical values

**Referential Integrity**
Examples:
- `sales.product_id → products.product_id`
- `sales.store_id → stores.store_id`
- `inventory.product_id → products.product_id`
- `shipments.supplier_id → suppliers.supplier_id`
- `shipments.product_id → products.product_id`
- `shipments.warehouse_id → warehouses.warehouse_id`

**Freshness**
- The platform monitors whether datasets arrive within their expected SLA.

---

# 16. Invalid Data Handling

Invalid data should never silently disappear.

The expected flow is:

```text
Raw Record
     ↓
Validation
     ↓
   ┌───────┐
   │ Valid │──────────→ Normal Pipeline
   └───────┘

   ┌─────────┐
   │ Invalid │────────→ Quarantine
   └─────────┘              │
                            ▼
                       Error Logging
                            │
                            ▼
                          Alert
```

Quarantined records should retain enough metadata for debugging and investigation.

---

# 17. Machine Learning Architecture

The primary ML problem is:
> Forecast future product demand at the Product × Store × Date level.

The secondary ML problem is:
> Detect abnormal supply-chain behavior.

---

# 18. Feature Engineering

Features are generated from the curated data.

**Historical Demand**
- `sales_last_1_day`
- `sales_last_7_days`
- `sales_last_14_days`
- `sales_last_30_days`
- `rolling_mean_7`
- `rolling_mean_14`
- `rolling_mean_30`
- `rolling_std_7`
- `rolling_std_30`

**Temporal**
- `day_of_week`
- `week_of_year`
- `month`
- `quarter`
- `weekend_flag`
- `holiday_flag`
- `festival_flag`

**Pricing**
- `unit_price`
- `discount_amount`
- `discount_percentage`
- `price_change`

**Inventory**
- `current_inventory`
- `reserved_inventory`
- `reorder_point`
- `safety_stock`
- `stockout_days`
- `inventory_turnover`

**Supplier**
- `lead_time_days`
- `reliability_score`
- `historical_delay_rate`

**Weather**
- `temperature_avg`
- `temperature_max`
- `temperature_min`
- `rainfall_mm`
- `humidity`

---

# 19. ML Data Leakage Prevention

Because this is a time-dependent forecasting problem, future information must never be used to predict the past.

For prediction date D:

**Allowed:**
- Data <= D

**Not allowed:**
- Data > D

Temporal validation must therefore be used instead of blindly applying random train/test splits.

---

# 20. ML Training Strategy

The platform will establish a baseline before using advanced models.

Potential baseline:
- Previous Day Demand
- 7-Day Moving Average

Candidate models may include:
- Random Forest
- XGBoost
- LightGBM
- Statistical Forecasting Baselines

The final model should be selected based on:
- Accuracy
- Stability
- Generalization
- Training cost
- Inference cost
- Business usefulness

---

# 21. ML Evaluation

Primary metrics:
- MAE
- RMSE
- MAPE

Additional metrics may include:
- Forecast Bias
- Weighted Error
- Segment-Level Error

The model must demonstrate measurable improvement over the selected baseline.

---

# 22. MLflow

MLflow provides experiment tracking and model lifecycle management.

Each experiment should capture:
- Experiment ID
- Run ID
- Model Type
- Hyperparameters
- Dataset Version
- Feature Version
- Metrics
- Artifacts
- Code Version
- Training Timestamp

---

# 23. Model Registry

Models move through controlled lifecycle stages:

```text
Candidate
    ↓
Validation
    ↓
Staging
    ↓
Production
```

Each production model should have:
- Model Version
- Training Dataset
- Feature Version
- Metrics
- Code Version
- Approval Status

---

# 24. Model Serving

The platform supports two prediction patterns.

**Batch**
```text
Gold Data
    ↓
Feature Generation
    ↓
Production Model
    ↓
Predictions
    ↓
Forecast Table
    ↓
Dashboard / Optimization
```

**Real-Time**
Where required, a model can be exposed through a serving endpoint.

The initial focus is batch demand forecasting because supply-chain demand planning is naturally batch-oriented.

---

# 25. Inventory Intelligence

Forecasting is combined with inventory information.

Conceptually:

```text
Predicted Demand
       +
Safety Stock
       -
Current Inventory
       =
Reorder Recommendation
```

Potential outputs:
- Stockout Risk
- Overstock Risk
- Recommended Reorder Quantity
- Recommended Reorder Timing

The initial system provides recommendations rather than automatically executing procurement.

---

# 26. Anomaly Detection

The anomaly detection layer can identify:
- Demand Spikes
- Demand Drops
- Inventory Anomalies
- Supplier Delays
- Shipment Delays
- Return Anomalies

Each anomaly can contain:
- Entity
- Timestamp
- Anomaly Score
- Severity
- Reason

---

# 27. MLOps Lifecycle

The production ML lifecycle is:

```text
Data
 ↓
Feature Engineering
 ↓
Training
 ↓
Experiment Tracking
 ↓
Validation
 ↓
Model Registry
 ↓
Staging
 ↓
Production
 ↓
Monitoring
 ↓
Drift Detection
 ↓
Retraining
 ↓
Validation
 ↓
Promotion
```

---

# 28. Monitoring

The platform monitors three major areas.

**Data Monitoring**
- Null Rate
- Duplicate Rate
- Schema Changes
- Freshness
- Invalid Records
- Record Counts

**Drift Monitoring**
- Feature Distribution
- PSI
- KS Test
- Category Distribution

**Model Monitoring**
- MAE
- RMSE
- MAPE
- Forecast Bias
- Prediction Distribution

**System Monitoring**
- Latency
- Error Rate
- Job Duration
- Throughput
- Resource Usage

---

# 29. Drift Detection

Drift does not automatically mean that the production model should be replaced.

The process is:

```text
Drift Detected
      ↓
Evaluate Severity
      ↓
Check Model Performance
      ↓
Determine Action
```

Possible actions:
- No Action
- Alert
- Investigate
- Retrain

---

# 30. Automated Retraining

One of the most important MLOps capabilities is the closed-loop retraining system.

```text
               PRODUCTION MODEL
                        │
                        ▼
                   MONITORING
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
         Data Drift          Performance Drop
             │                     │
             └──────────┬──────────┘
                        ▼
                 RETRAINING TRIGGER
                        │
                        ▼
                 TRAIN NEW MODEL
                        │
                        ▼
                     MLflow
                        │
                        ▼
                   VALIDATION
```


