def heat_points(customers, max_points=4000):
    """[lat, lon, weight 0-1] triples for Leaflet.heat (weight = customer spend)."""
    c = customers.sample(min(len(customers), max_points), random_state=1) if len(customers) > max_points else customers
    top = max(float(c["total_spent"].quantile(0.95)), 1.0)
    return [[round(float(la), 5), round(float(lo), 5), round(min(float(s) / top, 1.0), 3)]
            for la, lo, s in zip(c["latitude"], c["longitude"], c["total_spent"])]
