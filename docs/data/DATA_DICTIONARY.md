# Supply Chain Lakehouse — Data Dictionary

> Canonical definition of datasets, schemas, relationships, grains, data types,
> quality rules, and business meaning used across the Supply Chain Lakehouse.

---

# 1. Data Architecture

The platform will initially use the following logical datasets:

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

The core analytical grain for demand forecasting is:

**Product × Store × Date**

---

# 2. Dataset Classification

| Dataset | Layer | Type | Primary Purpose |
|---|---|---|---|
| Sales | Bronze/Silver/Gold | Transaction | Demand and revenue |
| Products | Bronze/Silver/Gold | Master | Product attributes |
| Inventory | Bronze/Silver/Gold | Snapshot | Stock monitoring |
| Stores | Bronze/Silver/Gold | Master | Store attributes |
| Warehouses | Bronze/Silver/Gold | Master | Warehouse capacity |
| Suppliers | Bronze/Silver/Gold | Master | Supplier performance |
| Shipments | Bronze/Silver/Gold | Transaction | Logistics tracking |
| Returns | Bronze/Silver/Gold | Transaction | Return analysis |
| Weather | Bronze/Silver/Gold | External | Demand signals |
| Calendar | Bronze/Silver/Gold | Reference | Seasonality |

---

# 3. Sales Dataset

## Purpose

Stores individual sales transactions and serves as the primary historical
signal for demand forecasting and revenue analytics.

## Grain

One row represents one sales transaction line.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| transaction_id | STRING | PK | NO | Unique transaction identifier |
| transaction_timestamp | TIMESTAMP | - | NO | Transaction timestamp |
| product_id | STRING | FK | NO | Product identifier |
| store_id | STRING | FK | NO | Store identifier |
| customer_id | STRING | FK | YES | Customer identifier |
| quantity | INTEGER | - | NO | Quantity purchased |
| unit_price | DECIMAL(12,2) | - | NO | Unit selling price |
| discount_amount | DECIMAL(12,2) | - | YES | Discount applied |
| total_amount | DECIMAL(14,2) | - | NO | Final transaction amount |
| payment_method | STRING | - | YES | Payment method |
| ingestion_timestamp | TIMESTAMP | - | NO | Pipeline ingestion time |
| source_system | STRING | - | NO | Source system |
| batch_id | STRING | - | NO | Ingestion batch identifier |

## Quality Rules

- `transaction_id` must be unique.
- `product_id` must exist in `products`.
- `store_id` must exist in `stores`.
- `quantity > 0`.
- `unit_price >= 0`.
- `total_amount >= 0`.
- `transaction_timestamp` must be valid.
- Duplicate records must be isolated.

---

# 4. Products Dataset

## Purpose

Master dataset containing product-level information.

## Grain

One row per product.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| product_id | STRING | PK | NO | Unique product identifier |
| product_name | STRING | - | NO | Product name |
| category | STRING | - | NO | Product category |
| subcategory | STRING | - | YES | Product subcategory |
| brand | STRING | - | YES | Brand |
| unit_cost | DECIMAL(12,2) | - | NO | Product cost |
| selling_price | DECIMAL(12,2) | - | NO | Standard selling price |
| shelf_life_days | INTEGER | - | YES | Shelf life |
| active_flag | BOOLEAN | - | NO | Product availability |
| created_at | TIMESTAMP | - | NO | Creation timestamp |
| updated_at | TIMESTAMP | - | YES | Last update timestamp |

## Quality Rules

- `product_id` must be unique.
- `unit_cost >= 0`.
- `selling_price >= 0`.
- `shelf_life_days > 0` when populated.
- Product category cannot be null.

---

# 5. Inventory Dataset

## Purpose

Tracks inventory levels across stores and warehouses.

## Grain

One inventory snapshot per:

**Product × Location × Timestamp**

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| inventory_id | STRING | PK | NO | Unique inventory record |
| product_id | STRING | FK | NO | Product identifier |
| store_id | STRING | FK | YES | Store identifier |
| warehouse_id | STRING | FK | YES | Warehouse identifier |
| snapshot_timestamp | TIMESTAMP | NO | NO | Inventory snapshot time |
| available_quantity | INTEGER | - | NO | Available inventory |
| reserved_quantity | INTEGER | - | NO | Reserved inventory |
| reorder_point | INTEGER | - | NO | Reorder threshold |
| safety_stock | INTEGER | - | NO | Safety stock |
| inventory_value | DECIMAL(14,2) | - | YES | Inventory monetary value |

## Quality Rules

- Exactly one location type should be populated where applicable.
- `available_quantity >= 0`.
- `reserved_quantity >= 0`.
- `reorder_point >= 0`.
- `safety_stock >= 0`.
- Product must exist.

---

# 6. Stores Dataset

## Purpose

Contains store master information.

## Grain

One row per store.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| store_id | STRING | PK | NO | Unique store identifier |
| store_name | STRING | - | NO | Store name |
| city | STRING | - | NO | City |
| state | STRING | - | NO | State/region |
| country | STRING | - | NO | Country |
| region | STRING | - | YES | Business region |
| store_type | STRING | - | YES | Store classification |
| latitude | DOUBLE | - | YES | Latitude |
| longitude | DOUBLE | - | YES | Longitude |
| opening_date | DATE | - | YES | Store opening date |
| active_flag | BOOLEAN | - | NO | Store status |

---

# 7. Warehouses Dataset

## Purpose

Contains warehouse master information and capacity.

## Grain

One row per warehouse.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| warehouse_id | STRING | PK | NO | Unique warehouse identifier |
| warehouse_name | STRING | - | NO | Warehouse name |
| city | STRING | - | NO | Warehouse city |
| state | STRING | - | NO | Warehouse state |
| region | STRING | - | YES | Business region |
| capacity_units | INTEGER | - | NO | Maximum capacity |
| current_utilization_units | INTEGER | - | NO | Current utilization |
| warehouse_type | STRING | - | YES | Warehouse classification |
| active_flag | BOOLEAN | - | NO | Warehouse status |

## Quality Rules

- `capacity_units > 0`.
- `current_utilization_units >= 0`.
- Utilization cannot exceed capacity unless explicitly flagged.

---

# 8. Suppliers Dataset

## Purpose

Tracks supplier information and reliability.

## Grain

One row per:

**Supplier × Product**

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| supplier_id | STRING | PK | NO | Supplier identifier |
| supplier_name | STRING | - | NO | Supplier name |
| product_id | STRING | FK | NO | Supplied product |
| lead_time_days | INTEGER | - | NO | Expected lead time |
| unit_cost | DECIMAL(12,2) | - | NO | Supplier unit cost |
| reliability_score | DOUBLE | - | YES | Supplier reliability |
| minimum_order_quantity | INTEGER | - | YES | Minimum order quantity |
| active_flag | BOOLEAN | - | NO | Supplier status |

## Quality Rules

- `lead_time_days >= 0`.
- `unit_cost >= 0`.
- `reliability_score` must be between 0 and 1.
- Product must exist.

---

# 9. Shipments Dataset

## Purpose

Tracks supplier-to-warehouse shipment activity and delivery performance.

## Grain

One row per shipment.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| shipment_id | STRING | PK | NO | Shipment identifier |
| supplier_id | STRING | FK | NO | Supplier |
| product_id | STRING | FK | NO | Product |
| warehouse_id | STRING | FK | NO | Destination warehouse |
| order_date | DATE | - | NO | Shipment order date |
| expected_delivery_date | DATE | - | NO | Expected delivery |
| actual_delivery_date | DATE | - | YES | Actual delivery |
| quantity | INTEGER | - | NO | Shipment quantity |
| status | STRING | - | NO | Shipment status |
| delay_days | INTEGER | - | YES | Delivery delay |

## Quality Rules

- `quantity > 0`.
- Supplier must exist.
- Product must exist.
- Warehouse must exist.
- `actual_delivery_date >= order_date`.
- `delay_days >= 0`.

---

# 10. Returns Dataset

## Purpose

Tracks returned products for product and demand analysis.

## Grain

One row per return event.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| return_id | STRING | PK | NO | Return identifier |
| transaction_id | STRING | FK | NO | Original transaction |
| product_id | STRING | FK | NO | Returned product |
| store_id | STRING | FK | NO | Store |
| return_date | DATE | NO | NO | Return date |
| quantity | INTEGER | - | NO | Returned quantity |
| reason | STRING | - | YES | Return reason |

## Quality Rules

- `quantity > 0`.
- Transaction must exist.
- Product must exist.
- Store must exist.

---

# 11. Weather Dataset

## Purpose

Provides external weather signals that may influence product demand.

## Grain

One row per:

**Location × Date**

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| weather_date | DATE | PK | NO | Observation date |
| city | STRING | PK | NO | City |
| temperature_avg | DOUBLE | - | YES | Average temperature |
| temperature_max | DOUBLE | - | YES | Maximum temperature |
| temperature_min | DOUBLE | - | YES | Minimum temperature |
| rainfall_mm | DOUBLE | - | YES | Rainfall |
| humidity | DOUBLE | - | YES | Humidity |
| weather_condition | STRING | - | YES | Weather category |

---

# 12. Calendar Dataset

## Purpose

Provides temporal and seasonal information for forecasting.

## Grain

One row per calendar date.

## Schema

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| date | DATE | PK | NO | Calendar date |
| day_of_week | INTEGER | - | NO | Day number |
| day_name | STRING | - | NO | Day name |
| week_of_year | INTEGER | - | NO | Week number |
| month | INTEGER | - | NO | Month |
| month_name | STRING | - | NO | Month name |
| quarter | INTEGER | - | NO | Quarter |
| year | INTEGER | - | NO | Year |
| weekend_flag | BOOLEAN | - | NO | Weekend indicator |
| holiday_flag | BOOLEAN | - | NO | Holiday indicator |
| holiday_name | STRING | - | YES | Holiday name |
| festival_flag | BOOLEAN | - | NO | Festival indicator |

---

# 13. Core Relationships

```text
products
   |
   +---- sales
   |
   +---- inventory
   |
   +---- suppliers
   |
   +---- shipments
   |
   +---- returns


stores
   |
   +---- sales
   |
   +---- inventory
   |
   +---- returns


warehouses
   |
   +---- inventory
   |
   +---- shipments


suppliers
   |
   +---- shipments
   |
   +---- products


calendar
   |
   +---- sales
   +---- inventory
   +---- shipments
   +---- returns


weather
   |
   +---- stores / locations