"""Revenue forecast: linear trend x month-of-year seasonality (multiplicative)."""
import numpy as np
import pandas as pd


def forecast(monthly_revenue, horizon=6):
    s = monthly_revenue.astype(float)
    # drop a partial trailing month
    if len(s) > 3 and s.iloc[-1] < 0.5 * s.iloc[-4:-1].mean():
        s = s.iloc[:-1]
    n = len(s)
    if n < 6:
        return None
    t = np.arange(n)
    slope, icpt = np.polyfit(t, s.values, 1)
    trend = icpt + slope * t
    ratio = s.values / np.where(trend <= 0, np.nan, trend)
    months = s.index.month
    seas = pd.Series(ratio, index=months).groupby(level=0).mean()
    seas = (seas / seas.mean()).reindex(range(1, 13)).fillna(1.0)
    fitted = trend * seas.reindex(months).values
    resid = s.values - fitted
    sd = float(np.std(resid, ddof=1)) if n > 2 else 0.0
    mape = float(np.mean(np.abs(resid) / s.values) * 100)
    fidx = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    tf = np.arange(n, n + horizon)
    pred = (icpt + slope * tf) * seas.reindex(fidx.month).values
    return {
        "hist_labels": [d.strftime("%b %y") for d in s.index], "hist": [round(float(v)) for v in s.values],
        "fitted": [round(float(v)) for v in fitted],
        "f_labels": [d.strftime("%b %y") for d in fidx], "forecast": [round(float(v)) for v in pred],
        "upper": [round(float(v + 1.28 * sd)) for v in pred], "lower": [round(float(max(0, v - 1.28 * sd))) for v in pred],
        "monthly_growth_pct": float(slope / max(s.mean(), 1) * 100), "mape": mape,
        "peak_month": fidx[int(np.argmax(pred))].strftime("%B %Y"),
    }
