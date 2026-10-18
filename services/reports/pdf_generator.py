from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.helpers import inr


def _rs(x):
    return x.replace("₹", "Rs ") if isinstance(x, str) else x


def build_pdf(out, title, k, payload, charts, filename):
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=colors.HexColor("#1D4ED8"), fontSize=22)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=colors.HexColor("#111827"), spaceBefore=10)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=14)
    small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.HexColor("#6B7280"))
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                            title=title)
    P = lambda t, st: Paragraph(_rs(t), st)  # noqa: E731
    S = [Paragraph(title, h1), Paragraph(f"Source file: {filename}", small), Spacer(1, 8)]
    kp = [["Customers", "Revenue (file)", "Avg spend", "Localities"],
          [f"{k['customers']:,}", inr(k["revenue"]), inr(k["avg_spend"], False), str(k["areas_covered"])]]
    kp = [[_rs(x) for x in r] for r in kp]
    t = Table(kp, colWidths=[4.2 * cm] * 4)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")), ("FONTSIZE", (0, 0), (-1, 0), 8),
                           ("FONTSIZE", (0, 1), (-1, 1), 13), ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                           ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    S += [t, Paragraph("Key findings", h2)]
    for line in payload["insights"]:
        S.append(P("• " + line.replace("**", "<b>", 1).replace("**", "</b>", 1), body))
    S += [Paragraph("Where to open the next store", h2), Image(charts["scores"], width=15 * cm, height=7.7 * cm)]
    rows = [["#", "Locality", "Score", "Customers\nin catchment", "Unserved", "Rent\n₹/sqft", "Est. revenue\n/month", "Payback"]]
    for r in payload["recommendations"][:8]:
        rows.append([r["rank"], r["area"], f"{r['score']:.0f}", f"{int(r['catchment_customers']):,}", f"{int(r['unserved_customers']):,}",
                     f"{r['avg_rent']:.0f}", inr(r["monthly_revenue"]),
                     f"{r['payback_months']:.0f} mo" if r["payback_months"] else "n/a"])
    rows = [[_rs(x) for x in r] for r in rows]
    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
                           ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ECFDF5")), ("ALIGN", (2, 0), (-1, -1), "CENTER")]))
    S += [Spacer(1, 6), KeepTogether([t]), KeepTogether([Paragraph("Customer & store map", h2), Image(charts["map"], width=12 * cm, height=9.7 * cm)])]
    if payload.get("roadmap"):
        S.append(Paragraph("Phased roadmap: " + " → ".join(f"{p['step']}. {p['area']}" for p in payload["roadmap"]), body))
    S.append(PageBreak())
    S += [Paragraph("Revenue by locality", h2), Image(charts["areas"], width=15 * cm, height=6.8 * cm)]
    if charts.get("forecast"):
        S += [Paragraph("Revenue forecast", h2), Image(charts["forecast"], width=15 * cm, height=6.8 * cm)]
    S.append(Paragraph("Method & assumptions: sites are scored on nearby demand, demand not served by existing stores, spend per customer, "
                       "competition, rent and population (weights adjustable in the app). Revenue/payback figures are planning estimates built "
                       "on stated assumptions (capture rate, file coverage, margin, store size); locality population, rent and competitor "
                       "counts are illustrative unless supplied in the Areas sheet. Validate on the ground before committing capital.", small))
    doc.build(S)
