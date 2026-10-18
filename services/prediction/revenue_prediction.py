"""Store-level economics for a candidate site. All inputs are explicit assumptions, shown in the UI."""
from utils.constants import DEFAULT_CAPTURE_RATE

DEFAULTS = {
    "capture_rate": DEFAULT_CAPTURE_RATE,  # share of catchment spend a new store wins
    "coverage": 0.15,        # share of real-world sales that the uploaded customer file represents
    "contribution": 0.22,    # contribution margin on sales, before rent
    "sqft": 1000,
    "fitout_per_sqft": 1200,  # Rs, one-off
    "deposit_months": 6,      # rent deposit, one-off
    "shift_factor": 0.5,      # how much of a served customer's spend moves to the new store
}


def economics(unserved_monthly, served_monthly, rent_psf, p):
    """Monthly revenue / profit / payback for one candidate.

    unserved_monthly: monthly spend (in the file) of catchment customers with no store nearby.
    served_monthly:   monthly spend of catchment customers already near an existing store.
    """
    scale = 1.0 / max(p["coverage"], 1e-6)
    new_rev = p["capture_rate"] * unserved_monthly * scale
    shifted = p["capture_rate"] * p["shift_factor"] * served_monthly * scale  # taken from existing stores
    revenue = new_rev + shifted
    rent = rent_psf * p["sqft"]
    profit = revenue * p["contribution"] - rent
    capex = p["sqft"] * p["fitout_per_sqft"] + rent * p["deposit_months"]
    return {
        "monthly_revenue": revenue, "incremental_revenue": new_rev, "cannibalised_revenue": shifted,
        "monthly_rent": rent, "monthly_profit": profit, "capex": capex,
        "payback_months": (capex / profit) if profit > 0 else None,
        "occupancy_ratio": (rent / revenue) if revenue > 0 else None,
    }
