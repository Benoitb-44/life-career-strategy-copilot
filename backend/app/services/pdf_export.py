from __future__ import annotations

from io import BytesIO

from app.models import ChecklistResult


def _as_bulleted_lines(items: list[str]) -> str:
    if not items:
        return "-"
    return "<br/>".join(f"• {item}" for item in items)


def generate_plan_pdf(plan_json: dict, checklist_result: ChecklistResult | None) -> bytes:
    """Generate a decision-grade 90-day strategy PDF from plan JSON + checklist result."""

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="90-Day Career Strategy – Decision-Grade Plan",
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story: list = [
        Paragraph("90-Day Career Strategy – Decision-Grade Plan", title_style),
        Spacer(1, 0.35 * cm),
        Paragraph(f"<b>Objective:</b> {plan_json.get('objective', '-')}", body_style),
        Spacer(1, 0.35 * cm),
    ]

    story.append(Paragraph("Monthly Objectives", heading_style))
    monthly_objectives = plan_json.get("monthly_objectives", [])
    if not monthly_objectives:
        story.append(Paragraph("No monthly objectives provided.", body_style))
    else:
        for month_data in monthly_objectives:
            month_number = month_data.get("month", "?")
            month_objective = month_data.get("objective", "-")
            deliverables = month_data.get("deliverables", [])
            story.append(
                Paragraph(
                    f"<b>Month {month_number}</b> — {month_objective}<br/>{_as_bulleted_lines(deliverables)}",
                    body_style,
                )
            )
            story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("KPIs", heading_style))
    story.append(Paragraph(_as_bulleted_lines(plan_json.get("kpis", [])), body_style))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Risks", heading_style))
    story.append(Paragraph(_as_bulleted_lines(plan_json.get("risks", [])), body_style))

    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph("Checklist Evaluation", heading_style))
    if checklist_result is None:
        story.append(Paragraph("No checklist result available.", body_style))
    else:
        checks = {
            "Clarity": checklist_result.clarity,
            "Focus": checklist_result.focus,
            "Actionability": checklist_result.actionability,
            "Feasibility": checklist_result.feasibility,
            "Risk awareness": checklist_result.risk_awareness,
            "Coherence": checklist_result.coherence,
        }
        for label, value in checks.items():
            story.append(Paragraph(f"• {label}: {'OK' if value else 'KO'}", body_style))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"<b>Verdict:</b> {checklist_result.verdict}", body_style))
        story.append(Paragraph(f"<b>Feedback:</b> {checklist_result.feedback}", body_style))

    document.build(story)
    return buffer.getvalue()
