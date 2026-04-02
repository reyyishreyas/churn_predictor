from __future__ import annotations

import os
import uuid

from app.config import settings
from app.utils.logger import append_jsonl, configure_logger


logger = configure_logger("intervention_engine", settings.logs_dir / "intervention_engine.log")


def _resolve_threshold() -> float:
    raw = os.getenv("CHURN_TRIGGER_THRESHOLD")
    return float(raw) if raw is not None else settings.risk_threshold


def _simulate_channel(action: str) -> str:
    text = action.lower()
    if any(token in text for token in ("email", "win-back", "sequence", "crm")):
        return "email"
    if any(token in text for token in ("push", "notification", "walkthrough", "nudge")):
        return "push"
    if any(token in text for token in ("discount", "offer", "incentive", "loyalty", "billing", "payment")):
        return "offer_system"
    return "orchestrator"


def _simulate_dispatch(channel: str, action: str) -> dict:
    ref = str(uuid.uuid4())
    templates = {
        "email": {"provider": "ses_stub", "template": "reactivation_v2", "message_id": ref},
        "push": {"provider": "fcm_stub", "campaign": "retention_nudge", "delivery_id": ref},
        "offer_system": {"provider": "billing_stub", "offer_id": ref, "status": "issued"},
        "orchestrator": {"provider": "workflow_stub", "run_id": ref},
    }
    return {"channel": channel, "action": action, "payload": templates.get(channel, templates["orchestrator"])}


class InterventionEngine:
    def __init__(self) -> None:
        self.log_path = settings.logs_dir / "action_log.jsonl"

    def trigger(
        self,
        customer_id: str,
        churn_probability: float,
        reasons: list[str],
        actions: list[str],
    ) -> bool:
        threshold = _resolve_threshold()
        should_trigger = churn_probability >= threshold and bool(actions)
        if not should_trigger:
            logger.debug(
                "Skip intervention | user=%s prob=%s threshold=%s",
                customer_id,
                churn_probability,
                threshold,
            )
            return False

        primary_reason = reasons[0] if reasons else "Unknown"

        for action in actions:
            channel = _simulate_channel(action)
            simulation = _simulate_dispatch(channel, action)
            append_jsonl(
                self.log_path,
                {
                    "user_id": customer_id,
                    "churn_probability": round(float(churn_probability), 4),
                    "reason": primary_reason,
                    "reasons": list(reasons),
                    "action": action,
                    "channel": channel,
                    "simulation": simulation,
                },
            )
            logger.info(
                "INTERVENTION | user=%s prob=%s channel=%s | %s -> %s",
                customer_id,
                round(float(churn_probability), 4),
                channel,
                primary_reason,
                action,
            )
        return True


intervention_engine = InterventionEngine()
