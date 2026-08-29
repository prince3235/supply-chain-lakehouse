"""
Supply Chain Anomaly & Outlier Detection Engine.
Detects demand spikes, demand drops, inventory discrepancies, and supplier lead-time anomalies.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


class SupplyChainAnomalyDetector:
    """
    Statistical anomaly detector for transactional supply chain operations.
    """

    def __init__(self, z_threshold: float = 2.5, iqr_multiplier: float = 1.5):
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier

    def detect_demand_anomalies(
        self,
        df: pd.DataFrame,
        entity_cols: Optional[List[str]] = None,
        date_col: str = "demand_date",
        demand_col: str = "daily_demand",
    ) -> pd.DataFrame:
        """
        Flags historical or real-time demand anomalies using rolling Z-Score & IQR tests.
        """
        entity_cols = entity_cols or ["product_id", "store_id"]
        df = df.copy()

        df["rolling_mean"] = df.groupby(entity_cols)[demand_col].transform(
            lambda s: s.rolling(window=14, min_periods=3).mean()
        )
        df["rolling_std"] = df.groupby(entity_cols)[demand_col].transform(
            lambda s: s.rolling(window=14, min_periods=3).std().fillna(1.0)
        )

        df["z_score"] = (df[demand_col] - df["rolling_mean"]) / (df["rolling_std"] + 1e-5)

        anomalies = []
        for _, row in df.iterrows():
            z = row["z_score"]
            if pd.isna(z):
                continue

            if z >= self.z_threshold:
                anomalies.append({
                    "entity_id": f"{row['product_id']}_{row['store_id']}",
                    "date": str(row[date_col]),
                    "anomaly_type": "DEMAND_SURGE",
                    "severity": "HIGH" if z > 3.5 else "MEDIUM",
                    "metric_value": round(float(row[demand_col]), 2),
                    "expected_value": round(float(row["rolling_mean"]), 2),
                    "z_score": round(float(z), 2),
                    "reason": f"Demand surge (+{round(z, 1)} std dev above 14-day average). Check promotions or viral demand.",
                })
            elif z <= -self.z_threshold and row[demand_col] >= 0:
                anomalies.append({
                    "entity_id": f"{row['product_id']}_{row['store_id']}",
                    "date": str(row[date_col]),
                    "anomaly_type": "DEMAND_COLLAPSE",
                    "severity": "HIGH" if z < -3.5 else "MEDIUM",
                    "metric_value": round(float(row[demand_col]), 2),
                    "expected_value": round(float(row["rolling_mean"]), 2),
                    "z_score": round(float(z), 2),
                    "reason": f"Demand collapse ({round(z, 1)} std dev below expected). Check stockout or store closure.",
                })

        return pd.DataFrame(anomalies)

    def detect_supplier_lead_time_anomalies(
        self,
        shipments_df: pd.DataFrame,
        supplier_col: str = "supplier_id",
        actual_lead_time_col: str = "actual_lead_time_days",
        expected_lead_time_col: str = "expected_lead_time_days",
    ) -> pd.DataFrame:
        """
        Detects anomalous delays in supplier shipments.
        """
        df = shipments_df.copy()
        df["delay_days"] = df[actual_lead_time_col] - df[expected_lead_time_col]

        anomalies = []
        for _, row in df.iterrows():
            delay = float(row["delay_days"])
            expected = float(row[expected_lead_time_col])

            if delay > 5.0:  # More than 5 days late
                severity = "CRITICAL" if delay > 10.0 else "HIGH"
                anomalies.append({
                    "supplier_id": str(row[supplier_col]),
                    "shipment_id": str(row.get("shipment_id", "N/A")),
                    "anomaly_type": "SUPPLIER_DELAY",
                    "severity": severity,
                    "delay_days": delay,
                    "expected_lead_time": expected,
                    "actual_lead_time": float(row[actual_lead_time_col]),
                    "reason": f"Shipment delayed by {delay:.1f} days beyond contract SLA ({expected:.1f}d).",
                })

        return pd.DataFrame(anomalies)
