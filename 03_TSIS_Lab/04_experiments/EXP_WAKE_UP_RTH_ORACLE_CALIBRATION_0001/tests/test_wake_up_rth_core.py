from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from wake_up_rth_core import (  # noqa: E402
    SessionContext,
    build_session_second_metrics,
    discover_candidates,
    stable_case_id,
)
from build_wake_up_blind_panel import _deterministic_sample  # noqa: E402


class AllowAllPolicy:
    @staticmethod
    def evaluate_trade(row, matrix, **kwargs):
        return {
            "trade_activity_eligibility_state": "ELIGIBLE_WITH_RESTRICTIONS",
            "trade_notional_eligibility_state": "ELIGIBLE_WITH_RESTRICTIONS",
        }


def context() -> SessionContext:
    return SessionContext(
        target_ordinal=1,
        block_id="block",
        cohort_id="D1",
        instrument_id="instrument",
        ticker="TEST",
        session_date="2021-01-04",
        open_utc=pd.Timestamp("2021-01-04T14:30:00Z"),
        close_utc=pd.Timestamp("2021-01-04T15:30:00Z"),
        expected_decision_seconds=3599,
        manifest_declared_decision_seconds=3600,
        presession_reference_price=2.0,
        presession_reference_market_cap_proxy=25000000.0,
    )


def base_metrics(seconds: int = 3600) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "decision_timestamp_utc": pd.date_range(
                "2021-01-04T14:30:01Z", periods=seconds, freq="1s"
            ),
            "trade_count": 0,
            "dollar_volume": 0.0,
            "distinct_timestamp_clusters": 0,
            "source_state": "OBSERVED",
        }
    )
    for key, value in {
        "target_file_key": "target_fixture",
        "target_ordinal": 1,
        "block_id": "block",
        "cohort_id": "D1",
        "instrument_id": "instrument",
        "ticker": "TEST",
        "session_date": "2021-01-04",
        "session_open_utc": pd.Timestamp("2021-01-04T14:30:00Z"),
        "presession_reference_price": 2.0,
        "presession_reference_market_cap_proxy": 25000000.0,
    }.items():
        frame[key] = value
    return frame


def test_abrupt_activity_transition_is_reduced_to_candidate():
    metrics = base_metrics()
    burst = slice(1800, 1830)
    metrics.loc[burst, "trade_count"] = 5
    metrics.loc[burst, "distinct_timestamp_clusters"] = 5
    metrics.loc[burst, "dollar_volume"] = 25000.0
    candidates = discover_candidates(
        metrics, [900], [30], 2, 2, 4, 12, 300
    )
    assert not candidates.empty
    onset = pd.Timestamp(candidates.iloc[0]["candidate_timestamp_utc"])
    expected = pd.Timestamp(metrics.iloc[1800]["decision_timestamp_utc"])
    assert abs((onset - expected).total_seconds()) <= 30
    assert set(candidates["candidate_state"]) == {
        "UNLABELED_CANDIDATE_REDUCTION_ONLY"
    }


def test_observed_zero_session_has_no_candidate():
    assert discover_candidates(
        base_metrics(), [900], [30], 2, 2, 4, 12, 300
    ).empty


def test_missing_source_is_unavailable_not_zero(tmp_path):
    metrics, audit, events = build_session_second_metrics(
        context(), tmp_path, AllowAllPolicy(), {}, 1000
    )
    assert len(metrics) == 3599
    assert set(metrics["source_state"]) == {"UNAVAILABLE_SOURCE_FILE"}
    assert audit["source_state"] == "UNAVAILABLE_SOURCE_FILE"
    assert events.empty


def test_latency_moves_trade_to_first_legal_decision_second(tmp_path):
    source = (
        tmp_path / "TEST" / "year=2021" / "month=01"
        / "day=2021-01-04" / "market.parquet"
    )
    source.parent.mkdir(parents=True)
    pd.DataFrame(
        {
            "ticker": ["TEST"],
            "date": ["2021-01-04"],
            "timestamp": [pd.Timestamp("2021-01-04T14:30:00.662Z")],
            "price": [2.0],
            "size": [100],
            "exchange": [1],
            "conditions": [None],
        }
    ).to_parquet(source, index=False)
    metrics, audit, events = build_session_second_metrics(
        context(), tmp_path, AllowAllPolicy(), {}, 1000
    )
    row = metrics.loc[metrics["trade_count"] == 1].iloc[0]
    assert pd.Timestamp(row["decision_timestamp_utc"]) == pd.Timestamp(
        "2021-01-04T14:30:02Z"
    )
    assert row["dollar_volume"] == 200.0
    assert audit["activity_eligible_rows"] == 1
    assert len(events) == 1


def test_case_id_is_deterministic():
    row = pd.Series(
        {
            "instrument_id": "instrument",
            "session_date": "2021-01-04",
            "candidate_timestamp_utc": "2021-01-04T14:40:00Z",
            "panel_role": "CONTROL_DORMANT",
        }
    )
    assert stable_case_id(row) == stable_case_id(row)


def test_blind_sampler_balances_rth_time_before_composite_strata():
    rows = []
    for bucket in ("OPEN_0_60M", "MID_60_240M", "CLOSE_240M_PLUS"):
        for ordinal in range(30):
            rows.append(
                {
                    "row_id": f"{bucket}-{ordinal}",
                    "rth_time_bucket": bucket,
                    "sampling_stratum": (
                        f"{bucket}|P_{ordinal % 5}|MCAP_{ordinal % 4}|"
                        f"PRIOR_{ordinal % 3}|QUALITY_{ordinal % 2}"
                    ),
                }
            )
    source = pd.DataFrame(rows)
    selected = _deterministic_sample(source, 10, 20260817, "D1|ROLE")
    counts = selected["rth_time_bucket"].value_counts()
    assert set(counts.index) == {
        "OPEN_0_60M",
        "MID_60_240M",
        "CLOSE_240M_PLUS",
    }
    assert counts.max() - counts.min() <= 1
    repeated = _deterministic_sample(source, 10, 20260817, "D1|ROLE")
    assert selected["row_id"].tolist() == repeated["row_id"].tolist()
