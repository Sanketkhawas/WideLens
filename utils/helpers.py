import math


def inr(value, compact=True):
    """Format a number as Indian rupees (lakh / crore aware)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    v = float(value)
    if compact:
        if abs(v) >= 1e7:
            return f"₹{v / 1e7:.2f} Cr"
        if abs(v) >= 1e5:
            return f"₹{v / 1e5:.2f} L"
    return f"₹{v:,.0f}"
