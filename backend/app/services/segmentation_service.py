from __future__ import annotations


def segment_user(payload: dict, churn_probability: float, engagement_score: int, business_features: dict) -> tuple[str, str]:
    if payload["tenure"] <= 3:
        return "New users", "Accelerate onboarding, highlight core value, and reinforce the first success milestone."
    if business_features["is_high_value"] and churn_probability >= 0.45:
        return "High-value users", "Escalate to retention playbook with VIP outreach and personalized incentives."
    if churn_probability >= 0.6 or engagement_score < 40:
        return "At-risk users", "Launch immediate intervention workflow with reactivation, support, and offer sequencing."
    return "Active users", "Maintain healthy engagement with upsell education and lifecycle nudges."
