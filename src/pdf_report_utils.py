"""PDF career report generation using ReportLab."""

from __future__ import annotations

from io import BytesIO


def generate_career_pdf_report(
    title: str,
    sections: list[tuple[str, str]],
) -> bytes:
    """Generate a simple PDF report from titled sections."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:
        raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    for heading, body in sections:
        safe_heading = heading.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_body = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
        story.append(Paragraph(safe_heading, styles["Heading2"]))
        story.append(Paragraph(safe_body, styles["BodyText"]))
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    return buffer.getvalue()


def build_gap_pdf_sections(
    target_role: str,
    match_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
    recommendations: str = "",
) -> list[tuple[str, str]]:
    """Build PDF sections from gap analysis results."""
    sections = [
        ("Overview", f"Target Role: {target_role}\nMatch Score: {match_score:.2f}%"),
        ("Matched Skills", "\n".join(f"- {s}" for s in matched_skills) or "None"),
        ("Missing Skills", "\n".join(f"- {s}" for s in missing_skills) or "None"),
    ]
    if recommendations:
        sections.append(("Recommendations", recommendations))
    sections.append(("Disclaimer", "This report is rule-based guidance, not a hiring decision."))
    return sections
