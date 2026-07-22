from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.price_views import (
    apply_adjusted_view,
    apply_adjusted_proxy_view,
    apply_split_normalized_view,
    build_future_split_factor_series,
    canonicalize_split_table,
)


def test_canonicalize_split_table_forward_and_reverse():
    splits = pd.DataFrame(
        [
            {"execution_date": "2015-02-05", "split_from": 1, "split_to": 2},
            {"execution_date": "2016-08-11", "split_from": 20, "split_to": 1},
        ]
    )
    out = canonicalize_split_table(splits)
    assert list(out["split_ratio"]) == [2.0, 0.05]


def test_future_split_factor_series_applies_future_product():
    splits = pd.DataFrame([{"execution_date": "2015-02-05", "split_from": 1, "split_to": 2}])
    dates = pd.Series(pd.to_datetime(["2013-11-04", "2015-02-05", "2016-01-01"]))
    factors = build_future_split_factor_series(dates, splits)
    assert factors.iloc[0] == 2.0
    assert factors.iloc[1] == 1.0
    assert factors.iloc[2] == 1.0


def test_apply_split_normalized_view_scales_raw_prices():
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2013-11-04", "2015-02-06"]),
            "c": [7.71, 8.00],
        }
    )
    splits = pd.DataFrame([{"execution_date": "2015-02-05", "split_from": 1, "split_to": 2}])
    out, meta = apply_split_normalized_view(frame, splits, price_cols=("c",))
    assert meta.view_name == "split_normalized"
    assert math.isclose(out.loc[0, "c_split_normalized"], 15.42, rel_tol=1e-9)
    assert math.isclose(out.loc[1, "c_split_normalized"], 8.00, rel_tol=1e-9)


def test_apply_adjusted_proxy_view_uses_future_dividend_factor_chain():
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2016-06-28", "2016-06-29", "2016-07-01"]),
            "c": [5.44, 5.50, 5.60],
        }
    )
    dividends = pd.DataFrame(
        [
            {"ex_dividend_date": "2016-06-30", "cash_amount": 0.10},
            {"ex_dividend_date": "2016-07-05", "cash_amount": 0.20},
        ]
    )
    out, meta = apply_adjusted_proxy_view(frame, dividends, price_cols=("c",))
    assert meta.view_name == "adjusted_proxy"
    assert math.isclose(out.loc[0, "future_dividend_sum"], 0.30, rel_tol=1e-12)
    assert math.isclose(out.loc[1, "future_dividend_sum"], 0.30, rel_tol=1e-12)
    assert math.isclose(out.loc[2, "future_dividend_sum"], 0.20, rel_tol=1e-12)
    assert out.loc[0, "future_dividend_factor"] < 1.0
    assert out.loc[1, "future_dividend_factor"] < 1.0
    assert out.loc[2, "future_dividend_factor"] < 1.0
    assert out.loc[0, "c_adjusted_proxy"] < out.loc[0, "c"]


def test_apply_adjusted_view_applies_split_then_dividend_chain():
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2013-11-04", "2015-02-06"]),
            "c": [7.71, 8.00],
        }
    )
    splits = pd.DataFrame([{"execution_date": "2015-02-05", "split_from": 1, "split_to": 2}])
    dividends = pd.DataFrame([{"ex_dividend_date": "2015-03-01", "cash_amount": 0.20}])
    out, meta = apply_adjusted_view(frame, splits, dividends, price_cols=("c",))
    assert meta.view_name == "adjusted"
    assert math.isclose(out.loc[0, "c_split_normalized"], 15.42, rel_tol=1e-9)
    assert out.loc[0, "future_adjustment_factor"] < 1.0
    assert out.loc[1, "future_adjustment_factor"] < 1.0
    assert out.loc[0, "c_adjusted"] < out.loc[0, "c_split_normalized"]
    assert out.loc[1, "c_adjusted"] < out.loc[1, "c_split_normalized"]
