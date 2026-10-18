import numpy as np
import pandas as pd


def age_band(a):
    return pd.cut(a, [0, 24, 34, 44, 54, 200], labels=["18-24", "25-34", "35-44", "45-54", "55+"])


def kpis(c, sales):
    d = {
        "customers": int(len(c)),
        "revenue": float(c["total_spent"].sum()),
        "avg_spend": float(c["total_spent"].mean()),
        "avg_frequency": float(c["purchase_frequency"].mean()),
        "avg_age": float(c["age"].mean()),
        "transactions": int(c["purchase_frequency"].sum()),
        "areas_covered": int(c["area"].nunique()),
    }
    if sales is not None and len(sales):
        d["period_from"] = sales["sale_date"].min().strftime("%b %Y")
        d["period_to"] = sales["sale_date"].max().strftime("%b %Y")
    return d


def demographics(c):
    ab = age_band(c["age"]).value_counts().reindex(["18-24", "25-34", "35-44", "45-54", "55+"]).fillna(0)
    g = c["gender"].value_counts()
    return {"age_labels": list(ab.index), "age_values": [int(v) for v in ab.values],
            "gender_labels": list(g.index), "gender_values": [int(v) for v in g.values]}


def area_table(c):
    g = c.groupby("area").agg(customers=("customer_id", "count"), revenue=("total_spent", "sum"),
                              avg_spend=("total_spent", "mean"), avg_freq=("purchase_frequency", "mean"),
                              lat=("latitude", "mean"), lon=("longitude", "mean")).reset_index()
    return g.sort_values("revenue", ascending=False)
