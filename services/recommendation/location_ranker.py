"""Score every Nagpur locality as a site for the next store."""
import numpy as np
import pandas as pd

from services.prediction.revenue_prediction import DEFAULTS as ECON_DEFAULTS, economics
from utils.constants import DEFAULT_CATCHMENT_KM, DEFAULT_WEIGHTS, MIN_STORE_GAP_KM
from utils.geo_utils import haversine_km

FACTORS = list(DEFAULT_WEIGHTS)


def _minmax(x, invert=False):
    x = np.asarray(x, float)
    rng = x.max() - x.min()
    z = np.zeros_like(x) + 0.5 if rng == 0 else (x - x.min()) / rng
    return 1 - z if invert else z


def rank_sites(customers, areas, stores, months, weights=None, radius=DEFAULT_CATCHMENT_KM, econ=None):
    """Return a DataFrame with one row per candidate locality, sorted by score (0-100)."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    tot = sum(max(v, 0) for v in w.values()) or 1
    w = {k: max(v, 0) / tot for k, v in w.items()}
    p = {**ECON_DEFAULTS, **(econ or {})}

    clat, clon = customers["latitude"].values, customers["longitude"].values
    spend = customers["total_spent"].values
    alat, alon = areas["latitude"].values, areas["longitude"].values
    D = haversine_km(clat[:, None], clon[:, None], alat[None, :], alon[None, :])      # customers x candidates

    if len(stores):
        Ds = haversine_km(clat[:, None], clon[:, None], stores["latitude"].values[None, :], stores["longitude"].values[None, :])
        near_store = Ds.min(axis=1)
        cand_to_store = haversine_km(alat[:, None], alon[:, None], stores["latitude"].values[None, :],
                                     stores["longitude"].values[None, :]).min(axis=1)
    else:
        near_store = np.full(len(customers), 99.0)
        cand_to_store = np.full(len(areas), 99.0)
    unserved = near_store > radius                       # no store within the catchment radius

    inside = D <= radius
    n_cust = inside.sum(axis=0)
    rev = (inside * spend[:, None]).sum(axis=0)
    rev_unserved = ((inside & unserved[:, None]) * spend[:, None]).sum(axis=0)
    n_unserved = (inside & unserved[:, None]).sum(axis=0)
    avg_spend = np.where(n_cust > 0, rev / np.maximum(n_cust, 1), 0)

    df = areas.copy()
    df["catchment_customers"] = n_cust
    df["catchment_revenue"] = rev
    df["unserved_customers"] = n_unserved
    df["unserved_revenue"] = rev_unserved
    df["avg_spend"] = avg_spend
    df["dist_to_store_km"] = cand_to_store
    df["has_store"] = cand_to_store < 0.8

    f = pd.DataFrame({
        "demand": _minmax(rev), "gap": _minmax(rev_unserved), "spend": _minmax(avg_spend),
        "competition": _minmax(df["competitor_count"], invert=True), "rent": _minmax(df["avg_rent"], invert=True),
        "population": _minmax(df["population"]),
    })
    cannibal = np.where(cand_to_store < MIN_STORE_GAP_KM, 0.35 + 0.65 * cand_to_store / MIN_STORE_GAP_KM, 1.0)
    for k in FACTORS:
        df[f"f_{k}"] = f[k].values
    df["cannibal_factor"] = cannibal
    df["score"] = 100 * sum(w[k] * f[k].values for k in FACTORS) * cannibal

    m = max(months, 1)
    rows = [economics(rev_unserved[i] / m, (rev[i] - rev_unserved[i]) / m, df["avg_rent"].iat[i], p) for i in range(len(df))]
    df = pd.concat([df, pd.DataFrame(rows, index=df.index)], axis=1)

    # per-factor contribution (points of the 0-100 score) for the "why" explanation
    for k in FACTORS:
        df[f"c_{k}"] = 100 * w[k] * f[k].values * cannibal
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = np.arange(1, len(df) + 1)
    return df, w


def roadmap(customers, areas, stores, months, n=3, **kw):
    """Greedy phased plan: open the best site, treat it as a store, repeat."""
    st = stores.copy()
    picks = []
    for step in range(n):
        df, _ = rank_sites(customers, areas, st, months, **kw)
        df = df[~df["has_store"]]
        if df.empty:
            break
        ok = df[(df["monthly_profit"] > 0) & (df["payback_months"].fillna(1e9) <= 60)]
        if ok.empty:
            break          # no further site pays back within 5 years on the current assumptions
        top = ok.iloc[0]
        picks.append(top)
        st = pd.concat([st, pd.DataFrame([{"store_name": f"Proposed {step + 1}", "area": top["area"],
                                           "latitude": top["latitude"], "longitude": top["longitude"]}])], ignore_index=True)
    return picks


def robustness(df, weights, n=500, seed=11):
    """Share of random weight scenarios (Dirichlet around the chosen weights) in which each candidate
    finishes #1 / in the top 3. df must be the candidate rows only (stores excluded)."""
    rng = np.random.default_rng(seed)
    base = np.array([max(weights[k], 1e-3) for k in FACTORS])
    W = rng.dirichlet(base / base.sum() * 25, size=n)                    # n x factors
    F = df[[f"f_{k}" for k in FACTORS]].values * df["cannibal_factor"].values[:, None]
    S = W @ F.T                                                           # n x candidates
    order = (-S).argsort(axis=1)
    top1 = np.bincount(order[:, 0], minlength=len(df)) / n
    top3 = np.zeros(len(df))
    for j in range(3):
        top3 += np.bincount(order[:, j], minlength=len(df)) / n
    return top1, top3
