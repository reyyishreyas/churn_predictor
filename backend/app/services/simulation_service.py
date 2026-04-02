from __future__ import annotations

from app.services.prediction_service import analyze_user


def run_simulation(base_user: dict, updated_user: dict) -> dict:
    baseline = analyze_user(base_user, allow_intervention=False)
    scenario_payload = {**base_user, **{key: value for key, value in updated_user.items() if value is not None}}
    scenario = analyze_user(scenario_payload, allow_intervention=False)
    original = baseline["churn_probability"]
    new = scenario["churn_probability"]
    diff = new - original
    relative = 0.0 if original == 0 else (diff / original) * 100
    direction = "reduced" if diff < 0 else "increased"
    summary = f"Churn {direction} from {original:.0%} → {new:.0%} (Δ {diff:+.1%})."
    return {
        "customer_id": base_user["customer_id"],
        "original_probability": original,
        "new_probability": new,
        "absolute_change": round(diff, 4),
        "relative_change_pct": round(relative, 2),
        "original_risk_level": baseline["risk_level"],
        "new_risk_level": scenario["risk_level"],
        "new_top_reasons": scenario["top_reasons"],
        "recommended_actions": scenario["recommended_actions"],
        "summary": summary,
    }
