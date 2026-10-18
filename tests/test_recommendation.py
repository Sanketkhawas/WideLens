from services.recommendation.location_ranker import rank_sites


def _rank(a, stores=None, **kw):
    return rank_sites(a.customers, a.areas, a.stores if stores is None else stores, a.months, **kw)[0]


def test_scores_bounded_and_sorted(analysis):
    df = _rank(analysis)
    assert df["score"].between(0, 100).all()
    assert df["score"].is_monotonic_decreasing


def test_existing_store_areas_not_recommended(analysis):
    cand = _rank(analysis)
    cand = cand[~cand["has_store"]]
    assert not set(cand["area"]) & {"Sitabuldi", "Dharampeth"}


def test_weights_change_ranking(analysis):
    rent_only = _rank(analysis, weights={"demand": 0, "gap": 0, "spend": 0, "competition": 0, "rent": 1, "population": 0})
    assert rent_only.iloc[0]["avg_rent"] == analysis.areas["avg_rent"].min()


def test_no_stores_means_everything_unserved(analysis):
    df = _rank(analysis, stores=analysis.stores.iloc[0:0])
    assert (df["unserved_customers"] == df["catchment_customers"]).all()
