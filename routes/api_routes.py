from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user, login_required

from routes.upload_routes import original_name, user_file
from services.recommendation import recommendation_engine as engine
from services.reports.report_builder import build_report

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _analysis():
    path = user_file(current_user.id)
    if not path:
        return None
    a = engine.load(path)
    a.filename = original_name(current_user.id, a.filename)
    return a


def _num(d, k, lo, hi, default):
    try:
        return min(hi, max(lo, float(d.get(k, default))))
    except (TypeError, ValueError):
        return default


def _params(d):
    w = d.get("weights") or {}
    e = d.get("econ") or {}
    weights = {k: _num(w, k, 0, 100, 0) for k in w} if w else None
    econ = {
        "capture_rate": _num(e, "capture_rate", 0.01, 1, 0.2), "coverage": _num(e, "coverage", 0.01, 1, 0.15),
        "contribution": _num(e, "contribution", 0.01, 0.9, 0.22), "sqft": _num(e, "sqft", 100, 20000, 1000),
        "fitout_per_sqft": _num(e, "fitout_per_sqft", 0, 20000, 1200), "deposit_months": _num(e, "deposit_months", 0, 36, 6),
    } if e else None
    return {"weights": weights, "radius": _num(d, "radius", 0.5, 10, 3.0), "econ": econ}


@api_bp.route("/analysis")
@login_required
def analysis():
    a = _analysis()
    if a is None:
        return jsonify(error="No data uploaded"), 404
    return jsonify(engine.static_payload(a))


@api_bp.route("/rank", methods=["POST"])
@login_required
def rank():
    a = _analysis()
    if a is None:
        return jsonify(error="No data uploaded"), 404
    return jsonify(engine.ranking_payload(a, **_params(request.get_json(silent=True) or {})))


@api_bp.route("/report.pdf", methods=["GET", "POST"])
@login_required
def report():
    a = _analysis()
    if a is None:
        return jsonify(error="No data uploaded"), 404
    d = request.get_json(silent=True) or {}
    buf = build_report(a, **_params(d))
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="WideLens_Nagpur_Expansion_Report.pdf")
