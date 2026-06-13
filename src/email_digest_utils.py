"""Optional SMTP weekly progress digest."""

from __future__ import annotations

import smtplib
from datetime import UTC, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.gamification_utils import evaluate_badges, get_earned_badge_count
from src.progress_tracker_utils import compute_progress_skill_growth, get_gap_history_dataframe, load_progress_data
from src.secrets_utils import get_smtp_settings


def build_weekly_digest_text() -> str:
    """Build plain-text weekly progress digest."""
    progress = load_progress_data()
    history = get_gap_history_dataframe()
    growth = compute_progress_skill_growth()
    badges = evaluate_badges(progress)

    lines = [
        "CareerCompass Weekly Progress Digest",
        "===================================",
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Total gap analyses: {len(history)}",
        f"Badges earned: {get_earned_badge_count()}/{len(badges)}",
    ]

    if growth.get("available"):
        lines.extend(
            [
                f"Latest skill growth: {growth.get('growth_percent', 0.0)}%",
                f"Match score change: {growth.get('match_score_delta', 0.0):+.2f}%",
                f"Skills gained: {', '.join(growth.get('gained_skills', [])) or 'None'}",
            ]
        )
    else:
        lines.append(growth.get("message", "Run more analyses to unlock growth tracking."))

    if not history.empty:
        latest = history.sort_values("timestamp").iloc[-1]
        lines.extend(
            [
                "",
                "Latest analysis:",
                f"- Role: {latest.get('target_role', 'N/A')}",
                f"- Match score: {latest.get('match_score', 0.0)}%",
                f"- Missing skills: {latest.get('missing_count', 0)}",
            ]
        )

    lines.extend(["", "Keep building. CareerCompass"])
    return "\n".join(lines)


def smtp_configured() -> bool:
    settings = get_smtp_settings()
    return bool(settings.get("host") and settings.get("user") and settings.get("recipient"))


def send_weekly_digest(dry_run: bool = False) -> dict:
    """Send weekly digest email via SMTP. Returns status dict."""
    settings = get_smtp_settings()
    body = build_weekly_digest_text()

    if not smtp_configured():
        return {
            "sent": False,
            "mode": "not_configured",
            "message": "SMTP not configured. Add SMTP_* and DIGEST_RECIPIENT to secrets.toml or environment.",
            "preview": body,
        }

    if dry_run:
        return {"sent": False, "mode": "dry_run", "message": "Dry run only.", "preview": body}

    msg = MIMEMultipart()
    msg["From"] = settings["user"]
    msg["To"] = settings["recipient"]
    msg["Subject"] = f"CareerCompass Weekly Digest — {datetime.now(UTC).strftime('%Y-%m-%d')}"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings["host"], settings["port"], timeout=20) as server:
            server.starttls()
            if settings.get("password"):
                server.login(settings["user"], settings["password"])
            server.sendmail(settings["user"], [settings["recipient"]], msg.as_string())
    except Exception as exc:
        return {"sent": False, "mode": "error", "message": str(exc), "preview": body}

    return {"sent": True, "mode": "sent", "message": f"Digest sent to {settings['recipient']}", "preview": body}
