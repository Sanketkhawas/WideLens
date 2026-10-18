"""Read a customer workbook (xlsx / csv), validate, clean and normalise it."""
import re

import numpy as np
import pandas as pd

from services.preprocessing.geo_processing import fill_geo, nearest_area
from utils.constants import NAGPUR_AREAS

ALIASES = {
    "customer_id": ["customer_id", "customerid", "cust_id", "id", "customer id"],
    "customer_name": ["customer_name", "name", "customer", "customer name"],
    "age": ["age"],
    "gender": ["gender", "sex"],
    "area": ["area", "locality", "neighbourhood", "neighborhood", "location", "ward"],
    "city": ["city", "town"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "lng", "long"],
    "purchase_frequency": ["purchase_frequency", "frequency", "orders", "no_of_purchases", "visits", "purchase frequency"],
    "total_spent": ["total_spent", "total_spend", "spend", "revenue", "amount", "total spent", "lifetime_value"],
}
SALES_ALIASES = {
    "sale_id": ["sale_id", "id", "order_id", "invoice"],
    "customer_id": ALIASES["customer_id"],
    "product": ["product", "category", "item", "product_category"],
    "quantity": ["quantity", "qty"],
    "amount": ["amount", "total", "sale_amount", "value", "price"],
    "sale_date": ["sale_date", "date", "order_date", "purchase_date"],
    "payment_method": ["payment_method", "payment", "mode"],
}
STORE_ALIASES = {
    "store_name": ["store_name", "name", "store"],
    "area": ALIASES["area"],
    "latitude": ALIASES["latitude"],
    "longitude": ALIASES["longitude"],
}
AREA_ALIASES = {
    "area": ALIASES["area"],
    "latitude": ALIASES["latitude"],
    "longitude": ALIASES["longitude"],
    "population": ["population", "pop"],
    "avg_rent": ["avg_rent", "rent", "average_rent", "rent_per_sqft"],
    "competitor_count": ["competitor_count", "competitors", "rivals"],
}


class DataError(ValueError):
    """Raised with a user-friendly message when the upload cannot be used."""


def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).strip().lower()).strip("_")


def _rename(df, aliases):
    lookup = {}
    for target, names in aliases.items():
        for n in names:
            lookup[_norm(n)] = target
    df = df.rename(columns={c: lookup.get(_norm(c), _norm(c)) for c in df.columns})
    return df.loc[:, ~df.columns.duplicated()]


def _canon_area(series, valid):
    """Case/space-insensitive match to known area names."""
    m = {a.lower(): a for a in valid}
    s = series.fillna("").astype(str).str.strip()
    return s.str.lower().map(m).fillna(s.where(s != "", None))


def read_workbook(path):
    """Return dict of raw DataFrames keyed customers / sales / stores / areas."""
    if str(path).lower().endswith(".csv"):
        return {"customers": pd.read_csv(path)}
    try:
        sheets = pd.read_excel(path, sheet_name=None)
    except Exception as e:  # noqa: BLE001
        raise DataError(f"Could not read the Excel file: {e}") from e
    by_name = {_norm(k): v for k, v in sheets.items()}
    cust = by_name.get("customers", by_name.get("customer"))
    if cust is None:
        # fall back to the first sheet that looks like customers
        for v in sheets.values():
            if {"total_spent", "latitude", "area"} & set(_rename(v, ALIASES).columns):
                cust = v
                break
    if cust is None:
        raise DataError("No 'Customers' sheet found. Add a sheet named Customers (see the template).")
    return {"customers": cust, "sales": by_name.get("sales"), "stores": by_name.get("stores"), "areas": by_name.get("areas")}


def clean(raw):
    """Clean the raw workbook. Returns (data dict, list of human-readable notes)."""
    notes = []
    base_areas = pd.DataFrame(NAGPUR_AREAS, columns=["area", "latitude", "longitude", "population", "avg_rent", "competitor_count"])

    # ---- areas (optional override)
    areas = base_areas.copy()
    if raw.get("areas") is not None and len(raw["areas"]):
        a = _rename(raw["areas"], AREA_ALIASES)
        if "area" in a.columns:
            a["area"] = a["area"].astype(str).str.strip()
            a = a.set_index("area")
            b = areas.set_index("area")
            for c in b.columns:
                if c in a.columns:
                    b.loc[a.index.intersection(b.index), c] = a.loc[a.index.intersection(b.index), c]
            new = a.index.difference(b.index)
            if len(new):
                add = a.loc[new].reindex(columns=b.columns)
                b = pd.concat([b, add])
            areas = b.reset_index()
            notes.append(f"Applied locality overrides from your 'Areas' sheet ({len(a)} rows).")
    for c, default in (("population", areas["population"].median()), ("avg_rent", areas["avg_rent"].median()),
                       ("competitor_count", areas["competitor_count"].median())):
        areas[c] = pd.to_numeric(areas[c], errors="coerce").fillna(default)
    areas = areas.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

    # ---- customers
    c = _rename(raw["customers"], ALIASES)
    missing = [k for k in ("customer_id", "total_spent") if k not in c.columns]
    if missing:
        raise DataError("Customers sheet is missing required column(s): " + ", ".join(missing))
    n0 = len(c)
    c["customer_id"] = c["customer_id"].astype(str).str.strip()
    c = c.drop_duplicates("customer_id")
    if n0 - len(c):
        notes.append(f"Removed {n0 - len(c)} duplicate customer rows.")
    for col in ("age", "latitude", "longitude", "purchase_frequency", "total_spent"):
        c[col] = pd.to_numeric(c.get(col), errors="coerce") if col in c.columns else np.nan
    for col, default in (("customer_name", ""), ("gender", "Unknown"), ("city", "Nagpur"), ("area", None)):
        if col not in c.columns:
            c[col] = default
    c["gender"] = c["gender"].fillna("Unknown").astype(str).str.strip().str.title().replace({"M": "Male", "F": "Female"})
    c["area"] = _canon_area(c["area"], areas["area"])
    c["total_spent"] = c["total_spent"].fillna(0).clip(lower=0)
    c["purchase_frequency"] = c["purchase_frequency"].fillna(1).clip(lower=0)
    med_age = c["age"].median() if c["age"].notna().any() else 35
    n_age = int(c["age"].isna().sum() + ((c["age"] < 10) | (c["age"] > 100)).sum())
    c.loc[(c["age"] < 10) | (c["age"] > 100), "age"] = np.nan
    c["age"] = c["age"].fillna(med_age).round().astype(int)
    if n_age:
        notes.append(f"Filled {n_age} missing/invalid ages with the median ({int(med_age)}).")

    before_ll = int((c["latitude"].isna() | c["longitude"].isna()).sum())
    before_area = int((~c["area"].isin(areas["area"])).sum())
    c = fill_geo(c, areas)
    still = c["latitude"].isna() | c["longitude"].isna()
    if still.any():
        notes.append(f"Dropped {int(still.sum())} customers with no usable location.")
        c = c[~still]
    # keep only coordinates plausibly inside the Nagpur region (~60 km)
    from utils.geo_utils import haversine_km
    from utils.constants import CITY_CENTER
    far = haversine_km(c["latitude"], c["longitude"], CITY_CENTER[0], CITY_CENTER[1]) > 60
    if far.any():
        notes.append(f"Dropped {int(far.sum())} customers located more than 60 km from Nagpur.")
        c = c[~far]
    if before_ll:
        notes.append(f"Filled {before_ll} missing coordinates from their locality.")
    if before_area:
        notes.append(f"Fixed/inferred {before_area} blank or mis-typed locality names.")
    if not len(c):
        raise DataError("No valid customer rows after cleaning.")
    c = c.reset_index(drop=True)

    # ---- sales (optional)
    sales = None
    if raw.get("sales") is not None and len(raw["sales"]):
        s = _rename(raw["sales"], SALES_ALIASES)
        if {"customer_id", "amount", "sale_date"} <= set(s.columns):
            s["customer_id"] = s["customer_id"].astype(str).str.strip()
            s["amount"] = pd.to_numeric(s["amount"], errors="coerce")
            s["sale_date"] = pd.to_datetime(s["sale_date"], errors="coerce")
            if "product" not in s.columns:
                s["product"] = "General"
            if "payment_method" not in s.columns:
                s["payment_method"] = "Unknown"
            s = s.dropna(subset=["amount", "sale_date"])
            s = s[s["customer_id"].isin(c["customer_id"])]
            sales = s.reset_index(drop=True)
            notes.append(f"Loaded {len(sales):,} sales transactions.")
        else:
            notes.append("Sales sheet ignored (needs customer_id, amount, sale_date).")
    if sales is None:
        notes.append("No usable Sales sheet - revenue trend and forecast are skipped.")

    # ---- existing stores
    stores = pd.DataFrame(columns=["store_name", "area", "latitude", "longitude"])
    if raw.get("stores") is not None and len(raw["stores"]):
        st = _rename(raw["stores"], STORE_ALIASES)
        if "store_name" not in st.columns:
            st["store_name"] = [f"Store {i + 1}" for i in range(len(st))]
        if "area" in st.columns:
            st["area"] = _canon_area(st["area"], areas["area"])
        cent = areas.set_index("area")
        for col in ("latitude", "longitude"):
            if col not in st.columns:
                st[col] = np.nan
            st[col] = pd.to_numeric(st[col], errors="coerce")
            if "area" in st.columns:
                st[col] = st[col].fillna(st["area"].map(cent[col]))
        stores = st.dropna(subset=["latitude", "longitude"])[["store_name", "area", "latitude", "longitude"]].reset_index(drop=True)
        if len(stores):
            if stores["area"].isna().any():
                names, _ = nearest_area(stores["latitude"].values, stores["longitude"].values, areas)
                stores["area"] = stores["area"].fillna(pd.Series(names, index=stores.index))
            notes.append(f"{len(stores)} existing store(s) loaded.")
    if not len(stores):
        notes.append("No existing stores given - every locality is treated as unserved.")
    return {"customers": c, "sales": sales, "stores": stores, "areas": areas}, notes
