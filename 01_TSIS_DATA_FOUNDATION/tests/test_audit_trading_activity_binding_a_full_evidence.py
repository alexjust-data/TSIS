from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_trading_activity_binding_a_full_evidence",
    ROOT / "scripts" / "audit_trading_activity_binding_a_full_evidence.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_not_close_preserves_null_comparison_semantics():
    left = pd.Series([1.0, 2.0, None])
    right = pd.Series([1.0, 2.1, 3.0])
    assert MODULE.not_close(left, right).tolist() == [False, True, False]


def test_failures_where_treats_null_as_not_a_failure():
    series = pd.Series([True, False, pd.NA], dtype="boolean")
    assert MODULE.failures_where(series) == 1


def test_binding_a_subwindow_mapping_is_one_then_five_seconds():
    windows = pd.Series([5, 15, 30, 60, 300])
    expected = MODULE.expected_subwindow_seconds(windows)
    assert expected.tolist() == [1, 1, 1, 5, 5]


def test_explicit_parquet_reader_bypasses_hive_partition_inference(tmp_path):
    path = tmp_path / "ticker=ABC" / "session_date=2026-08-14" / "part.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(pa.table({"ticker": ["ABC"], "value": [1]}), path)
    frame = MODULE.read_columns(str(path), ["ticker", "value"])
    assert frame.to_dict("records") == [{"ticker": "ABC", "value": 1}]
