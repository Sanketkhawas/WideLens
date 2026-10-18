import numpy as np
import pandas as pd


def add_customer_features(customers, sales):
    """Add recency / ticket-size features used for segmentation."""
    c = customers.copy()
    c["avg_ticket"] = (c["total_spent"] / c["purchase_frequency"].replace(0, np.nan)).fillna(0)
    if sales is not None and len(sales):
        last = sales.groupby("customer_id")["sale_date"].max()
        ref = sales["sale_date"].max()
        c["recency_days"] = (ref - c["customer_id"].map(last)).dt.days
        c["recency_days"] = c["recency_days"].fillna(c["recency_days"].max() if c["recency_days"].notna().any() else 365)
    else:
        c["recency_days"] = 0
    return c
