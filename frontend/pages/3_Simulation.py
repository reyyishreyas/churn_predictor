from __future__ import annotations

import streamlit as st

from utils.api_client import default_customer_payload, simulate_user

st.title("What-If Simulation")
base = default_customer_payload()

with st.form("simulation-form"):
    st.write("Base user")
    col1, col2 = st.columns(2)
    with col1:
        customer_id = st.text_input("Customer ID", value=base["customer_id"])
        tenure = st.slider("Tenure", 0, 72, base["tenure"])
        monthly = st.slider("Monthly Charges", 0.0, 150.0, float(base["MonthlyCharges"]))
        total = st.number_input("Total Charges", min_value=0.0, value=float(base["TotalCharges"]))
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"], index=0)
        payment_method = st.selectbox(
            "Payment Method",
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
            index=0,
        )
    with col2:
        new_logins = st.slider("Scenario Logins / Week", 0.0, 10.0, 4.0, 0.1)
        new_recency = st.slider("Scenario Days Since Last Login", 0, 90, 8)
        new_usage = st.slider("Scenario Feature Usage Score", 0.0, 100.0, 68.0, 1.0)
        new_failures = st.slider("Scenario Payment Failures", 0, 5, 0)
        new_contract = st.selectbox("Scenario Contract", ["Month-to-month", "One year", "Two year"], index=1)
    submitted = st.form_submit_button("Run Simulation", use_container_width=True)

if submitted:
    base_user = {
        **base,
        "customer_id": customer_id,
        "tenure": tenure,
        "MonthlyCharges": monthly,
        "TotalCharges": total,
        "Contract": contract,
        "PaymentMethod": payment_method,
    }
    updated_user = {
        "avg_logins_per_week": new_logins,
        "days_since_last_login": new_recency,
        "feature_usage_score": new_usage,
        "payment_failures_90d": new_failures,
        "Contract": new_contract,
    }
    result = simulate_user(base_user, updated_user)
    c1, c2, c3 = st.columns(3)
    c1.metric("Original Risk", f"{result['original_probability']:.1%}", result["original_risk_level"])
    c2.metric("New Risk", f"{result['new_probability']:.1%}", result["new_risk_level"])
    c3.metric("Delta", f"{result['absolute_change']:.1%}", f"{result['relative_change_pct']:.1f}%")
    st.write(result["summary"])
    st.write("New Top Reasons:", ", ".join(result["new_top_reasons"]))
    st.write("Recommended Actions:", ", ".join(result["recommended_actions"]))
