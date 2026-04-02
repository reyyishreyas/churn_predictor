from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

_backend_root = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv

    load_dotenv(_backend_root / ".env")
except ImportError:
    pass


@dataclass(slots=True)
class Settings:
    app_name: str = "Churn Predictor"
    app_version: str = "1.0.0"
    risk_threshold: float = field(default_factory=lambda: float(os.getenv("CHURN_TRIGGER_THRESHOLD", "0.60")))
    classification_threshold: float = field(default_factory=lambda: float(os.getenv("MODEL_CLASSIFICATION_THRESHOLD", "0.35")))
    backend_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[3])
    artifacts_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    data_path: Path = field(init=False)
    action_map: dict[str, list[str]] = field(init=False)
    email_mode: str = field(init=False)
    smtp_host: str = field(init=False)
    smtp_port: int = field(init=False)
    smtp_user: str = field(init=False)
    smtp_password: str = field(init=False)
    smtp_use_tls: bool = field(init=False)
    mail_from_email: str = field(init=False)
    mail_from_name: str = field(init=False)
    email_batch_min_risk: str = field(init=False)

    def __post_init__(self) -> None:
        self.artifacts_dir = self.backend_dir / "artifacts"
        self.logs_dir = self.backend_dir / "logs"
        self.data_path = self.backend_dir / "data" / "churn.csv"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.action_map = self._load_action_map()
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = (
            os.getenv("SMTP_USER") or os.getenv("GMAIL_ADDRESS") or os.getenv("SMTP_EMAIL") or ""
        ).strip()
        self.smtp_password = (os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD", "") or "").strip()
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
        mail_from_env = (os.getenv("MAIL_FROM_EMAIL") or "").strip()
        if mail_from_env:
            self.mail_from_email = mail_from_env
        elif self.smtp_user:
            self.mail_from_email = self.smtp_user
        else:
            self.mail_from_email = ""
        self.mail_from_name = os.getenv("MAIL_FROM_NAME", "Retention Team")
        self.email_batch_min_risk = os.getenv("EMAIL_BATCH_MIN_RISK", "threshold").strip().lower()
        raw_email_mode = os.getenv("EMAIL_MODE")
        if raw_email_mode is None or str(raw_email_mode).strip() == "":
            self.email_mode = "smtp" if self.smtp_user and self.smtp_password else "stub"
        else:
            self.email_mode = str(raw_email_mode).strip().lower()
        if self.email_mode == "smtp" and not self.smtp_host:
            self.smtp_host = "smtp.gmail.com"
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        if self.smtp_user and self.smtp_password and self.email_mode == "stub":
            self.email_mode = "smtp"
            if not self.smtp_host:
                self.smtp_host = "smtp.gmail.com"
                self.smtp_port = int(os.getenv("SMTP_PORT", "587"))

    def _load_action_map(self) -> dict[str, list[str]]:
        default_map = {
            "Low engagement": ["Send push notification", "Launch in-app walkthrough"],
            "Inactive user": ["Send reactivation email", "Offer win-back content"],
            "User inactive": ["Send reactivation email", "Offer win-back content"],
            "Payment issue": ["Retry payment reminder", "Prompt billing update"],
            "High-value risk": ["Offer loyalty discount", "Route to success manager"],
            "Weak contract commitment": ["Promote annual plan incentive"],
            "Price sensitivity": ["Offer targeted retention discount"],
            "Low product stickiness": ["Recommend sticky features tutorial"],
            "Early lifecycle risk": ["Trigger onboarding success sequence"],
        }
        config_path = os.getenv("ACTION_MAP_PATH")
        if not config_path:
            return default_map
        path = Path(config_path)
        if not path.exists():
            return default_map
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        return {**default_map, **loaded}


settings = Settings()
