# ADR-001: Adopt AWS + Databricks Lakehouse Architecture

**Status:** Accepted

**Date:** 2026-08-16

---

## 1. Context

Supply Chain Lakehouse requires a scalable platform capable of supporting:

- Large-scale data processing
- Data Lake storage
- Data Warehouse analytics
- Machine Learning
- MLOps
- Governance
- Monitoring
- Future streaming workloads

The project is intended to demonstrate production-oriented Data Engineering, Cloud, Lakehouse, Machine Learning, and MLOps capabilities.

---

## 2. Decision

We will use:

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
MLflow
```

as the primary platform architecture.

---

## 3. Responsibilities

### AWS S3

Primary durable object-storage and data-lake foundation.

### Databricks

Primary data-processing and Lakehouse platform.

### Apache Spark

Distributed processing engine.

### Delta Lake

Reliable table/storage layer for Lakehouse datasets.

### Unity Catalog

Governance, access control, discovery, and lineage.

### Databricks SQL

Analytical SQL and warehouse-style workloads.

### MLflow

ML experiment tracking and model lifecycle management.

---

## 4. Why AWS?

AWS provides:

* Mature cloud infrastructure.
* S3 object storage.
* IAM security.
* Broad ecosystem.
* Strong industry adoption.
* Integration opportunities with streaming and monitoring services.

---

## 5. Why Databricks?

Databricks provides:

* Apache Spark integration.
* Lakehouse architecture.
* Delta Lake.
* SQL analytics.
* MLflow integration.
* Model lifecycle capabilities.
* Data and ML governance.
* Unified data engineering and ML workflows.

---

## 6. Alternatives Considered

### Azure + Databricks

Advantages:

* Strong Databricks integration.
* Azure ecosystem.
* Power BI integration.

Reason not selected:

The project will use AWS to strengthen AWS cloud and S3 data-lake skills.

---

### AWS Native Only

Possible architecture:

```text
S3
Glue
Athena
Redshift
SageMaker
```

Reason not selected:

The project specifically aims to develop strong Databricks Lakehouse skills in addition to AWS cloud skills.

---

## 7. Consequences

### Positive

* Strong Data Engineering experience.
* Strong Lakehouse experience.
* Strong Cloud experience.
* Unified analytics and ML platform.
* Industry-relevant MLOps workflow.
* Strong portfolio value.

### Negative

* Multiple technologies increase learning complexity.
* Cloud resources may incur costs.
* Databricks configuration requires careful management.

---

## 8. Cost Mitigation

We will:

* Use small development compute.
* Avoid always-on clusters.
* Monitor cloud spending.
* Stop unused resources.
* Use development-sized datasets initially.
* Scale only when required.

---

## 9. Decision Outcome

AWS + Databricks is the selected architecture for Supply Chain Lakehouse.

This decision should be revisited only if project requirements materially change.

---

## 10. Status

**Accepted**
