"""
Inventory Replenishment & Decision Intelligence Engine.
Computes dynamic safety stock, reorder points (ROP), order quantities (ROQ), and stockout risk urgency.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class StockoutUrgency(str, Enum):
    CRITICAL = "CRITICAL"      # Stockout expected within <= 3 days
    HIGH = "HIGH"              # Stockout expected before supplier lead-time arrival
    MEDIUM = "MEDIUM"          # Inventory below Reorder Point (buffer eroding)
    HEALTHY = "HEALTHY"        # Inventory within optimal operating bounds
    OVERSTOCK = "OVERSTOCK"    # Excessive capital tied up (> 60 days forward coverage)


@dataclass
class ReplenishmentRecommendation:
    product_id: str
    store_id: str
    current_inventory: float
    daily_demand_forecast: float
    demand_std_dev: float
    supplier_lead_time_days: float
    lead_time_std_dev: float
    service_level_pct: float
    dynamic_safety_stock: float
    reorder_point: float
    effective_inventory: float
    recommended_order_quantity: float
    days_of_coverage: float
    urgency: StockoutUrgency
    action_required: bool
    reason: str


class InventoryRecommendationEngine:
    """
    Translates demand predictions into optimal replenishment policies.
    """

    SERVICE_LEVEL_Z_SCORES = {
        90.0: 1.28,
        95.0: 1.645,
        98.0: 2.05,
        99.0: 2.33,
    }

    def __init__(
        self,
        default_service_level: float = 95.0,
        default_lead_time_days: float = 7.0,
        default_lead_time_std: float = 1.5,
        min_order_quantity: float = 10.0,
        order_cycle_days: int = 14,
    ):
        self.default_service_level = default_service_level
        self.default_lead_time_days = default_lead_time_days
        self.default_lead_time_std = default_lead_time_std
        self.min_order_quantity = min_order_quantity
        self.order_cycle_days = order_cycle_days

    def calculate_dynamic_safety_stock(
        self,
        daily_demand_mean: float,
        daily_demand_std: float,
        lead_time_days: float,
        lead_time_std: float,
        service_level: float,
    ) -> float:
        """
        Calculates dynamic safety stock accounting for both demand and lead-time stochasticity:
        SS = Z * sqrt(L * sigma_d^2 + d^2 * sigma_L^2)
        """
        z = self.SERVICE_LEVEL_Z_SCORES.get(service_level, 1.645)
        d_mean = max(0.1, daily_demand_mean)
        d_std = max(0.1, daily_demand_std)
        lt_mean = max(1.0, lead_time_days)
        lt_std = max(0.1, lead_time_std)

        variance = (lt_mean * (d_std ** 2)) + ((d_mean ** 2) * (lt_std ** 2))
        return float(np.ceil(z * np.sqrt(variance)))

    def calculate_reorder_point(self, daily_demand_mean: float, lead_time_days: float, safety_stock: float) -> float:
        """
        ROP = (Daily Demand * Lead Time) + Safety Stock
        """
        lead_time_demand = max(0.0, daily_demand_mean) * max(1.0, lead_time_days)
        return float(np.ceil(lead_time_demand + safety_stock))

    def evaluate_inventory_position(
        self,
        product_id: str,
        store_id: str,
        current_inventory: float,
        daily_demand_forecast: float,
        demand_std_dev: float = 2.0,
        in_transit_inventory: float = 0.0,
        reserved_inventory: float = 0.0,
        supplier_lead_time_days: Optional[float] = None,
        service_level: Optional[float] = None,
    ) -> ReplenishmentRecommendation:
        """
        Evaluates a single product-store inventory node and generates prescriptive purchase orders.
        """
        lt = supplier_lead_time_days or self.default_lead_time_days
        sl = service_level or self.default_service_level

        # 1. Compute dynamic safety stock and ROP
        safety_stock = self.calculate_dynamic_safety_stock(
            daily_demand_mean=daily_demand_forecast,
            daily_demand_std=demand_std_dev,
            lead_time_days=lt,
            lead_time_std=self.default_lead_time_std,
            service_level=sl,
        )
        rop = self.calculate_reorder_point(daily_demand_forecast, lt, safety_stock)

        # 2. Net Effective Inventory
        effective_inv = current_inventory + in_transit_inventory - reserved_inventory
        daily_rate = max(0.1, daily_demand_forecast)
        days_of_coverage = round(current_inventory / daily_rate, 1)

        # 3. Target Max Stock Level
        cycle_stock = daily_rate * self.order_cycle_days
        target_max_stock = rop + cycle_stock

        # 4. Replenishment Quantity (ROQ) & Action Decision
        if effective_inv < rop:
            raw_order_qty = target_max_stock - effective_inv
            roq = float(np.ceil(max(self.min_order_quantity, raw_order_qty)))
            action_required = True
        else:
            roq = 0.0
            action_required = False

        # 5. Urgency Classification
        if days_of_coverage <= 3.0:
            urgency = StockoutUrgency.CRITICAL
            reason = f"Critical risk! Stockout expected in ~{days_of_coverage} days. Immediate expedite order required."
        elif days_of_coverage <= lt:
            urgency = StockoutUrgency.HIGH
            reason = f"High risk: Current stock ({days_of_coverage}d) cannot bridge supplier lead time ({lt}d)."
        elif effective_inv < rop:
            urgency = StockoutUrgency.MEDIUM
            reason = f"Inventory breached Reorder Point ({effective_inv} < {rop}). Replenishment order recommended."
        elif days_of_coverage > 60.0:
            urgency = StockoutUrgency.OVERSTOCK
            reason = f"Excess inventory ({days_of_coverage}d coverage). Hold replenishment to release working capital."
        else:
            urgency = StockoutUrgency.HEALTHY
            reason = f"Optimal stock level ({days_of_coverage}d coverage). No action needed."

        return ReplenishmentRecommendation(
            product_id=product_id,
            store_id=store_id,
            current_inventory=current_inventory,
            daily_demand_forecast=round(daily_demand_forecast, 2),
            demand_std_dev=round(demand_std_dev, 2),
            supplier_lead_time_days=lt,
            lead_time_std_dev=self.default_lead_time_std,
            service_level_pct=sl,
            dynamic_safety_stock=safety_stock,
            reorder_point=rop,
            effective_inventory=effective_inv,
            recommended_order_quantity=roq,
            days_of_coverage=days_of_coverage,
            urgency=urgency,
            action_required=action_required,
            reason=reason,
        )

    def generate_recommendations(
        self,
        forecast_df: pd.DataFrame,
        inventory_df: pd.DataFrame,
        supplier_df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Batch-evaluates inventory recommendations for entire catalog.
        """
        # Aggregate average forward daily demand per entity
        avg_forecast = forecast_df.groupby(["product_id", "store_id"])["predicted_demand"].agg(
            mean_demand="mean",
            std_demand="std"
        ).reset_index()
        avg_forecast["std_demand"] = avg_forecast["std_demand"].fillna(1.5)

        merged = avg_forecast.merge(inventory_df, on=["product_id", "store_id"], how="inner")

        recommendations = []
        for _, row in merged.iterrows():
            rec = self.evaluate_inventory_position(
                product_id=str(row["product_id"]),
                store_id=str(row["store_id"]),
                current_inventory=float(row.get("total_available", 100.0)),
                daily_demand_forecast=float(row["mean_demand"]),
                demand_std_dev=float(row["std_demand"]),
                in_transit_inventory=float(row.get("in_transit", 0.0)),
                reserved_inventory=float(row.get("total_reserved", 0.0)),
                supplier_lead_time_days=float(row.get("lead_time_days", self.default_lead_time_days)),
            )
            recommendations.append({
                "product_id": rec.product_id,
                "store_id": rec.store_id,
                "current_inventory": rec.current_inventory,
                "daily_demand_forecast": rec.daily_demand_forecast,
                "safety_stock": rec.dynamic_safety_stock,
                "reorder_point": rec.reorder_point,
                "effective_inventory": rec.effective_inventory,
                "recommended_order_qty": rec.recommended_order_quantity,
                "days_of_coverage": rec.days_of_coverage,
                "urgency": rec.urgency.value,
                "action_required": rec.action_required,
                "reason": rec.reason,
            })

        return pd.DataFrame(recommendations)
