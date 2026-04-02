from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.artifact_store import get_feature_columns, get_metadata, get_model, get_scaler


FEATURE_REASON_MAP = {
    "ContractRisk": "Weak contract commitment",
    "PaymentMethod_Electronic check": "Payment issue",
    "MonthlyCharges": "Price sensitivity",
    "ChargesPerMonth": "Price sensitivity",
    "HighValue": "High-value risk",
    "tenure": "Early lifecycle risk",
    "TenureBucket": "Early lifecycle risk",
    "ServiceCount": "Low product stickiness",
    "OnlineSecurity_Yes": "Low product stickiness",
    "TechSupport_Yes": "Low product stickiness",
    "InternetService_Fiber optic": "Low engagement",
}


def _reason_for_feature(feature: str) -> str:
    for key, reason in FEATURE_REASON_MAP.items():
        if key in feature:
            return reason
    return "Low engagement"


def local_reason_hints_fast(processed_row: pd.Series) -> list[str]:
    metadata = get_metadata()
    medians: dict[str, Any] = metadata.get("feature_medians", {})
    ranked = metadata.get("feature_importance", [])
    scored: list[tuple[float, str]] = []
    for item in ranked[:16]:
        feature = item["feature"]
        if feature not in processed_row.index:
            continue
        weight = float(item.get("importance", 0.01)) + 1e-6
        median_val = float(medians.get(feature, 0.0))
        val = float(processed_row[feature])
        scored.append((abs(val - median_val) * weight, feature))
    scored.sort(key=lambda t: t[0], reverse=True)
    reasons: list[str] = []
    seen: set[str] = set()
    for _, feature in scored:
        reason = _reason_for_feature(feature)
        if reason not in seen:
            seen.add(reason)
            reasons.append(reason)
        if len(reasons) >= 3:
            break
    return reasons


def explain_prediction(processed_row: pd.DataFrame, probability: float) -> list[dict[str, Any]]:
    feature_columns = get_feature_columns()
    metadata = get_metadata()
    medians = metadata.get("feature_medians", {})
    model = get_model()
    scaler = get_scaler()

    row = processed_row.iloc[0].to_dict()
    contributions: list[dict[str, Any]] = []
    for feature in feature_columns:
        altered = dict(row)
        altered[feature] = medians.get(feature, 0.0)
        altered_df = pd.DataFrame([altered])[feature_columns]
        altered_scaled = scaler.transform(altered_df)
        altered_probability = float(model.predict_proba(altered_scaled)[0][1])
        delta = probability - altered_probability
        if abs(delta) < 1e-5:
            continue
        contributions.append(
            {
                "feature": feature,
                "reason": _reason_for_feature(feature),
                "contribution": round(abs(delta), 4),
                "raw_delta": delta,
            }
        )

    contributions.sort(key=lambda item: abs(item["raw_delta"]), reverse=True)
    top_items = contributions[:5]
    total = sum(item["contribution"] for item in top_items) or 1.0
    formatted: list[dict[str, Any]] = []
    for item in top_items:
        formatted.append(
            {
                "feature": item["feature"],
                "reason": item["reason"],
                "contribution": round(item["contribution"], 4),
                "contribution_pct": round((item["contribution"] / total) * 100, 2),
                "direction": "increase" if item["raw_delta"] >= 0 else "decrease",
            }
        )
    return formatted
