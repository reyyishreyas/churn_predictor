from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.api_client import default_customer_payload, predict_user

st.title("User Analysis")

defaults = default_customer_payload()

with st.form("prediction-form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        customer_id = st.text_input("Customer ID", value=defaults["customer_id"])
        gender = st.selectbox("Gender", ["Female", "Male"], index=0)
        senior = st.selectbox("Senior Citizen", [0, 1], index=0)
        partner = st.selectbox("Partner", ["Yes", "No"], index=0)
        dependents = st.selectbox("Dependents", ["No", "Yes"], index=0)
        tenure = st.slider("Tenure", 0, 72, defaults["tenure"])
        monthly = st.slider("Monthly Charges", 0.0, 150.0, float(defaults["MonthlyCharges"]))
        total = st.number_input("Total Charges", min_value=0.0, value=float(defaults["TotalCharges"]))
    with col2:
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"], index=0)
        payment_method = st.selectbox(
            "Payment Method",
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
            index=0,
        )
        internet = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"], index=0)
        phone = st.selectbox("Phone Service", ["Yes", "No"], index=0)
        multiple = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"], index=0)
        online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"], index=0)
        tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"], index=0)
        paperless = st.selectbox("Paperless Billing", ["Yes", "No"], index=0)
    with col3:
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"], index=0)
        device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"], index=0)
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"], index=0)
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"], index=0)
        days_since_last_login = st.slider("Days Since Last Login", 0, 90, 18)
        avg_logins_per_week = st.slider("Logins Per Week", 0.0, 10.0, 2.1, 0.1)
        avg_session_duration_minutes = st.slider("Avg Session Minutes", 0.0, 120.0, 14.0, 1.0)
        feature_usage_score = st.slider("Feature Usage Score", 0.0, 100.0, 42.0, 1.0)
        payment_failures = st.slider("Payment Failures (90d)", 0, 5, 1)
    submitted = st.form_submit_button("Analyze User", use_container_width=True)

if submitted:
    payload = {
        "customer_id": customer_id,
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone,
        "MultipleLines": multiple,
        "InternetService": internet,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly,
        "TotalCharges": total,
        "days_since_last_login": days_since_last_login,
        "avg_logins_per_week": avg_logins_per_week,
        "avg_session_duration_minutes": avg_session_duration_minutes,
        "feature_usage_score": feature_usage_score,
        "payment_failures_90d": payment_failures,
        "activity_trend_pct": None,
        "support_tickets_30d": 0,
    }
    result = predict_user(payload)

    stat1, stat2, stat3, stat4, stat5 = st.columns(5)
    stat1.metric("Churn Probability", f"{result['churn_probability']:.1%}")
    stat2.metric("Risk Level", result["risk_level"])
    stat3.metric("Engagement", f"{result['engagement_score']} ({result['engagement_label']})")
    stat4.metric("Segment", result["segment"])
    stat5.metric("Auto intervention", "Yes" if result.get("auto_triggered") else "No")

    left, right = st.columns((1.1, 1))
    with left:
        st.subheader("Reasons and Actions")
        st.write("Top Reasons:", ", ".join(result["top_reasons"]))
        st.write("Recommended Actions:", ", ".join(result["recommended_actions"]))
        st.write("Strategy:", result["strategy"])
        st.json(result["business_signals"])
    with right:
        st.subheader("Local Explainability")
        explain_df = pd.DataFrame(result["explainability"])
        st.plotly_chart(
            px.bar(
                explain_df.sort_values("contribution_pct"),
                x="contribution_pct",
                y="feature",
                orientation="h",
                color="direction",
                color_discrete_map={"increase": "#ef5350", "decrease": "#42a5f5"},
            ).update_layout(height=360),
            use_container_width=True,
        )
        st.dataframe(explain_df, use_container_width=True, hide_index=True)
