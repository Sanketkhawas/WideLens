import io

from services.recommendation.recommendation_engine import ranking_payload
from services.reports.pdf_generator import build_pdf
from services.visualization import charts


def build_report(a, **params):
    payload = ranking_payload(a, **params)
    recs = payload["recommendations"]
    ch = {"scores": charts.site_scores(recs), "map": charts.map_png(a.customers, a.stores, recs),
          "areas": charts.area_bars({"labels": list(a.area_tbl.head(12)["area"]), "revenue": list(a.area_tbl.head(12)["revenue"])})}
    if a.forecast:
        ch["forecast"] = charts.revenue_forecast(a.forecast)
    buf = io.BytesIO()
    build_pdf(buf, "WideLens - Store Expansion Report: Nagpur, Maharashtra", a.kpis, payload, ch, a.filename)
    buf.seek(0)
    return buf
