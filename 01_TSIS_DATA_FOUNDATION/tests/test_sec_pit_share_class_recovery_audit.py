from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.audit_share_class_recovery import (  # noqa: E402
    _document_signals,
    derive_workstreams,
)


def test_explicit_current_and_acquirable_columns_are_a_distinct_workstream() -> None:
    result = derive_workstreams(
        target_class_label="Common Stock",
        ownership_states=Counter({"CURRENTLY_ISSUED_COMPONENT_UNRESOLVED": 8}),
        supported_single_rows=0,
        baseline_states={"OWNERSHIP_TABLE_REQUIRES_CLASS_RECONCILIATION"},
        document_signals={
            "explicit_current_acquirable_columns": True,
            "numeric_component_decomposition": False,
        },
    )
    assert "EXPLICIT_CURRENT_ACQUIRABLE_COLUMN_PARSER" in result


def test_numbered_target_with_supported_single_table_requires_bridge_proof() -> None:
    result = derive_workstreams(
        target_class_label="Class A Common Stock",
        ownership_states=Counter({"NO_MULTI_CLASS_CONFLICT_IDENTIFIED": 9}),
        supported_single_rows=9,
        baseline_states={"OWNERSHIP_BASELINE_CONTENT_COMPLETE_CANDIDATE"},
        document_signals={},
    )
    assert result == ["SINGLE_TABLE_TO_NUMBERED_TARGET_CLASS_BRIDGE"]


def test_numbered_target_with_both_classes_in_document_stays_fail_closed() -> None:
    result = derive_workstreams(
        target_class_label="Class A Common Stock",
        ownership_states=Counter({"NO_MULTI_CLASS_CONFLICT_IDENTIFIED": 9}),
        supported_single_rows=9,
        baseline_states={"OWNERSHIP_BASELINE_CONTENT_COMPLETE_CANDIDATE"},
        document_signals={"document_mentions_class_a_and_b": True},
    )
    assert result == ["EXPLICIT_MULTI_CLASS_COMPONENT_EVIDENCE"]


def test_numeric_footnote_components_are_not_silently_treated_as_current() -> None:
    result = derive_workstreams(
        target_class_label="Common Stock",
        ownership_states=Counter({"CURRENTLY_ISSUED_COMPONENT_UNRESOLVED": 12}),
        supported_single_rows=0,
        baseline_states={"OWNERSHIP_TABLE_REQUIRES_CLASS_RECONCILIATION"},
        document_signals={"numeric_component_decomposition": True},
    )
    assert result == ["NUMERIC_FOOTNOTE_COMPONENT_DECOMPOSITION"]


def test_true_multiclass_table_remains_fail_closed() -> None:
    result = derive_workstreams(
        target_class_label="Class A Ordinary Shares",
        ownership_states=Counter({"MULTI_CLASS_ALLOCATION_REQUIRED": 10}),
        supported_single_rows=0,
        baseline_states={"OWNERSHIP_TABLE_REQUIRES_CLASS_RECONCILIATION"},
        document_signals={"document_mentions_class_a_and_b": True},
    )
    assert result == ["EXPLICIT_MULTI_CLASS_COMPONENT_EVIDENCE"]


def test_footnote_decomposition_is_not_mislabeled_as_separate_columns() -> None:
    signals = _document_signals(
        "Shares Owned include 54,667 shares underlying exercisable stock options."
    )
    assert signals["numeric_component_decomposition"] is True
    assert signals["explicit_current_acquirable_columns"] is False
