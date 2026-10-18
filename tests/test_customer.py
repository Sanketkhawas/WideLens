def test_cleaning_fixes_messy_rows(analysis):
    c = analysis.customers
    assert len(c) == 2000
    assert c["latitude"].notna().all() and c["longitude"].notna().all()
    assert c["area"].notna().all() and (c["area"].str.strip() == c["area"]).all()


def test_segments_cover_everyone(analysis):
    assert analysis.seg_summary["customers"].sum() == len(analysis.customers)
    assert list(analysis.seg_summary["segment"])[0] == "Champions"


def test_missing_required_columns():
    import pandas as pd
    import pytest
    from services.preprocessing.data_cleaner import DataError, clean
    with pytest.raises(DataError):
        clean({"customers": pd.DataFrame({"a": [1]})})
