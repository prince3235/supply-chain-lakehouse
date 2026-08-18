"""
Business KPI Framework.
Contains standardized definitions and constants for metrics
to ensure BI reports and dashboards use consistent vocabulary.
"""

# Inventory KPIs
KPI_INVENTORY_VALUE = "Total financial value of available and reserved inventory."
KPI_STOCKOUT_RISK = "Boolean indicator: True if available quantity < safety stock."

# Supplier KPIs
KPI_SUPPLIER_ON_TIME_RATE = "Ratio of on-time shipments to total shipments per supplier per month."
KPI_AVERAGE_LEAD_TIME = "Average expected lead time in days for a supplier."

# Demand KPIs
KPI_DAILY_DEMAND = "Total quantity of a product sold in a single store on a given day."
KPI_DAILY_REVENUE = "Total revenue of a product sold in a single store on a given day."

# Logistics KPIs
KPI_INCOMING_VOLUME = "Total units expected to arrive at a warehouse on a given date."
KPI_DELAYED_SHIPMENTS = "Count of shipments arriving later than the expected delivery date."
