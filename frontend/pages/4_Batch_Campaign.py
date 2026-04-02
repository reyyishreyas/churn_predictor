from __future__ import annotations

import base64
import io

import pandas as pd
import streamlit as st

from utils.api_client import batch_predict_upload

st.title("Batch upload")
st.caption("CSV must include user_id, email, and the same feature columns as the training data.")

uploaded = st.file_uploader("Customer CSV", type=["csv"])

col_a, col_b, col_c = st.columns(3)
with col_a:
    dry_run = st.toggle("Dry run (no emails sent)", value=False)
with col_b:
    send_emails = st.toggle("Send real emails", value=True)
with col_c:
    include_csv = st.toggle("Return enriched CSV in response", value=True)

run = st.button("Run batch job", type="primary", use_container_width=True)

if run and uploaded is not None:
    raw = uploaded.getvalue()
    with st.spinner("Processing batch…"):
        result = batch_predict_upload(
            raw,
            uploaded.name,
            send_emails=send_emails,
            dry_run=dry_run,
            include_enriched_csv=include_csv,
        )
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total users", result["total_users"])
    m2.metric("High risk (≥70%)", result["high_risk_users"])
    m3.metric("Emails sent", result["emails_sent"])
    m4.metric("Failed / blocked", result["failed"])
    m5.metric("Eligible rows (see API)", result["would_send"])
    if result.get("email_mode") == "stub" and result.get("send_emails") and not result.get("dry_run"):
        st.warning("SMTP not configured; set Gmail credentials in backend/.env.")
    st.json({k: v for k, v in result.items() if k != "enriched_csv_base64"})
    b64 = result.get("enriched_csv_base64")
    if b64:
        decoded = base64.b64decode(b64).decode("utf-8")
        st.download_button(
            "Download enriched CSV",
            data=decoded,
            file_name="batch_enriched.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.dataframe(pd.read_csv(io.StringIO(decoded)), use_container_width=True, hide_index=True)
elif run and uploaded is None:
    st.warning("Upload a CSV first.")

st.subheader("Required columns")
st.markdown(
    """
- **user_id** (or `customer_id` / `customerID`) and **email**
- All model fields: `gender`, `SeniorCitizen`, `Partner`, `Dependents`, `tenure`, `PhoneService`,
  `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`,
  `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`,
  `PaymentMethod`, `MonthlyCharges`, `TotalCharges`
- Optional: `days_since_last_login`, `avg_logins_per_week`, `avg_session_duration_minutes`,
  `feature_usage_score`, `payment_failures_90d`, `activity_trend_pct`, `support_tickets_30d`
- `Churn` column is ignored if present
"""
)
