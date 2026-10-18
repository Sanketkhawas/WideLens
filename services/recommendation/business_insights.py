from utils.constants import FACTOR_LABELS
from utils.helpers import inr


def why(row, top_n=3):
    """Top contributing factors for a candidate row (dict-like)."""
    contrib = sorted(((k, row[f"c_{k}"]) for k in FACTOR_LABELS), key=lambda kv: -kv[1])[:top_n]
    return [{"factor": k, "label": FACTOR_LABELS[k], "points": round(float(v), 1)} for k, v in contrib]


def narrative(best, k, area_tbl, stores, radius, seg_summary, fc, cat_tbl):
    """Plain-language findings for the dashboard / PDF."""
    out = []
    n = k["customers"]
    unserved_share = best["unserved_customers"] / max(n, 1)
    out.append(
        f"**{best['area']}** is the strongest site for the next store (score {best['score']:.0f}/100). "
        f"{int(best['catchment_customers']):,} of your customers live within {radius:g} km of it, and "
        f"{int(best['unserved_customers']):,} of them ({unserved_share:.0%} of all customers) are not within {radius:g} km of any existing store."
    )
    reasons = ", ".join(f"{r['label'].lower()}" for r in why(best))
    out.append(f"The biggest drivers are {reasons}.")
    if best["payback_months"]:
        out.append(
            f"Planning estimate: about {inr(best['monthly_revenue'])}/month revenue against {inr(best['monthly_rent'])}/month rent "
            f"(rent is {best['occupancy_ratio']:.0%} of sales); payback ≈ {best['payback_months']:.0f} months on the stated assumptions."
        )
    else:
        out.append("On the current assumptions this site does not reach a monthly profit - adjust the assumptions or pick a cheaper area.")
    if len(stores):
        names = ", ".join(stores["area"].astype(str))
        top2 = area_tbl.head(3)
        out.append(f"Your existing stores are in {names}, but the highest-spending localities are {', '.join(top2['area'])} - demand is concentrated where you are not.")
    if seg_summary is not None and len(seg_summary):
        ch = seg_summary.iloc[0]
        out.append(f"{ch['segment']} customers are {ch['customers'] / n:.0%} of the base but bring {ch['share_revenue']:.0%} of revenue - prioritise sites close to them.")
    if fc:
        out.append(f"Revenue trend is {'up' if fc['monthly_growth_pct'] > 0 else 'down'} ≈ {abs(fc['monthly_growth_pct']):.1f}% per month; the forecast peaks in {fc['peak_month']} - aim to open before the festive season.")
    if cat_tbl is not None and len(cat_tbl):
        out.append(f"Top category is {cat_tbl.index[0]} ({cat_tbl['revenue'].iloc[0] / cat_tbl['revenue'].sum():.0%} of sales) - plan the store's range and floor space around it.")
    return out
