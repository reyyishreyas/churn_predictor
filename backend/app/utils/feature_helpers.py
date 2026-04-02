from __future__ import annotations

from typing import Any

import pandas as pd


MODEL_FIELDS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]

SUPPLEMENTAL_FIELDS = [
    "customer_id",
    "days_since_last_login",
    "avg_logins_per_week",
    "avg_session_duration_minutes",
    "feature_usage_score",
    "payment_failures_90d",
    "activity_trend_pct",
    "support_tickets_30d",
]


def clean_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    if "customerID" in data.columns:
        data = data.drop(columns=["customerID"])
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
    data["TotalCharges"] = data["TotalCharges"].fillna(data["TotalCharges"].median())
    if "Churn" in data.columns:
        data["Churn"] = (data["Churn"] == "Yes").astype(int)
    return data


def to_model_payload(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    if data.get("TotalCharges") is None:
        tenure = max(int(data.get("tenure", 0)), 1)
        monthly = float(data.get("MonthlyCharges", 0.0))
        data["TotalCharges"] = round(monthly * tenure, 2)
    return {field: data[field] for field in MODEL_FIELDS}


def count_active_services(payload: dict[str, Any]) -> int:
    service_cols = [
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
    ]
    return sum(payload.get(col) not in {"No", "No internet service", "No phone service"} for col in service_cols)


def derive_business_features(payload: dict[str, Any]) -> dict[str, Any]:
    service_count = count_active_services(payload)
    tenure = int(payload["tenure"])
    monthly = float(payload["MonthlyCharges"])
    contract = payload["Contract"]
    payment_failures = int(payload.get("payment_failures_90d", 0))
    recency_days = payload.get("days_since_last_login")
    if recency_days is None:
        contract_penalty = 8 if contract == "Month-to-month" else -4 if contract == "Two year" else 0
        recency_days = round(max(0, min(90, 34 - min(tenure, 30) * 0.7 + contract_penalty + max(0, 3 - service_count) * 3 + payment_failures * 4)))
    logins_per_week = payload.get("avg_logins_per_week")
    if logins_per_week is None:
        internet_boost = 0.7 if payload["InternetService"] != "No" else 0.0
        logins_per_week = round(max(0.2, min(14.0, 0.8 + service_count * 0.55 + min(tenure, 36) / 18 + internet_boost)), 2)
    activity_trend_pct = payload.get("activity_trend_pct")
    if activity_trend_pct is None:
        trend = (logins_per_week * 6.5) - (recency_days * 1.15)
        if contract == "Month-to-month":
            trend -= 8
        activity_trend_pct = round(max(-100.0, min(100.0, trend)), 2)
    avg_session_duration = float(payload.get("avg_session_duration_minutes", 18.0))
    feature_usage_score = float(payload.get("feature_usage_score", min(100.0, 15 + service_count * 11)))
    support_tickets = int(payload.get("support_tickets_30d", 0))
    return {
        "recency_days": int(recency_days),
        "frequency_logins_per_week": float(logins_per_week),
        "monetary_value": round(monthly, 2),
        "activity_trend_pct": float(activity_trend_pct),
        "service_count": service_count,
        "avg_session_duration_minutes": avg_session_duration,
        "feature_usage_score": feature_usage_score,
        "payment_failures_90d": payment_failures,
        "support_tickets_30d": support_tickets,
        "is_high_value": monthly >= 90 or (monthly >= 70 and tenure >= 24),
    }


def build_reason_candidates(
    payload: dict[str, Any],
    business_features: dict[str, Any],
    local_reason_hints: list[str],
    churn_probability: float = 0.0,
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    def add(reason: str) -> None:
        if reason and reason not in seen:
            seen.add(reason)
            ordered.append(reason)

    for hint in local_reason_hints:
        add(hint)

    if business_features["recency_days"] >= 21:
        add("Inactive user")
    if business_features["frequency_logins_per_week"] < 2.5 or business_features["feature_usage_score"] < 40:
        add("Low engagement")
    if business_features["payment_failures_90d"] > 0 or payload["PaymentMethod"] == "Electronic check":
        add("Payment issue")
    if payload["Contract"] == "Month-to-month":
        add("Weak contract commitment")
    if payload["MonthlyCharges"] >= 85:
        add("Price sensitivity")
    if payload["tenure"] <= 6:
        add("Early lifecycle risk")
    if business_features["service_count"] <= 3:
        add("Low product stickiness")
    if business_features["is_high_value"] and churn_probability >= 0.45:
        add("High-value risk")
    return ordered[:3]
