# Supply Chain Lakehouse — Data Model

> Defines the logical relationships, entities, grains, and analytical model used across the Supply Chain Lakehouse.

---

## 1. Data Model Overview

The platform uses a hybrid analytical architecture:

```text
Operational Data
      ↓
Lakehouse
      ↓
Curated Gold Data
      ↓
Analytical Warehouse
      ↓
ML Feature Layer
```

---

## 2. Core Entities

```text
Product
Store
Warehouse
Supplier
Sales
Inventory
Shipment
Return
Weather
Calendar
```

---

## 3. Entity Relationship Model

```text
                         PRODUCT
                            |
              +-------------+-------------+
              |             |             |
              ↓             ↓             ↓
            SALES       INVENTORY      SUPPLIER
              |             |             |
              ↓             ↓             ↓
           RETURNS      WAREHOUSE      SHIPMENT
              |
            STORE
              |
           CALENDAR

WEATHER
   |
   +---- STORE / LOCATION
```

---

## 4. Entity Definitions

### Product

Master entity representing products sold by the organization.

**Grain:**

```text
One row per product
```

**Primary Key:**

```text
product_id
```

---

### Store

Represents a physical retail location.

**Grain:**

```text
One row per store
```

**Primary Key:**

```text
store_id
```

---

### Warehouse

Represents a distribution/storage facility.

**Grain:**

```text
One row per warehouse
```

**Primary Key:**

```text
warehouse_id
```

---

### Supplier

Represents a supplier-product relationship.

**Grain:**

```text
Supplier × Product
```

---

### Sales

Represents individual sales transaction lines.

**Grain:**

```text
Transaction Line
```

---

### Inventory

Represents inventory snapshots.

**Grain:**

```text
Product × Location × Timestamp
```

---

### Shipment

Represents supplier-to-warehouse shipment events.

**Grain:**

```text
One row per shipment
```

---

### Returns

Represents product return events.

**Grain:**

```text
One row per return event
```

---

# 5. Core Forecasting Grain

The primary demand forecasting grain is:

```text
Product × Store × Date
```

Example:

```text
P1001
S001
2026-08-16
```

Target:

```text
daily_demand
```

---

# 6. Demand Aggregation

Raw sales:

```text
Transaction
   ↓
Transaction Line
   ↓
Product × Store × Date
```

Example:

```text
100 transactions
       ↓
Product P1001
Store S001
Date 2026-08-16
       ↓
Daily Demand = 127
```

This aggregated dataset becomes the foundation for demand forecasting.

---

# 7. Warehouse Model

## Fact Tables

```text
fact_sales
fact_inventory
fact_shipments
fact_returns
```

## Dimensions

```text
dim_product
dim_store
dim_warehouse
dim_supplier
dim_customer
dim_date
```

---

# 8. Fact Sales

**Grain:**

```text
One sales transaction line
```

**Measures:**

```text
quantity
unit_price
discount_amount
total_amount
```

**Dimensions:**

```text
product
store
customer
date
```

---

# 9. Fact Inventory

**Grain:**

```text
Product × Location × Snapshot
```

**Measures:**

```text
available_quantity
reserved_quantity
inventory_value
```

**Dimensions:**

```text
product
store
warehouse
date
```

---

# 10. Fact Shipments

**Grain:**

```text
One shipment
```

**Measures:**

```text
quantity
delay_days
```

**Dimensions:**

```text
supplier
product
warehouse
date
```

---

# 11. Fact Returns

**Grain:**

```text
One return event
```

**Measures:**

```text
quantity
```

**Dimensions:**

```text
product
store
date
```

---

# 12. Dimension Strategy

Initial dimensions will use a simple overwrite strategy where historical attribute tracking is not required.

Future implementation may introduce Slowly Changing Dimensions where business history requires it.

---

# 13. Gold Analytical Model

Important Gold datasets:

```text
gold_daily_sales
gold_product_demand
gold_inventory_health
gold_supplier_performance
gold_shipment_performance
gold_store_performance
gold_supply_chain_metrics
```

---

# 14. ML Feature Model

Feature dataset grain:

```text
Product × Store × Date
```

Feature groups:

```text
Historical Demand
Temporal
Pricing
Inventory
Supplier
Weather
Calendar
```

---

# 15. Data Model Principles

1. Every dataset must have a clearly defined grain.
2. Fact tables contain measurable business events.
3. Dimensions provide descriptive context.
4. Raw data remains separate from analytical data.
5. Gold datasets should be business-oriented.
6. ML datasets should be reproducible.
7. Relationships should be explicit.
8. Duplicate business logic should be avoided.

---

# 16. Version

**Version:** 1.0.0

**Status:** Initial Design
