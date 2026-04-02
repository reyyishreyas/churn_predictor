from __future__ import annotations

import base64
import io
import os
import re
from typing import Any

import numpy as np
import pandas as pd

from app.config import settings
from app.services.artifact_store import get_model, get_preprocessor, get_scaler
from app.services.email_service import compose_retention_email, send_email
from app.services.engagement_service import calculate_engagement_score
from app.services.explainability_service import local_reason_hints_fast
from app.services.recommendation_service import recommend_actions
from app.services.segmentation_service import segment_user
from app.utils.feature_helpers import MODEL_FIELDS, build_reason_candidates, derive_business_features
from app.utils.logger import append_jsonl, configure_logger


logger = configure_logger("batch_service", settings.logs_dir / "batch_service.log")

_EMAIL_OK = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _intervention_threshold() -> float:
    raw = os.getenv("CHURN_TRIGGER_THRESHOLD")
    return float(raw) if raw is not None else settings.risk_threshold


def _risk_level(probability: float) -> str:
    if probability < 0.4:
        return "Low"
    if probability < 0.7:
        return "Medium"
    return "High"


def _batch_email_qualifies(churn_probability: float, risk: str, threshold: float) -> bool:
    mode = settings.email_batch_min_risk
    if mode == "high":
        return risk == "High"
    if mode == "medium":
        return risk in ("Medium", "High")
    if mode in ("threshold", "any", "all"):
        return churn_probability > threshold
    return churn_probability > threshold


def normalize_batch_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    rename: dict[str, str] = {}
    for col in df.columns:
        raw = str(col).strip()
        low = raw.lower().replace(" ", "")
        if low in ("userid", "user_id", "customerid", "customer_id"):
            rename[col] = "user_id"
        elif low == "email":
            rename[col] = "email"
        else:
            rename[col] = raw
    out = df.rename(columns=rename)
    return out


def _validate_batch_columns(df: pd.DataFrame) -> None:
    if "user_id" not in df.columns:
        raise ValueError("CSV must include a user identifier column: user_id, customer_id, or customerID.")
    if "email" not in df.columns:
        raise ValueError("CSV must include an 'email' column.")
    missing = [c for c in MODEL_FIELDS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required model columns: {missing}")


def _coerce_model_frame(df: pd.DataFrame) -> pd.DataFrame:
    mdf = df[MODEL_FIELDS].copy()
    mdf["SeniorCitizen"] = pd.to_numeric(mdf["SeniorCitizen"], errors="coerce").fillna(0).astype(int).clip(0, 1)
    mdf["tenure"] = pd.to_numeric(mdf["tenure"], errors="coerce").fillna(0).astype(int)
    mdf["MonthlyCharges"] = pd.to_numeric(mdf["MonthlyCharges"], errors="coerce").fillna(0.0)
    mdf["TotalCharges"] = pd.to_numeric(mdf["TotalCharges"], errors="coerce")
    med = float(mdf["TotalCharges"].median()) if mdf["TotalCharges"].notna().any() else 0.0
    mdf["TotalCharges"] = mdf["TotalCharges"].fillna(med)
    for col in MODEL_FIELDS:
        if col in ("SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"):
            continue
        mdf[col] = mdf[col].astype(str).str.strip()
    return mdf


def _row_to_payload(user_id: str, model_row: pd.Series, raw_row: pd.Series) -> dict[str, Any]:
    payload: dict[str, Any] = {"customer_id": user_id}
    for field in MODEL_FIELDS:
        payload[field] = model_row[field]
    supplemental_keys = (
        "days_since_last_login",
        "avg_logins_per_week",
        "avg_session_duration_minutes",
        "feature_usage_score",
        "payment_failures_90d",
        "activity_trend_pct",
        "support_tickets_30d",
    )
    for key in supplemental_keys:
        if key in raw_row.index and pd.notna(raw_row[key]):
            payload[key] = raw_row[key]
    return payload


def run_batch_job(
    file_bytes: bytes,
    *,
    send_emails: bool,
    dry_run: bool,
    include_enriched_csv: bool,
) -> dict[str, Any]:
    df = pd.read_csv(io.BytesIO(file_bytes))
    if df.empty:
        raise ValueError("Uploaded CSV is empty.")
    df = normalize_batch_dataframe(df)
    _validate_batch_columns(df)

    drop_cols = [c for c in ("Churn",) if c in df.columns]
    work = df.drop(columns=drop_cols, errors="ignore")

    model_df = _coerce_model_frame(work)
    preprocessor = get_preprocessor()
    processed = preprocessor.transform(model_df)
    scaler = get_scaler()
    scaled = scaler.transform(processed)
    model = get_model()
    probabilities = model.predict_proba(scaled)[:, 1].astype(np.float64)

    threshold = _intervention_threshold()
    high_risk_users = 0
    emails_sent = 0
    email_failures = 0
    would_send = 0
    batch_log_path = settings.logs_dir / "batch_email.jsonl"

    enriched_rows: list[dict[str, Any]] = []

    for i in range(len(work)):
        raw_row = work.iloc[i]
        model_row = model_df.iloc[i]
        user_id = str(raw_row["user_id"])
        raw_email = raw_row["email"]
        email_str = "" if pd.isna(raw_email) else str(raw_email).strip()
        email_valid = bool(email_str) and bool(_EMAIL_OK.match(email_str))
        prob = float(probabilities[i])
        risk = _risk_level(prob)
        if risk == "High":
            high_risk_users += 1

        payload = _row_to_payload(user_id, model_row, raw_row)
        business = derive_business_features(payload)
        engagement_score, engagement_label = calculate_engagement_score(business)
        hints = local_reason_hints_fast(processed.iloc[i])
        reasons = build_reason_candidates(payload, business, hints, prob)
        segment, _strategy = segment_user(payload, prob, engagement_score, business)
        actions = recommend_actions(reasons)

        qualifies = _batch_email_qualifies(prob, risk, threshold)
        if qualifies and email_valid:
            would_send += 1

        email_sent_flag = False
        email_error: str | None = None
        email_status = "not_applicable"

        if qualifies and not email_valid:
            email_failures += 1
            email_error = "missing_or_invalid_email"
            email_status = "failed"
        elif qualifies and dry_run:
            email_status = "dry_run"
        elif qualifies and not send_emails:
            email_status = "send_disabled"
        elif qualifies and email_valid and send_emails and not dry_run:
            subject, text_body, html_body = compose_retention_email(
                to_email=email_str,
                user_label=user_id,
                churn_probability=prob,
                risk_level=risk,
                segment=segment,
                engagement_label=engagement_label,
                top_reasons=reasons,
                recommended_actions=actions,
            )
            result = send_email(email_str, subject, text_body, html_body)
            email_sent_flag = result.ok
            if result.ok:
                emails_sent += 1
                email_status = "sent"
            else:
                email_failures += 1
                email_error = result.error
                email_status = "failed"

        append_jsonl(
            batch_log_path,
            {
                "user_id": user_id,
                "email": email_str,
                "churn_probability": round(prob, 4),
                "risk_level": risk,
                "email_status": email_status,
                "email_error": email_error,
                "top_reasons": reasons,
                "recommended_actions": actions,
            },
        )

        enriched_rows.append(
            {
                **{c: raw_row[c] for c in work.columns if c in raw_row.index},
                "churn_probability": round(prob, 6),
                "risk_level": risk,
                "engagement_score": engagement_score,
                "top_reasons": "|".join(reasons),
                "recommended_actions": "|".join(actions),
                "email_sent": email_sent_flag,
            }
        )

    enriched_csv_b64: str | None = None
    if include_enriched_csv:
        enriched_df = pd.DataFrame(enriched_rows)
        buf = io.StringIO()
        enriched_df.to_csv(buf, index=False)
        enriched_csv_b64 = base64.b64encode(buf.getvalue().encode("utf-8")).decode("ascii")

    return {
        "total_users": int(len(work)),
        "high_risk_users": high_risk_users,
        "emails_sent": emails_sent,
        "failed": email_failures,
        "intervention_threshold": threshold,
        "email_batch_min_risk": settings.email_batch_min_risk,
        "email_mode": settings.email_mode,
        "smtp_configured": bool(settings.smtp_user and settings.smtp_password),
        "dry_run": dry_run,
        "send_emails": send_emails,
        "would_send": would_send,
        "enriched_csv_base64": enriched_csv_b64,
    }
