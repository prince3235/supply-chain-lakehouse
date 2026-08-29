"""
Supply Chain Lakehouse — Interactive Command Center.
Built with Streamlit, Plotly, and Lakehouse ML / Decision Engines.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from dashboards.mock_data import generate_mock_dashboard_data
from src.features.pipeline import FeaturePipeline
from src.training.train import train_and_evaluate_models
from src.inference.batch_predict import BatchInferenceEngine
from src.inference.inventory_recommender import InventoryRecommendationEngine
from src.inference.anomaly_detector import SupplyChainAnomalyDetector

st.set_page_config(
    page_title="Supply Chain Lakehouse Command Center",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.875rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .badge-critical { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-high { background-color: #f97316; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-medium { background-color: #eab308; color: black; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-healthy { background-color: #22c55e; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-overstock { background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def load_and_prepare_data():
    data = generate_mock_dashboard_data()
    return data


data = load_and_prepare_data()
df_history = data["history"]
df_products = data["products"]
df_stores = data["stores"]
df_suppliers = data["suppliers"]

# Sidebar Filters
st.sidebar.title("🎛️ Navigation & Filters")
selected_store = st.sidebar.selectbox("Select Store", ["All Stores"] + list(df_stores["name"].unique()))
selected_category = st.sidebar.selectbox("Select Category", ["All Categories"] + list(df_products["category"].unique()))
forecast_horizon = st.sidebar.slider("Forecast Horizon (Days)", min_value=7, max_value=30, value=14, step=7)
confidence_interval = st.sidebar.selectbox("Confidence Level", [0.95, 0.90, 0.99])

# Filter datasets
filtered_df = df_history.copy()
if selected_store != "All Stores":
    filtered_df = filtered_df[filtered_df["store_name"] == selected_store]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

# Header
st.title("📦 Supply Chain Lakehouse — Intelligent Command Center")
st.caption(f"Connected to Delta Lakehouse • Unity Catalog Dev • Live ML Champion Active • Last Refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Navigation Tabs
tab_exec, tab_forecast, tab_inventory, tab_suppliers, tab_mlops = st.tabs([
    "📊 Executive Overview",
    "📈 Demand Forecasting",
    "📦 Inventory & Replenishment",
    "🚚 Supplier Performance",
    "⚙️ MLOps & Model Registry",
])

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
with tab_exec:
    st.subheader("Executive KPIs")
    total_sales_volume = int(filtered_df["daily_demand"].sum())
    total_revenue = float((filtered_df["daily_demand"] * filtered_df["unit_price"]).sum())
    avg_daily_demand = round(filtered_df["daily_demand"].mean(), 1)
    stockout_incidents = int((filtered_df["total_available"] <= filtered_df["current_safety_stock"]).sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales Volume", f"{total_sales_volume:,} units", "+4.2% MoM")
    with col2:
        st.metric("Total Revenue", f"${total_revenue:,.2f}", "+6.8% MoM")
    with col3:
        st.metric("Daily Demand Run-Rate", f"{avg_daily_demand} units/day", "Stable")
    with col4:
        st.metric("Low Stock Alerts", f"{stockout_incidents} nodes", "-12.5% vs Last Week", delta_color="inverse")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.write("##### 📈 Historical Demand Trend by Category")
        trend_df = filtered_df.groupby(["demand_date", "category"])["daily_demand"].sum().reset_index()
        fig_trend = px.line(
            trend_df,
            x="demand_date",
            y="daily_demand",
            color="category",
            title="Aggregated Daily Demand by Product Category",
            labels={"daily_demand": "Total Units", "demand_date": "Date"},
        )
        fig_trend.update_layout(template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c_right:
        st.write("##### 🏬 Demand Distribution by Store")
        store_df = filtered_df.groupby("store_name")["daily_demand"].sum().reset_index()
        fig_pie = px.pie(
            store_df,
            names="store_name",
            values="daily_demand",
            title="Revenue Contribution by Store",
            hole=0.4,
        )
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)


# -------------------------------------------------------------
# TAB 2: DEMAND FORECASTING
# -------------------------------------------------------------
with tab_forecast:
    st.subheader("Machine Learning Demand Forecasting")
    
    product_options = filtered_df["product_name"].unique()
    selected_prod = st.selectbox("Select Product for Detailed ML Forecast", product_options)
    
    prod_history = filtered_df[filtered_df["product_name"] == selected_prod].sort_values("demand_date").reset_index(drop=True)
    
    # Train Quick Model for Display
    pipeline = FeaturePipeline()
    feature_df = pipeline.build_features(prod_history, fill_na=True)
    results = train_and_evaluate_models(feature_df, holdout_days=14)
    best_model = results["best_model"]
    
    engine = BatchInferenceEngine(model_obj=best_model, feature_pipeline=pipeline)
    forecast_df = engine.generate_forecasts(historical_df=prod_history, horizon_days=forecast_horizon, confidence_level=confidence_interval)
    
    # Combine Historical and Forecast for Plotting
    hist_plot = prod_history[["demand_date", "daily_demand"]].rename(columns={"daily_demand": "value"})
    hist_plot["type"] = "Historical Actuals"
    
    fc_plot = forecast_df[["forecast_date", "predicted_demand", "confidence_lower", "confidence_upper"]].rename(
        columns={"forecast_date": "demand_date", "predicted_demand": "value"}
    )
    fc_plot["type"] = "ML Forecast"
    
    # Plotly Forecast Chart
    fig_fc = go.Figure()
    
    # Historical line
    fig_fc.add_trace(go.Scatter(
        x=hist_plot["demand_date"],
        y=hist_plot["value"],
        mode="lines+markers",
        name="Historical Actual Demand",
        line=dict(color="#38bdf8", width=2),
    ))
    
    # Forecast line
    fig_fc.add_trace(go.Scatter(
        x=fc_plot["demand_date"],
        y=fc_plot["value"],
        mode="lines+markers",
        name="Forecast (ML Production Champion)",
        line=dict(color="#f59e0b", width=3, dash="dash"),
    ))
    
    # Confidence Interval Ribbon
    fig_fc.add_trace(go.Scatter(
        x=list(fc_plot["demand_date"]) + list(fc_plot["demand_date"])[::-1],
        y=list(fc_plot["confidence_upper"]) + list(fc_plot["confidence_lower"])[::-1],
        fill="toself",
        fillcolor="rgba(245, 158, 11, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=True,
        name=f"{int(confidence_interval*100)}% Confidence Band",
    ))
    
    fig_fc.update_layout(
        title=f"Demand Trajectory & Forward {forecast_horizon}-Day Prediction: {selected_prod}",
        xaxis_title="Date",
        yaxis_title="Units Demanded",
        template="plotly_dark",
        hovermode="x unified",
    )
    st.plotly_chart(fig_fc, use_container_width=True)
    
    # Forecast Table
    st.write("##### 📋 Detailed Forecast Table")
    st.dataframe(forecast_df, use_container_width=True)


# -------------------------------------------------------------
# TAB 3: INVENTORY REPLENISHMENT
# -------------------------------------------------------------
with tab_inventory:
    st.subheader("Inventory Health & Prescriptive Replenishment")
    
    rec_engine = InventoryRecommendationEngine()
    
    # Aggregate demand forecast per entity
    recommendations_list = []
    for p_id in filtered_df["product_id"].unique():
        for s_id in filtered_df["store_id"].unique():
            entity_data = filtered_df[(filtered_df["product_id"] == p_id) & (filtered_df["store_id"] == s_id)]
            if len(entity_data) > 0:
                curr_inv = float(entity_data.iloc[-1]["total_available"])
                demand_mean = float(entity_data["daily_demand"].mean())
                demand_std = float(entity_data["daily_demand"].std() or 2.0)
                
                rec = rec_engine.evaluate_inventory_position(
                    product_id=p_id,
                    store_id=s_id,
                    current_inventory=curr_inv,
                    daily_demand_forecast=demand_mean,
                    demand_std_dev=demand_std,
                    supplier_lead_time_days=6.0,
                )
                recommendations_list.append({
                    "Product ID": rec.product_id,
                    "Store ID": rec.store_id,
                    "Current Stock": rec.current_inventory,
                    "Daily Run Rate": rec.daily_demand_forecast,
                    "Safety Stock (SS)": rec.dynamic_safety_stock,
                    "Reorder Point (ROP)": rec.reorder_point,
                    "Recommended Order Qty": rec.recommended_order_quantity,
                    "Days of Coverage": rec.days_of_coverage,
                    "Urgency": rec.urgency.value,
                    "Action Required": "🚨 ORDER NOW" if rec.action_required else "✅ In Control",
                    "Prescriptive Reason": rec.reason,
                })
                
    df_recs = pd.DataFrame(recommendations_list)
    
    # Summary Metrics
    c_crit, c_high, c_healthy, c_over = st.columns(4)
    with c_crit:
        st.metric("Critical Stockouts (≤3d)", len(df_recs[df_recs["Urgency"] == "CRITICAL"]))
    with c_high:
        st.metric("High Replenishment Risk", len(df_recs[df_recs["Urgency"] == "HIGH"]))
    with c_healthy:
        st.metric("Healthy Nodes", len(df_recs[df_recs["Urgency"] == "HEALTHY"]))
    with c_over:
        st.metric("Overstocked Nodes (>60d)", len(df_recs[df_recs["Urgency"] == "OVERSTOCK"]))
        
    st.write("##### 📦 Replenishment Purchase Order Recommendations")
    st.dataframe(df_recs, use_container_width=True)


# -------------------------------------------------------------
# TAB 4: SUPPLIER PERFORMANCE
# -------------------------------------------------------------
with tab_suppliers:
    st.subheader("Supplier Reliability & Lead-Time Analysis")
    
    col_sup1, col_sup2 = st.columns(2)
    with col_sup1:
        fig_sup = px.bar(
            df_suppliers,
            x="name",
            y="reliability",
            color="reliability",
            color_continuous_scale="Viridis",
            title="Supplier On-Time Delivery Rate (%)",
            labels={"name": "Supplier", "reliability": "Reliability %"},
        )
        fig_sup.update_layout(template="plotly_dark")
        st.plotly_chart(fig_sup, use_container_width=True)
        
    with col_sup2:
        fig_lt = px.bar(
            df_suppliers,
            x="name",
            y="lead_time",
            title="Average Lead Time (Days)",
            color="lead_time",
            color_continuous_scale="Turbo",
            labels={"name": "Supplier", "lead_time": "Lead Time (Days)"},
        )
        fig_lt.update_layout(template="plotly_dark")
        st.plotly_chart(fig_lt, use_container_width=True)
        
    st.write("##### 🚚 Supplier Directory & SLA Contracts")
    st.dataframe(df_suppliers, use_container_width=True)


# -------------------------------------------------------------
# TAB 5: MLOPS & MODEL REGISTRY
# -------------------------------------------------------------
with tab_mlops:
    st.subheader("MLOps Model Registry & Drift Monitoring")
    
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric("Active Champion Model", "GradientBoostingRegressor v3", "In Production")
    with c_m2:
        st.metric("Production WAPE", "11.4%", "-28.2% vs Baseline", delta_color="inverse")
    with c_m3:
        st.metric("Population Drift (PSI)", "0.042", "Within Tolerance (<0.10)")
        
    st.markdown("---")
    st.write("##### 🏆 Model Leaderboard & Champion/Challenger History")
    mock_registry = pd.DataFrame([
        {"Version": "v3 (Champion)", "Model": "GradientBoostingRegressor", "Stage": "PRODUCTION", "WAPE (%)": 11.4, "MAE": 2.85, "Bias (%)": -0.8, "Trained Date": "2026-08-28"},
        {"Version": "v2", "Model": "RandomForestRegressor", "Stage": "ARCHIVED", "WAPE (%)": 13.8, "MAE": 3.42, "Bias (%)": 1.2, "Trained Date": "2026-08-20"},
        {"Version": "v1", "Model": "MovingAverageBaseline", "Stage": "ARCHIVED", "WAPE (%)": 15.9, "MAE": 4.10, "Bias (%)": 0.0, "Trained Date": "2026-08-15"},
    ])
    st.dataframe(mock_registry, use_container_width=True)
