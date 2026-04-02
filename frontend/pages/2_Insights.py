from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.api_client import get_insights, get_model_metrics

st.title("Business Insights")

insights = get_insights()
metrics = get_model_metrics()

left, right = st.columns(2)
with left:
    st.subheader("Feature Importance")
    importance_df = pd.DataFrame(insights["feature_importance"])
    st.plotly_chart(
        px.bar(
            importance_df.sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            color="importance",
            color_continuous_scale="Teal",
        ).update_layout(height=450, coloraxis_showscale=False),
        use_container_width=True,
    )

with right:
    st.subheader("Top Churn Reasons")
    reasons_df = pd.DataFrame(insights["top_churn_reasons"], columns=["reason", "count"])
    st.plotly_chart(
        px.bar(
            reasons_df,
            x="reason",
            y="count",
            color="count",
            color_continuous_scale="OrRd",
            text_auto=True,
        ).update_layout(height=450, coloraxis_showscale=False),
        use_container_width=True,
    )

st.subheader("Churn Trend by Tenure")
trend_df = pd.DataFrame(insights.get("churn_trend_by_tenure", []))
if not trend_df.empty:
    trend_melt = trend_df.melt(
        id_vars=["tenure_band", "population"],
        value_vars=["observed_churn_rate", "mean_predicted_risk"],
        var_name="metric",
        value_name="value",
    )
    trend_melt["metric"] = trend_melt["metric"].map(
        {"observed_churn_rate": "Observed churn", "mean_predicted_risk": "Mean predicted risk"}
    )
    st.plotly_chart(
        px.line(
            trend_melt,
            x="tenure_band",
            y="value",
            color="metric",
            markers=True,
            title="Historical churn vs model risk by tenure band",
        ).update_layout(height=420, yaxis_tickformat=".0%"),
        use_container_width=True,
    )
    st.dataframe(trend_df, use_container_width=True, hide_index=True)
else:
    st.info("Trend data unavailable.")

st.subheader("Model Comparison")
# Outer dict keys (e.g. stacking_ensemble); inner dict has key "model" (display name) — do not rename index to "model".
metrics_df = pd.DataFrame([{"model_key": key, **val} for key, val in metrics.items()])
st.dataframe(metrics_df, use_container_width=True, hide_index=True)
