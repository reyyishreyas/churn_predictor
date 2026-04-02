from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.utils.logger import configure_logger


logger = configure_logger("email_service", settings.logs_dir / "email_service.log")


@dataclass(slots=True)
class EmailSendResult:
    ok: bool
    provider: str
    error: str | None = None


def compose_retention_email(
    *,
    to_email: str,
    user_label: str,
    churn_probability: float,
    risk_level: str,
    segment: str,
    engagement_label: str,
    top_reasons: list[str],
    recommended_actions: list[str],
) -> tuple[str, str, str]:
    reasons_text = "; ".join(top_reasons) if top_reasons else "recent patterns in your account activity"
    actions_text = (
        " ".join(f"• {a}" for a in recommended_actions)
        if recommended_actions
        else "• Our team is ready to help you get the most value from your subscription."
    )
    greeting = user_label.strip() if user_label.strip() else "there"
    if any("inactive" in r.lower() or "miss" in r.lower() for r in top_reasons):
        subject = "We Miss You – Let’s Get You Back!"
    elif risk_level == "High":
        subject = "We’re here to help — your account matters to us"
    else:
        subject = "A quick note from your customer success team"

    text_body = (
        f"Hi {greeting},\n\n"
        f"We noticed signals that suggest you might not be getting everything you need from us. "
        f"Areas we’re focused on helping with: {reasons_text}.\n\n"
        f"Here’s what we recommend next:\n{actions_text}\n\n"
        f"Your engagement level appears {engagement_label} and you’re in our “{segment}” segment. "
        f"If anything feels off with billing, access, or product fit, reply to this email and we’ll prioritize it.\n\n"
        f"Thank you for being with us.\n\n"
        f"— {settings.mail_from_name}\n"
    )
    html_body = f"""\
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#1a1a1a">
<p>Hi {greeting},</p>
<p>We noticed signals that suggest you might not be getting everything you need from us.
<strong>What we’re seeing:</strong> {reasons_text}.</p>
<p><strong>Recommended next steps:</strong></p>
<ul>{''.join(f'<li>{a}</li>' for a in recommended_actions) or '<li>Our team is ready to help you get the most value.</li>'}</ul>
<p>Your <strong>engagement</strong> appears <strong>{engagement_label}</strong> and you’re in the
<strong>{segment}</strong> segment. Estimated churn risk band: <strong>{risk_level}</strong>
(probability ~{churn_probability:.0%}).</p>
<p>If billing, access, or product fit is getting in the way, reply to this email—we’ll prioritize it.</p>
<p>Thank you for being with us.</p>
<p>— {settings.mail_from_name}</p>
</body></html>"""
    return subject, text_body, html_body


def send_email(to_address: str, subject: str, text_body: str, html_body: str) -> EmailSendResult:
    if settings.smtp_user and settings.smtp_password:
        return _send_smtp(to_address, subject, text_body, html_body)

    logger.info(
        "STUB email (no SMTP credentials) | to=%s subject=%s — set GMAIL_ADDRESS + GMAIL_APP_PASSWORD or SMTP_USER + SMTP_PASSWORD",
        to_address,
        subject,
    )
    return EmailSendResult(ok=True, provider="stub")


def _send_smtp(to_address: str, subject: str, text_body: str, html_body: str) -> EmailSendResult:
    host = settings.smtp_host or "smtp.gmail.com"
    port = settings.smtp_port or 587
    if not settings.mail_from_email:
        return EmailSendResult(ok=False, provider="smtp", error="MAIL_FROM_EMAIL not configured")
    if not settings.smtp_user or not settings.smtp_password:
        return EmailSendResult(
            ok=False,
            provider="smtp",
            error="SMTP_USER (or GMAIL_ADDRESS) and SMTP_PASSWORD (or GMAIL_APP_PASSWORD) are required",
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.mail_from_name} <{settings.mail_from_email}>"
    msg["To"] = to_address
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=60) as server:
            if settings.smtp_use_tls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info("SMTP sent | to=%s host=%s", to_address, host)
        return EmailSendResult(ok=True, provider="smtp")
    except Exception as exc:  # noqa: BLE001
        logger.exception("SMTP failed | to=%s", to_address)
        return EmailSendResult(ok=False, provider="smtp", error=str(exc))
