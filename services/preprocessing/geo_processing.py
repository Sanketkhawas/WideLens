import numpy as np
import pandas as pd

from utils.geo_utils import haversine_km


def nearest_area(lat, lon, areas):
    """Return the name of the closest locality centroid for each (lat, lon)."""
    d = haversine_km(np.asarray(lat)[:, None], np.asarray(lon)[:, None],
                     areas["latitude"].values[None, :], areas["longitude"].values[None, :])
    return areas["area"].values[d.argmin(axis=1)], d.min(axis=1)


def fill_geo(customers, areas):
    """Fill missing coordinates from the area centroid and missing area from coordinates."""
    c = customers.copy()
    cent = areas.set_index("area")[["latitude", "longitude"]]
    miss_ll = c["latitude"].isna() | c["longitude"].isna()
    known = c["area"].isin(cent.index)
    fix = miss_ll & known
    c.loc[fix, "latitude"] = c.loc[fix, "area"].map(cent["latitude"])
    c.loc[fix, "longitude"] = c.loc[fix, "area"].map(cent["longitude"])
    miss_area = ~known & c["latitude"].notna()
    if miss_area.any():
        names, _ = nearest_area(c.loc[miss_area, "latitude"].values, c.loc[miss_area, "longitude"].values, areas)
        c.loc[miss_area, "area"] = names
    return c
