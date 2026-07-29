from __future__ import annotations

from typing import Any


def build_pdf_bytes(report: dict[str, Any]) -> bytes:
    """Render a candidate report to PDF bytes using reportlab.

    Raises ``ImportError`` when reportlab is unavailable so the caller can
    fall back to a JSON report.
    """
    from io import BytesIO

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - inch

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(inch, y, "HireMind Candidate Report")
    y -= 0.4 * inch

    pdf.setFont("Helvetica", 11)
    lines = [
        f"Name: {report.get('candidate_name', '')}",
        f"Email: {report.get('candidate_email', '')}",
        f"Job: {report.get('job_title') or 'N/A'}",
        f"Status: {report.get('application_status', '')}",
        f"Applied: {report.get('applied_at', '')}",
        f"Skills: {', '.join(report.get('skills', []) or []) or 'N/A'}",
        f"Experience (years): {report.get('experience_years') or 'N/A'}",
        f"College: {report.get('college') or 'N/A'}",
        f"Interview status: {report.get('interview_status') or 'N/A'}",
        f"Interview score: {report.get('interview_score') or 'N/A'}",
    ]
    for line in lines:
        pdf.drawString(inch, y, line)
        y -= 0.25 * inch

    summary = report.get("evaluation_summary")
    if summary:
        y -= 0.2 * inch
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(inch, y, "Evaluation Summary")
        y -= 0.25 * inch
        pdf.setFont("Helvetica", 10)
        for chunk in _wrap(summary, 90):
            pdf.drawString(inch, y, chunk)
            y -= 0.2 * inch

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = f"{current} {word}".strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
