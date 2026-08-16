# Supply Chain Lakehouse — ML Specification

> Defines the machine-learning objectives, datasets, features, evaluation, training, and prediction strategy.

---

## 1. ML Objectives

The platform will initially implement two ML capabilities:

### Primary

Demand Forecasting

### Secondary

Supply Chain Anomaly Detection

---

## 2. Demand Forecasting Problem

Predict future demand for each:

```text
Product × Store × Date
```

Forecast horizons:

```text
7 Days
14 Days
30 Days
```

---

## 3. Target Variable

Primary target:

```text
daily_demand
```

Calculated from historical sales transactions.

---

## 4. Feature Groups

### Historical

```text
sales_last_1_day
sales_last_7_days
sales_last_14_days
sales_last_30_days
rolling_mean_7
rolling_mean_14
rolling_mean_30
rolling_std_7
rolling_std_30
```

### Temporal

```text
day_of_week
week_of_year
month
quarter
weekend_flag
holiday_flag
festival_flag
```

### Pricing

```text
unit_price
discount_amount
discount_percentage
price_change
```

### Inventory

```text
current_inventory
reserved_inventory
reorder_point
safety_stock
stockout_days
inventory_turnover
```

### Supplier

```text
lead_time_days
reliability_score
historical_delay_rate
```

### Weather

```text
temperature_avg
temperature_max
temperature_min
rainfall_mm
humidity
```

---

## 5. Feature Engineering Principles

Features must:

* Be reproducible.
* Avoid future information leakage.
* Respect forecasting time boundaries.
* Have documented definitions.
* Be validated before training.

---

## 6. Data Leakage Prevention

The model must never use information that would not have been available at prediction time.

Example:

```text
Prediction Date = D

Allowed:
Data <= D

Not Allowed:
Data > D
```

This is a critical requirement.

---

## 7. Training Dataset

Training dataset structure:

```text
product_id
store_id
date

historical_features...
pricing_features...
inventory_features...
supplier_features...
weather_features...
calendar_features...

daily_demand
```

---

## 8. Model Candidates

Initial candidates:

```text
Baseline
Random Forest
XGBoost
LightGBM
Statistical Forecasting Baseline
```

Additional models may be evaluated only when justified.

---

## 9. Baseline

A simple baseline must be established before advanced models.

Potential baselines:

```text
Previous Day Demand
7-Day Moving Average
```

Advanced models must demonstrate measurable improvement over the baseline.

---

## 10. Evaluation Metrics

Primary:

```text
MAE
RMSE
MAPE
```

Additional:

```text
Forecast Bias
Weighted Error
Segment-Level Error
```

Final metric selection will depend on the dataset characteristics.

---

## 11. Model Validation

Validation must respect temporal ordering.

Preferred strategy:

```text
Historical Data
      ↓
Train
      ↓
Validation
      ↓
Future Holdout
```

Random train/test splitting should not be used blindly for time-dependent forecasting.

---

## 12. Experiment Tracking

MLflow should record:

```text
Experiment ID
Run ID
Model Type
Hyperparameters
Feature Version
Dataset Version
Metrics
Artifacts
Code Version
Training Timestamp
```

---

## 13. Model Selection

Candidate models will be evaluated based on:

1. Forecast accuracy
2. Stability
3. Generalization
4. Training cost
5. Inference cost
6. Business usefulness

---

## 14. Model Registry

Models will move through:

```text
Candidate
   ↓
Validation
   ↓
Staging
   ↓
Production
```

Every production model must have:

```text
Version
Metrics
Training Dataset
Feature Definition
Code Version
Approval Status
```

---

## 15. Batch Inference

Daily batch workflow:

```text
Gold Data
   ↓
Feature Generation
   ↓
Load Production Model
   ↓
Prediction
   ↓
Forecast Table
   ↓
Dashboard / Optimization
```

---

## 16. Real-Time Inference

Real-time prediction will be supported where a business use case justifies low-latency predictions.

The initial project may prioritize batch forecasting because demand planning is naturally batch-oriented.

---

## 17. Anomaly Detection

Potential anomaly areas:

```text
Demand Spikes
Demand Drops
Inventory Anomalies
Supplier Delays
Shipment Delays
Return Anomalies
```

The anomaly layer should provide:

```text
entity
timestamp
anomaly_score
severity
reason
```

---

## 18. Model Explainability

Where practical, model predictions should provide interpretable signals.

Potential techniques:

```text
Feature Importance
SHAP
Error Analysis
```

Explainability should be added only where it provides meaningful business value.

---

## 19. ML Success Criteria

The ML system must:

* Beat the selected baseline.
* Maintain reproducibility.
* Pass defined validation thresholds.
* Track all production model versions.
* Detect meaningful degradation.
* Support retraining.

---

## 20. Version

**Version:** 1.0.0

**Status:** Initial Design
