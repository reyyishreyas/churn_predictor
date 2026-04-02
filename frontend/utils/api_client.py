from __future__ import annotations

import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("CHURN_API_URL", "http://localhost:8000")


def _request(method: str, path: str, payload: dict | None = None):
    response = requests.request(method, f"{API_BASE_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def default_customer_payload() -> dict:
    return {
        "customer_id": "demo-user-001",
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 79.9,
        "TotalCharges": 959.0,
        "days_since_last_login": 18,
        "avg_logins_per_week": 2.1,
        "avg_session_duration_minutes": 14.0,
        "feature_usage_score": 42.0,
        "payment_failures_90d": 1,
        "activity_trend_pct": None,
        "support_tickets_30d": 0,
    }


@st.cache_data(show_spinner=False)
def get_insights():
    return _request("GET", "/insights")


@st.cache_data(show_spinner=False)
def get_model_metrics():
    return _request("GET", "/model-metrics")


def predict_user(payload: dict):
    return _request("POST", "/predict", payload)


def simulate_user(base_user: dict, updated_user: dict):
    return _request("POST", "/simulate", {"base_user": base_user, "updated_user": updated_user})


def batch_predict_upload(
    file_bytes: bytes,
    filename: str,
    *,
    send_emails: bool = True,
    dry_run: bool = False,
    include_enriched_csv: bool = True,
) -> dict:
    files = {"file": (filename, file_bytes, "text/csv")}
    data = {
        "send_emails": str(send_emails).lower(),
        "dry_run": str(dry_run).lower(),
        "include_enriched_csv": str(include_enriched_csv).lower(),
    }
    base = API_BASE_URL.rstrip("/")
    for path in ("/batch-predict", "/api/batch-predict"):
        response = requests.post(
            f"{base}{path}",
            files=files,
            data=data,
            timeout=600,
        )
        if response.status_code != 404:
            response.raise_for_status()
            return response.json()
    response.raise_for_status()
    return response.json()
