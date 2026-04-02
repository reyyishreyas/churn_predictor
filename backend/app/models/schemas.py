from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CustomerPayload(BaseModel):
    customer_id: str = Field(default="demo-user-001")
    gender: Literal["Male", "Female"] = "Female"
    SeniorCitizen: int = Field(default=0, ge=0, le=1)
    Partner: Literal["Yes", "No"] = "Yes"
    Dependents: Literal["Yes", "No"] = "No"
    tenure: int = Field(default=12, ge=0, le=120)
    PhoneService: Literal["Yes", "No"] = "Yes"
    MultipleLines: Literal["Yes", "No", "No phone service"] = "No"
    InternetService: Literal["DSL", "Fiber optic", "No"] = "Fiber optic"
    OnlineSecurity: Literal["Yes", "No", "No internet service"] = "No"
    OnlineBackup: Literal["Yes", "No", "No internet service"] = "Yes"
    DeviceProtection: Literal["Yes", "No", "No internet service"] = "No"
    TechSupport: Literal["Yes", "No", "No internet service"] = "No"
    StreamingTV: Literal["Yes", "No", "No internet service"] = "Yes"
    StreamingMovies: Literal["Yes", "No", "No internet service"] = "Yes"
    Contract: Literal["Month-to-month", "One year", "Two year"] = "Month-to-month"
    PaperlessBilling: Literal["Yes", "No"] = "Yes"
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ] = "Electronic check"
    MonthlyCharges: float = Field(default=79.9, ge=0)
    TotalCharges: float = Field(default=959.0, ge=0)
    days_since_last_login: int | None = Field(default=None, ge=0, le=365)
    avg_logins_per_week: float | None = Field(default=None, ge=0, le=100)
    avg_session_duration_minutes: float = Field(default=18.0, ge=0, le=600)
    feature_usage_score: float = Field(default=52.0, ge=0, le=100)
    payment_failures_90d: int = Field(default=0, ge=0, le=20)
    activity_trend_pct: float | None = Field(default=None, ge=-100, le=100)
    support_tickets_30d: int = Field(default=0, ge=0, le=100)


class ContributionItem(BaseModel):
    feature: str
    reason: str
    contribution: float
    contribution_pct: float
    direction: Literal["increase", "decrease"]


class PredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    risk_level: Literal["Low", "Medium", "High"]
    engagement_score: int
    engagement_label: Literal["Low", "Moderate", "High"]
    segment: str
    strategy: str
    top_reasons: list[str]
    recommended_actions: list[str]
    auto_triggered: bool
    explainability: list[ContributionItem]
    business_signals: dict[str, Any]


class CustomerPayloadUpdate(BaseModel):
    gender: str | None = None
    SeniorCitizen: int | None = None
    Partner: str | None = None
    Dependents: str | None = None
    tenure: int | None = None
    PhoneService: str | None = None
    MultipleLines: str | None = None
    InternetService: str | None = None
    OnlineSecurity: str | None = None
    OnlineBackup: str | None = None
    DeviceProtection: str | None = None
    TechSupport: str | None = None
    StreamingTV: str | None = None
    StreamingMovies: str | None = None
    Contract: str | None = None
    PaperlessBilling: str | None = None
    PaymentMethod: str | None = None
    MonthlyCharges: float | None = None
    TotalCharges: float | None = None
    days_since_last_login: int | None = None
    avg_logins_per_week: float | None = None
    avg_session_duration_minutes: float | None = None
    feature_usage_score: float | None = None
    payment_failures_90d: int | None = None
    activity_trend_pct: float | None = None
    support_tickets_30d: int | None = None


class SimulationRequest(BaseModel):
    base_user: CustomerPayload
    updated_user: CustomerPayloadUpdate


class SimulationResponse(BaseModel):
    customer_id: str
    original_probability: float
    new_probability: float
    absolute_change: float
    relative_change_pct: float
    original_risk_level: str
    new_risk_level: str
    new_top_reasons: list[str]
    recommended_actions: list[str]
    summary: str


class BatchPredictResponse(BaseModel):
    total_users: int
    high_risk_users: int
    emails_sent: int
    failed: int
    intervention_threshold: float
    email_batch_min_risk: str = "threshold"
    email_mode: str = "stub"
    smtp_configured: bool = False
    dry_run: bool
    send_emails: bool
    would_send: int
    enriched_csv_base64: str | None = None
