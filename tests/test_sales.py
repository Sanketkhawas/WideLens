def test_monthly_revenue_matches_sales(analysis):
    assert abs(analysis.monthly["revenue"].sum() - analysis.sales["amount"].sum()) < 1


def test_categories_present(analysis):
    assert "Electronics" in analysis.cat.index
