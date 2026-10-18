def test_forecast_shape_and_band(analysis):
    f = analysis.forecast
    assert len(f["forecast"]) == 6
    assert all(lo <= p <= hi for lo, p, hi in zip(f["lower"], f["forecast"], f["upper"]))
    assert f["mape"] < 15
