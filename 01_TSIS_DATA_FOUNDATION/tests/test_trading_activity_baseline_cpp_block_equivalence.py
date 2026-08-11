import pandas as pd
from validate_trading_activity_baseline_cpp_block_equivalence import (
    compare_frames,
)


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "identity": pd.Series(["A", "B", None], dtype="object"),
            "count": pd.Series([1, 2, pd.NA], dtype="Int64"),
            "value": pd.Series([1.0, 2.0, pd.NA], dtype="Float64"),
            "available": pd.Series([True, False, pd.NA], dtype="boolean"),
            "observed_at": pd.to_datetime(
                ["2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z", None],
                utc=True,
            ),
        }
    )


def test_compare_frames_passes_complete_exact_contract() -> None:
    expected = _frame()
    result = compare_frames(expected, expected.copy())

    assert result["status"] == "PASS"
    assert result["all_dtypes_exact"] is True
    assert result["contract_mismatch_count"] == 0
    assert result["exact_mismatch_count"] == 0


def test_compare_frames_reports_float_tolerance_without_hiding_exact_difference() -> None:
    expected = _frame()
    actual = expected.copy()
    actual.loc[0, "value"] = 1.0 + 1e-13

    result = compare_frames(expected, actual)

    assert result["status"] == "PASS"
    assert result["contract_mismatch_count"] == 0
    assert result["exact_mismatch_count"] == 1
    assert result["column_results"]["value"]["exact_value_mismatches"] == 1


def test_compare_frames_fails_dtype_null_value_and_column_order_changes() -> None:
    expected = _frame()

    wrong_dtype = expected.copy()
    wrong_dtype["count"] = wrong_dtype["count"].astype("Float64")
    assert compare_frames(expected, wrong_dtype)["status"] == "FAIL"

    wrong_null = expected.copy()
    wrong_null.loc[0, "identity"] = None
    assert compare_frames(expected, wrong_null)["status"] == "FAIL"

    wrong_value = expected.copy()
    wrong_value.loc[0, "value"] = 1.01
    assert compare_frames(expected, wrong_value)["status"] == "FAIL"

    wrong_order = expected[list(reversed(expected.columns))]
    assert compare_frames(expected, wrong_order)["status"] == "FAIL"
