from __future__ import annotations

from typing import Any

import pandas as pd

from app.config import settings
from app.services.artifact_store import get_model, get_preprocessor, get_scaler
from app.services.engagement_service import calculate_engagement_score
from app.services.explainability_service import explain_prediction
from app.services.intervention_engine import intervention_engine
from app.services.recommendation_service import recommend_actions
from app.services.segmentation_service import segment_user
from app.utils.feature_helpers import build_reason_candidates, derive_business_features, to_model_payload


def _risk_level(probability: float) -> str:
    if probability < 0.4:
        return "Low"
    if probability < 0.7:
        return "Medium"
    return "High"


def analyze_user(payload: dict[str, Any], allow_intervention: bool = True) -> dict[str, Any]:
    model_payload = to_model_payload(payload)
    frame = pd.DataFrame([model_payload])
    preprocessor = get_preprocessor()
    processed = preprocessor.transform(frame)
    scaler = get_scaler()
    scaled = scaler.transform(processed)
    model = get_model()

    probability = float(model.predict_proba(scaled)[0][1])
    business_features = derive_business_features(payload)
    engagement_score, engagement_label = calculate_engagement_score(business_features)
    explanation = explain_prediction(processed, probability)
    local_reason_hints = [item["reason"] for item in explanation]
    reasons = build_reason_candidates(payload, business_features, local_reason_hints, probability)
    segment, strategy = segment_user(payload, probability, engagement_score, business_features)
    actions = recommend_actions(reasons)
    auto_triggered = intervention_engine.trigger(payload["customer_id"], probability, reasons, actions) if allow_intervention else False

    return {
        "customer_id": payload["customer_id"],
        "churn_probability": round(probability, 4),
        "risk_level": _risk_level(probability),
        "engagement_score": engagement_score,
        "engagement_label": engagement_label,
        "segment": segment,
        "strategy": strategy,
        "top_reasons": reasons,
        "recommended_actions": actions,
        "auto_triggered": auto_triggered,
        "explainability": explanation,
        "business_signals": {
            **business_features,
            "classification_threshold": settings.classification_threshold,
            "intervention_threshold": settings.risk_threshold,
        },
    }
