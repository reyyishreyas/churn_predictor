from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.api_client import get_insights

st.set_page_config(page_title="Churn Predictor", layout="wide")

st.title("Churn dashboard")
st.caption("Metrics from the running API (`GET /insights`).")

insights = get_insights()

metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("Total Users", f"{insights['total_users']:,}")
metric_b.metric("Observed Churn Rate", f"{insights['overall_churn_rate']:.1%}")
metric_c.metric("Mean Predicted Risk", f"{insights['churn_probability_summary']['mean']:.1%}")
metric_d.metric("P90 Risk", f"{insights['churn_probability_summary']['p90']:.1%}")

left, right = st.columns((1.2, 1))

with left:
    st.subheader("Risk Distribution")
    risk_df = pd.DataFrame(
        [{"risk": key, "count": value} for key, value in insights["predicted_risk_distribution"].items()]
    )
    st.plotly_chart(
        px.bar(
            risk_df,
            x="risk",
            y="count",
            color="risk",
            color_discrete_map={"Low": "#66bb6a", "Medium": "#ffa726", "High": "#ef5350"},
            text_auto=True,
        ).update_layout(showlegend=False, height=360),
        use_container_width=True,
    )

with right:
    st.subheader("Engagement Distribution")
    engagement_df = pd.DataFrame(
        [{"label": key, "count": value} for key, value in insights["engagement_distribution"].items()]
    )
    st.plotly_chart(
        px.pie(
            engagement_df,
            values="count",
            names="label",
            hole=0.45,
            color="label",
            color_discrete_map={"Low": "#ef5350", "Moderate": "#ffca28", "High": "#42a5f5"},
        ).update_layout(height=360),
        use_container_width=True,
    )

lower_left, lower_right = st.columns(2)

with lower_left:
    st.subheader("Top Churn Reasons")
    reasons_df = pd.DataFrame(insights["top_churn_reasons"], columns=["reason", "count"])
    st.dataframe(reasons_df, use_container_width=True, hide_index=True)

with lower_right:
    st.subheader("Top Feature Importance")
    importance_df = pd.DataFrame(insights["feature_importance"])
    st.plotly_chart(
        px.bar(
            importance_df.sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            color="importance",
            color_continuous_scale="Blues",
        ).update_layout(height=360, coloraxis_showscale=False),
        use_container_width=True,
    )

st.subheader("Model Comparison")
metrics_df = pd.DataFrame(insights["model_metrics"]).T.reset_index().rename(columns={"index": "model_key"})
st.dataframe(metrics_df, use_container_width=True, hide_index=True)
