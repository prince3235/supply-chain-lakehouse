# Supply Chain Lakehouse — Data Contract

> Defines the operational contract between data producers, ingestion pipelines, Lakehouse layers, and downstream consumers.

---

## 1. Purpose

The Data Contract defines the expected structure, quality, freshness, ownership, and evolution rules for datasets entering and moving through the Supply Chain Lakehouse.

The contract ensures that downstream pipelines do not silently break when upstream data changes.

---

## 2. Contract Principles

1. Every dataset must have a defined schema.
2. Every dataset must have a clearly defined grain.
3. Required fields must be explicitly identified.
4. Primary keys must be defined.
5. Foreign-key relationships must be documented.
6. Data freshness expectations must be defined.
7. Data-quality rules must be automated where practical.
8. Schema changes must be detected.
9. Breaking changes require explicit approval.
10. Invalid records must be isolated rather than silently discarded.
11. Dataset ownership must be documented.
12. Dataset versions must be traceable.

---

## 3. Dataset Contract Lifecycle

```text
Source
  ↓
Schema Definition
  ↓
Schema Validation
  ↓
Ingestion
  ↓
Quality Validation
  ↓
Bronze
  ↓
Transformation
  ↓
Silver
  ↓
Business Validation
  ↓
Gold
  ↓
Downstream Consumers
```

---

## 4. Dataset Contract

Every production dataset must define:

```text
Dataset Name
Purpose
Owner
Source System
Schema Version
Grain
Primary Key
Foreign Keys
Required Fields
Nullable Fields
Expected Volume
Freshness SLA
Quality Rules
Retention
Schema Evolution Policy
```

---

## 5. Dataset Ownership

| Dataset    | Logical Owner         | Criticality |
| ---------- | --------------------- | ----------- |
| Sales      | Sales Data Domain     | Critical    |
| Products   | Product Data Domain   | High        |
| Inventory  | Inventory Data Domain | Critical    |
| Stores     | Store Data Domain     | High        |
| Warehouses | Warehouse Data Domain | High        |
| Suppliers  | Supplier Data Domain  | High        |
| Shipments  | Logistics Data Domain | Critical    |
| Returns    | Sales Operations      | Medium      |
| Weather    | External Data Domain  | Medium      |
| Calendar   | Analytics Data Domain | Low         |

Ownership is logical for this project and may be mapped to actual teams in a production organization.

---

## 6. Freshness Expectations

| Dataset    | Expected Freshness      |
| ---------- | ----------------------- |
| Sales      | Daily / Streaming-ready |
| Inventory  | Hourly / Daily          |
| Shipments  | Daily                   |
| Suppliers  | Daily / Weekly          |
| Products   | Daily                   |
| Stores     | Daily / Weekly          |
| Warehouses | Daily                   |
| Returns    | Daily                   |
| Weather    | Daily                   |
| Calendar   | Static / Periodic       |

The pipeline must expose freshness status for each dataset.

---

## 7. Data Quality Contract

### Completeness

Required fields must not exceed configured null thresholds.

Example:

```text
Critical field null rate <= 0.5%
```

Thresholds may vary by dataset.

### Uniqueness

Primary keys must be unique where the dataset grain requires uniqueness.

### Validity

Values must conform to defined ranges and formats.

Examples:

```text
quantity > 0
price >= 0
lead_time >= 0
reliability_score BETWEEN 0 AND 1
```

### Referential Integrity

Examples:

```text
sales.product_id → products.product_id

sales.store_id → stores.store_id

inventory.product_id → products.product_id

shipments.supplier_id → suppliers.supplier_id

shipments.product_id → products.product_id

shipments.warehouse_id → warehouses.warehouse_id
```

---

## 8. Quality Severity

| Severity | Meaning                         | Action            |
| -------- | ------------------------------- | ----------------- |
| CRITICAL | Pipeline cannot safely continue | Stop pipeline     |
| HIGH     | Significant data corruption     | Quarantine / Fail |
| MEDIUM   | Quality degradation             | Continue + Alert  |
| LOW      | Non-critical issue              | Log               |

---

## 9. Invalid Data Handling

Invalid records should not be silently dropped.

Recommended flow:

```text
Raw Record
   ↓
Validation
   ↓
Valid ─────────→ Normal Pipeline
   |
   └── Invalid ─→ Quarantine
                    ↓
                 Error Log
                    ↓
                   Alert
```

Quarantine records should retain enough metadata for investigation.

---

## 10. Schema Evolution

Schema changes are classified as:

### Non-Breaking

Examples:

* Adding an optional field.
* Adding metadata.
* Adding a new category.

These may be accepted automatically after validation.

### Breaking

Examples:

* Removing a required field.
* Renaming a required field.
* Changing a data type incompatibly.
* Changing dataset grain.

Breaking changes require explicit review.

---

## 11. Schema Versioning

Datasets should maintain schema versions.

Example:

```text
sales_schema_v1
sales_schema_v2
sales_schema_v3
```

The pipeline should record:

```text
schema_version
pipeline_run_id
batch_id
ingestion_timestamp
```

---

## 12. Data Freshness Failure

If a dataset exceeds its freshness SLA:

```text
Freshness Check
      ↓
SLA Violated
      ↓
Pipeline Warning
      ↓
Alert
      ↓
Downstream Impact Evaluation
```

Critical datasets may block downstream processing.

---

## 13. Contract Validation

Every ingestion pipeline should validate:

```text
Schema
+
Required Fields
+
Types
+
Keys
+
Ranges
+
Freshness
+
Referential Integrity
```

before promoting data to the next layer.

---

## 14. Contract Version

**Version:** 1.0.0

**Status:** Initial Design