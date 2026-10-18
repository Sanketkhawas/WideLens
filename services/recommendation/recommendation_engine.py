"""Orchestrates the pipeline: Excel -> clean -> analytics -> forecast -> site ranking."""
import os

import numpy as np
import pandas as pd

from services.analytics import customer_statistics as cs
from services.analytics import sales_analysis as sa
from services.analytics.customer_segmentation import segment
from services.prediction.revenue_prediction import DEFAULTS as ECON_DEFAULTS
from services.prediction.sales_prediction import forecast
from services.preprocessing.data_cleaner import clean, read_workbook
from services.preprocessing.feature_engineering import add_customer_features
from services.recommendation.business_insights import narrative, why
from services.recommendation.location_ranker import FACTORS, rank_sites, roadmap, robustness
from services.visualization.heatmap import heat_points
from utils.constants import DEFAULT_CATCHMENT_KM, DEFAULT_WEIGHTS, FACTOR_LABELS

_CACHE = {}


class Analysis:
    pass


def load(path):
    """Parse + analyse an uploaded workbook (cached by path and modified-time)."""
    key = (path, os.path.getmtime(path))
    if key in _CACHE:
        return _CACHE[key]
    raw = read_workbook(path)
    data, notes = clean(raw)
    a = Analysis()
    a.filename = os.path.basename(path)
    a.notes = notes
    a.areas, a.stores, a.sales = data["areas"], data["stores"], data["sales"]
    c = add_customer_features(data["customers"], a.sales)
    a.customers, a.seg_summary = segment(c)
    a.kpis = cs.kpis(a.customers, a.sales)
    a.demo = cs.demographics(a.customers)
    a.area_tbl = cs.area_table(a.customers)
    if a.sales is not None and len(a.sales):
        a.monthly = sa.monthly(a.sales)
        a.cat, a.pay = sa.by_category(a.sales), sa.by_payment(a.sales)
        a.forecast = forecast(a.monthly["revenue"])
        a.months = max(1, int(round((a.sales["sale_date"].max() - a.sales["sale_date"].min()).days / 30.44)))
    else:
        a.monthly = a.cat = a.pay = a.forecast = None
        a.months = 12
    _CACHE.clear()
    _CACHE[key] = a
    return a


def _py(o):
    if isinstance(o, dict):
        return {k: _py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_py(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if (isinstance(o, float) and np.isnan(o)) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def static_payload(a):
    k = _py(a.kpis)
    seg = a.seg_summary
    area = a.area_tbl.head(12)
    d = {
        "filename": a.filename, "notes": a.notes, "kpis": k, "demo": a.demo,
        "areas": {"labels": list(area["area"]), "customers": [int(v) for v in area["customers"]],
                  "revenue": [round(float(v)) for v in area["revenue"]],
                  "avg_spend": [round(float(v)) for v in area["avg_spend"]]},
        "segments": {"labels": list(seg["segment"]), "customers": [int(v) for v in seg["customers"]],
                     "revenue": [round(float(v)) for v in seg["revenue"]],
                     "avg_spend": [round(float(v)) for v in seg["avg_spend"]],
                     "avg_freq": [round(float(v), 1) for v in seg["avg_freq"]]},
        "stores": a.stores.to_dict("records"),
        "heat": heat_points(a.customers),
        "forecast": a.forecast,
        "monthly": None if a.monthly is None else {"labels": [d.strftime("%b %y") for d in a.monthly.index],
                                                   "revenue": [round(float(v)) for v in a.monthly["revenue"]],
                                                   "orders": [int(v) for v in a.monthly["orders"]]},
        "categories": None if a.cat is None else {"labels": list(a.cat.index), "revenue": [round(float(v)) for v in a.cat["revenue"]]},
        "payments": None if a.pay is None else {"labels": list(a.pay.index), "values": [round(float(v)) for v in a.pay.values]},
        "defaults": {"weights": DEFAULT_WEIGHTS, "radius": DEFAULT_CATCHMENT_KM, "econ": ECON_DEFAULTS},
        "factor_labels": FACTOR_LABELS,
    }
    return _py(d)


def ranking_payload(a, weights=None, radius=DEFAULT_CATCHMENT_KM, econ=None, top=12):
    df, w = rank_sites(a.customers, a.areas, a.stores, a.months, weights, radius, econ)
    cand = df[~df["has_store"]].reset_index(drop=True)
    cand["robust_top1"], cand["robust_top3"] = robustness(cand, w)
    cols = ["rank", "area", "latitude", "longitude", "score", "catchment_customers", "catchment_revenue", "unserved_customers",
            "unserved_revenue", "avg_spend", "avg_rent", "competitor_count", "population", "dist_to_store_km",
            "monthly_revenue", "incremental_revenue", "cannibalised_revenue", "monthly_rent", "monthly_profit", "capex",
            "payback_months", "occupancy_ratio", "cannibal_factor", "robust_top1", "robust_top3"] + [f"f_{k}" for k in FACTORS] + [f"c_{k}" for k in FACTORS]
    recs = []
    for i, (_, r) in enumerate(cand.head(top).iterrows(), 1):
        d = r[cols].to_dict()
        d["rank"] = i
        d["why"] = why(r)
        if d["payback_months"] and d["payback_months"] > 120:
            d["payback_months"] = None
        recs.append(d)
    picks = roadmap(a.customers, a.areas, a.stores, a.months, n=3, weights=weights, radius=radius, econ=econ)
    road = [{"step": i + 1, "area": p["area"], "latitude": p["latitude"], "longitude": p["longitude"], "score": p["score"],
             "monthly_revenue": p["monthly_revenue"], "payback_months": p["payback_months"],
             "monthly_profit": p["monthly_profit"], "unserved_customers": p["unserved_customers"]} for i, p in enumerate(picks)]
    seg_summary = a.seg_summary
    story = narrative(cand.iloc[0], a.kpis, a.area_tbl, a.stores, radius, seg_summary, a.forecast, a.cat) if len(cand) else []
    # coverage: customers with no store within radius
    from utils.geo_utils import haversine_km
    if len(a.stores):
        ns = haversine_km(a.customers["latitude"].values[:, None], a.customers["longitude"].values[:, None],
                          a.stores["latitude"].values[None, :], a.stores["longitude"].values[None, :]).min(axis=1)
        un = ns > radius
    else:
        un = np.ones(len(a.customers), bool)
    cov = {"unserved_customers": int(un.sum()), "unserved_share": float(un.mean()),
           "unserved_revenue_share": float(a.customers.loc[un, "total_spent"].sum() / max(a.customers["total_spent"].sum(), 1))}
    all_areas = df[["area", "score", "has_store"]].to_dict("records")
    road_note = None
    if len(picks) < 3:
        road_note = (f"Only {len(picks)} site(s) pay back within 5 years once earlier picks are counted as stores - "
                     "a further store needs lower rent, a higher capture rate or more customers in the file.")
    return _py({"roadmap_note": road_note, "weights": w, "radius": radius, "recommendations": recs, "roadmap": road, "insights": story,
                "coverage": cov, "all_scores": all_areas})
