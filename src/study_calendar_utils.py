"""Generate 4-week ICS study calendars from career actions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import textwrap
import uuid


def _ics_escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def _format_ics_datetime(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def generate_study_plan_ics(
    actions: list[dict],
    plan_title: str = "CareerCompass 4-Week Study Plan",
) -> str:
    """
    Generate an ICS calendar file from career action items.

    Distributes actions across 4 weeks (one primary action per week block).
    """
    now = datetime.now(UTC).replace(hour=9, minute=0, second=0, microsecond=0)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CareerCompass//Study Plan//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(plan_title)}",
    ]

    if not actions:
        uid = str(uuid.uuid4())
        start = now
        end = start + timedelta(hours=1)
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{_format_ics_datetime(now)}",
                f"DTSTART:{_format_ics_datetime(start)}",
                f"DTEND:{_format_ics_datetime(end)}",
                "SUMMARY:CareerCompass planning session",
                "DESCRIPTION:Add career actions to generate a full 4-week plan.",
                "END:VEVENT",
            ]
        )
    else:
        for idx, action in enumerate(actions[:4]):
            week_start = now + timedelta(days=7 * idx)
            start = week_start
            end = start + timedelta(days=1, hours=2)
            uid = str(uuid.uuid4())
            title = action.get("title", f"Career Action {idx + 1}")
            description = textwrap.dedent(
                f"""
                Action type: {action.get('action_type', 'N/A')}
                Difficulty: {action.get('difficulty', 'N/A')}
                Estimated time: {action.get('estimated_time', 'N/A')}
                Skills: {', '.join(action.get('matched_skills', action.get('skills_covered', [])))}
                {action.get('description', '')}
                """
            ).strip()

            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{_format_ics_datetime(now)}",
                    f"DTSTART:{_format_ics_datetime(start)}",
                    f"DTEND:{_format_ics_datetime(end)}",
                    f"SUMMARY:{_ics_escape(title)}",
                    f"DESCRIPTION:{_ics_escape(description)}",
                    "END:VEVENT",
                ]
            )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
