from __future__ import annotations

from collections import Counter
from functools import lru_cache

import numpy as np
import pandas as pd

from app.services.artifact_store import get_dataset, get_metadata, get_preprocessor, get_scaler, get_model
from app.utils.feature_helpers import clean_training_frame, derive_business_features
from app.services.engagement_service import calculate_engagement_score


@lru_cache(maxsize=1)
def build_insights() -> dict:
    raw_df = get_dataset()
    df = clean_training_frame(raw_df)
    preprocessor = get_preprocessor()
    model_df = df.drop(columns=["Churn"])
    processed = preprocessor.transform(model_df)
    scaled = get_scaler().transform(processed)
    probabilities = get_model().predict_proba(scaled)[:, 1]

    risk_labels = pd.cut(probabilities, bins=[-0.01, 0.4, 0.7, 1.0], labels=["Low", "Medium", "High"])
    risk_distribution = risk_labels.value_counts().reindex(["Low", "Medium", "High"], fill_value=0).to_dict()

    engagement_buckets: list[str] = []
    reason_counter: Counter[str] = Counter()
    for row in raw_df.to_dict(orient="records"):
        payload = {
            **row,
            "customer_id": row.get("customerID", "unknown"),
            "payment_failures_90d": 1 if row["PaymentMethod"] == "Electronic check" else 0,
            "feature_usage_score": 55.0,
            "avg_session_duration_minutes": 18.0,
            "support_tickets_30d": 0,
        }
        business_features = derive_business_features(payload)
        score, label = calculate_engagement_score(business_features)
        engagement_buckets.append(label)
        if business_features["recency_days"] >= 21:
            reason_counter["Inactive user"] += 1
        if business_features["frequency_logins_per_week"] < 2.5:
            reason_counter["Low engagement"] += 1
        if payload["PaymentMethod"] == "Electronic check":
            reason_counter["Payment issue"] += 1
        if payload["Contract"] == "Month-to-month":
            reason_counter["Weak contract commitment"] += 1
        if payload["MonthlyCharges"] >= 85:
            reason_counter["Price sensitivity"] += 1

    metadata = get_metadata()
    feature_importance = metadata.get("feature_importance", [])
    metrics = metadata.get("metrics", {})
    actual_churn_rate = round(float(df["Churn"].mean()), 4)

    tenure_bins = pd.cut(df["tenure"], bins=[-1, 12, 36, 100], labels=["0-12 mo", "13-36 mo", "37+ mo"])
    churn_trend = []
    for bucket in ["0-12 mo", "13-36 mo", "37+ mo"]:
        mask = tenure_bins == bucket
        if not mask.any():
            continue
        churn_trend.append(
            {
                "tenure_band": bucket,
                "population": int(mask.sum()),
                "observed_churn_rate": round(float(df.loc[mask, "Churn"].mean()), 4),
                "mean_predicted_risk": round(float(np.mean(probabilities[mask.to_numpy()])), 4),
            }
        )

    return {
        "total_users": int(len(raw_df)),
        "overall_churn_rate": actual_churn_rate,
        "predicted_risk_distribution": risk_distribution,
        "engagement_distribution": dict(Counter(engagement_buckets)),
        "top_churn_reasons": reason_counter.most_common(5),
        "feature_importance": feature_importance,
        "model_metrics": metrics,
        "churn_probability_summary": {
            "mean": round(float(np.mean(probabilities)), 4),
            "median": round(float(np.median(probabilities)), 4),
            "p90": round(float(np.quantile(probabilities, 0.9)), 4),
        },
        "churn_trend_by_tenure": churn_trend,
    }
