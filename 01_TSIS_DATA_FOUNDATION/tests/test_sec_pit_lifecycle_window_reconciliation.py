from scripts.sec_pit.reconcile_vendor_sec_lifecycle_windows import _comparison_state, _delta


def test_delta_preserves_direction() -> None:
    assert _delta("2024-03-15", "2024-03-18") == -3


def test_ticker_reuse_has_priority() -> None:
    row = {
        "identity_match_state": "TICKER_REUSE_CONFLICT",
        "sec_boundary_state": "NONE_ADMITTED",
        "vendor_first_seen_to_daily_delta_days": 0,
    }
    assert _comparison_state(row) == "TICKER_REUSE_CONFLICT"


def test_scheduled_sec_boundary_is_not_promoted() -> None:
    row = {
        "identity_match_state": "TARGET_IDENTITY_MATCHED",
        "sec_boundary_state": "SCHEDULED_REQUIRES_CONFIRMATION",
        "vendor_first_seen_to_daily_delta_days": 0,
    }
    assert _comparison_state(row) == "SEC_SCHEDULED_REQUIRES_CONFIRMATION"


def test_observed_exchange_end_is_not_legal_delist() -> None:
    row = {
        "identity_match_state": "TARGET_IDENTITY_MATCHED",
        "sec_boundary_state": "OBSERVED_EXCHANGE_END_CANDIDATE",
        "vendor_first_seen_to_daily_delta_days": 0,
    }
    assert _comparison_state(row) == "SEC_EXCHANGE_END_CANDIDATE_NOT_LEGAL_DELIST"
