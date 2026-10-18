import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

LABELS = ["Champions", "Loyal", "Occasional", "At-risk"]


def segment(c, k=4, seed=7):
    """KMeans on spend / frequency / recency / ticket. Segments are named by total spend rank."""
    k = min(k, max(2, c["customer_id"].nunique() // 10))
    X = c[["total_spent", "purchase_frequency", "recency_days", "avg_ticket"]].astype(float).values
    X = np.log1p(np.clip(X, 0, None))
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(Xs)
    lab = km.labels_
    order = np.argsort([-c.loc[lab == i, "total_spent"].mean() for i in range(k)])
    names = {int(cl): (LABELS[r] if k == 4 else f"Segment {r + 1}") for r, cl in enumerate(order)}
    seg = np.array([names[int(i)] for i in lab])
    out = c.assign(segment=seg)
    summary = (out.groupby("segment").agg(customers=("customer_id", "count"), avg_spend=("total_spent", "mean"),
                                          avg_freq=("purchase_frequency", "mean"), revenue=("total_spent", "sum"),
                                          avg_recency=("recency_days", "mean")).reset_index())
    summary["share_revenue"] = summary["revenue"] / summary["revenue"].sum()
    summary["_o"] = summary["segment"].map({n: i for i, n in enumerate(LABELS)}).fillna(9)
    return out, summary.sort_values("_o").drop(columns="_o")
