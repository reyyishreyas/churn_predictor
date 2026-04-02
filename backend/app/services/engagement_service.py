from __future__ import annotations


def calculate_engagement_score(business_features: dict) -> tuple[int, str]:
    activity_component = min(business_features["frequency_logins_per_week"] / 7.0, 1.0) * 35
    session_component = min(business_features["avg_session_duration_minutes"] / 22.0, 1.0) * 20
    feature_component = min(business_features["feature_usage_score"] / 100.0, 1.0) * 25
    recency_component = max(0.0, 1.0 - business_features["recency_days"] / 60.0) * 20
    score = round(activity_component + session_component + feature_component + recency_component)
    if score < 40:
        return score, "Low"
    if score < 70:
        return score, "Moderate"
    return score, "High"
