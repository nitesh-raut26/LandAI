"""
PDF Report Generator — provenance-stamped city land report.

Renders a branded PDF report for a given city containing:
  - Zone-level price table (🟢 Real / 🟠 Heuristic per zone)
  - Investment score summary (sub-scores + SHAP drivers)
  - Growth forecast highlights
  - Full provenance section (sources, licenses, effective dates)
  - Disclaimer

Uses reportlab (pure Python, no system libs needed) via platypus + styles.
All data is fetched from the existing backend APIs — no duplication of logic.

HUMAN GATE: For richer HTML→PDF rendering, weasyprint==62.3 (needs pango/cairo
system libs) is the upgrade path. reportlab is the zero-dependency fallback that
ships immediately.
"""
from __future__ import annotations

import io
import math
from datetime import datetime, timezone
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable, KeepTogether,
    )
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False


# ── Brand colors ──────────────────────────────────────────────────────────────
_BRAND_GREEN = (0.039, 0.588, 0.412)    # #0A9668  (emerald)
_BRAND_DARK  = (0.094, 0.118, 0.176)    # #181E2D
_ACCENT_REAL = (0.039, 0.588, 0.412)    # green — real data
_ACCENT_HEUR = (0.812, 0.459, 0.059)    # orange — heuristic
_LIGHT_GRAY  = (0.945, 0.949, 0.961)
_WHITE       = (1.0, 1.0, 1.0)


def _to_rl(rgb: tuple) -> colors.Color:
    return colors.Color(*rgb)


def _utcnow_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _fmt_price(v: int | float) -> str:
    """Format price as ₹X,XXX/sqft."""
    return f"₹{int(v):,}/sqft"


def _fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


def _data_class_badge(dc: str) -> str:
    """Text badge for data class."""
    if dc == "real":
        return "🟢 Real"
    if dc == "heuristic":
        return "🟠 Heuristic"
    return dc


def generate_city_report(
    city: dict[str, Any],
    zone_table: dict[str, Any],
    score: dict[str, Any],
) -> bytes:
    """Generate a PDF report for a city.

    Parameters
    ----------
    city       : full city record (from cities_data.py)
    zone_table : result of zone_price_index_table(city)
    score      : result of score_city(city)

    Returns
    -------
    bytes : PDF file content
    """
    if not _REPORTLAB_AVAILABLE:
        raise RuntimeError(
            "reportlab is not installed. Add reportlab>=4.2 to requirements.txt."
        )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"LandAI Report — {city['name']}",
        author="LandAI",
        subject="Land Investment Intelligence",
    )

    styles = getSampleStyleSheet()
    brand_green = _to_rl(_BRAND_GREEN)
    brand_dark  = _to_rl(_BRAND_DARK)
    light_gray  = _to_rl(_LIGHT_GRAY)

    h1 = ParagraphStyle("h1", parent=styles["Heading1"],
                         textColor=brand_dark, fontSize=20, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"],
                         textColor=brand_green, fontSize=13, spaceBefore=12, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"],
                           textColor=brand_dark, fontSize=9, leading=13)
    small = ParagraphStyle("small", parent=styles["Normal"],
                            textColor=colors.HexColor("#6B7280"), fontSize=7.5, leading=11)
    badge_real = ParagraphStyle("badge_real", parent=styles["Normal"],
                                 textColor=_to_rl(_ACCENT_REAL), fontSize=8, leading=11)
    badge_heur = ParagraphStyle("badge_heur", parent=styles["Normal"],
                                 textColor=_to_rl(_ACCENT_HEUR), fontSize=8, leading=11)

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(f"LandAI — City Intelligence Report", h1))
    story.append(Paragraph(
        f"<b>{city['name']}</b>, {city['state']} · Tier {city['tier']} · "
        f"Generated {_utcnow_str()}",
        body
    ))
    story.append(HRFlowable(width="100%", color=brand_green, thickness=2))
    story.append(Spacer(1, 0.3 * cm))

    # ── Investment Score Summary ───────────────────────────────────────────────
    story.append(Paragraph("Investment Score Summary", h2))
    composite = score.get("composite_score", 0)
    rec = score.get("recommendation", "")
    story.append(Paragraph(
        f"<b>Composite Score: {composite}/100</b>  ·  Recommendation: {rec}",
        body
    ))
    story.append(Spacer(1, 0.2 * cm))

    sub_scores = score.get("sub_scores", {})
    if sub_scores:
        ss_data = [["Sub-score", "Value", "Max"]]
        for k, v in sub_scores.items():
            try:
                display = str(round(float(v), 1))
            except (TypeError, ValueError):
                display = str(v)
            ss_data.append([k.replace("_", " ").title(), display, "100"])
        ss_table = Table(ss_data, colWidths=[8*cm, 3*cm, 3*cm])
        ss_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), brand_green),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_to_rl(_WHITE), light_gray]),
            ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ss_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Zone Price Index ──────────────────────────────────────────────────────
    story.append(Paragraph("Zone-Level Price Index", h2))

    coverage = zone_table.get("coverage", {})
    real_zones = coverage.get("real_zones", 0)
    total_zones = coverage.get("total_zones", 0)
    coverage_note = (
        f"{real_zones}/{total_zones} zones backed by real government circle-rate data. "
        f"🟢 Real = government guidance value (GODL-India). "
        f"🟠 Heuristic = distance-decay model (transparent formula)."
    )
    story.append(Paragraph(coverage_note, small))
    story.append(Spacer(1, 0.2 * cm))

    zones = zone_table.get("zones", [])
    if zones:
        tbl_data = [[
            "Zone", "Dir", "Horizon", "Current Price", "Projected Price", "CAGR", "Source"
        ]]
        for z in zones:
            dc = z.get("data_class", "heuristic")
            prov = z.get("provenance") or {}
            source_label = "🟢 " + prov.get("source", "")[:30] if dc == "real" else "🟠 Heuristic"
            if dc == "real" and prov.get("effective_date"):
                source_label += f"\n({prov['effective_date']})"
            tbl_data.append([
                z.get("label", z.get("zone_id", ""))[:22],
                z.get("direction", ""),
                f"{z.get('horizon_years', '')}yr",
                _fmt_price(z.get("current_price_inr_per_sqft", 0)),
                _fmt_price(z.get("projected_price_inr_per_sqft", 0)),
                _fmt_pct(z.get("implied_price_cagr_pct", 0)),
                source_label,
            ])

        col_widths = [4.5*cm, 1.2*cm, 1.5*cm, 3*cm, 3*cm, 1.8*cm, 4.5*cm]
        tbl = Table(tbl_data, colWidths=col_widths)

        # Build row-level colours based on data_class
        tbl_style = [
            ("BACKGROUND", (0, 0), (-1, 0), brand_green),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 7.5),
            ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]
        for i, z in enumerate(zones, start=1):
            dc = z.get("data_class", "heuristic")
            bg = _to_rl(_WHITE) if i % 2 == 0 else light_gray
            tbl_style.append(("BACKGROUND", (0, i), (-1, i), bg))
            if dc == "real":
                tbl_style.append(("TEXTCOLOR", (6, i), (6, i), _to_rl(_ACCENT_REAL)))
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)
        story.append(Spacer(1, 0.3 * cm))

    # ── Provenance Section ────────────────────────────────────────────────────
    story.append(Paragraph("Data Provenance", h2))
    story.append(Paragraph(
        "Every price figure in this report carries a data class. 🟢 Real data is sourced "
        "from government-published circle rates (ASR / guidance values) under GODL-India. "
        "🟠 Heuristic data is derived from LandAI's transparent distance-decay formula; "
        "formula parameters are documented in the model card at /api/ml/model-info.",
        body
    ))
    story.append(Spacer(1, 0.2 * cm))

    prov_data = [["Source", "License", "Data Class", "Coverage"]]
    prov_data.append([
        "Maharashtra IGR — ASR 2023-24",
        "GODL-India",
        "🟢 Real",
        "MH cities",
    ])
    prov_data.append([
        "Karnataka Kaveri — Guidance Value 2023-24",
        "GODL-India",
        "🟢 Real",
        "KA cities",
    ])
    prov_data.append([
        "Telangana IGRS — Dharani 2023-24",
        "GODL-India",
        "🟢 Real",
        "TS cities",
    ])
    prov_data.append([
        "LandAI distance-decay formula",
        "Heuristic (formula documented)",
        "🟠 Heuristic",
        "All other cities",
    ])

    prov_tbl = Table(prov_data, colWidths=[6*cm, 3.5*cm, 3*cm, 3*cm])
    prov_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand_green),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_to_rl(_WHITE), light_gray]),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(prov_tbl)
    story.append(Spacer(1, 0.5 * cm))

    # ── Disclaimer ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", color=light_gray, thickness=0.5))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "<b>Disclaimer</b>: LandAI is an analytics and research tool — not investment advice "
        "or a valuation service. Circle rates are legally mandated guidance values for "
        "stamp duty and may not reflect actual market transaction prices. Forecasts carry "
        "uncertainty; see conformal intervals at /api/ml/model-info. Always validate with "
        "local, licensed due diligence before any property decision.",
        small
    ))

    doc.build(story)
    return buf.getvalue()
