import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.companyfacts_reconcile import (  # noqa: E402
    promote_companyfacts_validated_primary_anchors,
    reconcile_companyfacts_to_primary_os,
)


def fact(value: float) -> dict:
    return {
        "observation_id": "cf",
        "accession_number": "a",
        "form": "10-Q",
        "measurement_at": "2025-01-01",
        "eligible_from_session": "2025-01-03",
        "value": value,
        "extraction_method": "SEC_COMPANYFACTS_XBRL",
        "attributes": {
            "taxonomy": "dei",
            "concept": "EntityCommonStockSharesOutstanding",
        },
    }


def primary(value: float) -> dict:
    return {
        "observation_id": "primary",
        "accession_number": "a",
        "measurement_at": "2025-01-01",
        "value": value,
    }


def test_exact_single_class_fact_is_validation_authorized() -> None:
    rows, readout = reconcile_companyfacts_to_primary_os(
        [fact(100)], [primary(100)],
        target_class_label="Common Stock",
        security_class_gate="PASS",
    )
    assert rows[0]["reconciliation_state"] == (
        "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE"
    )
    assert rows[0]["class_validation_authorized"] is True
    assert readout["class_validation_authorized_rows"] == 1


def test_multiclass_exact_fact_is_not_class_validation() -> None:
    rows, _ = reconcile_companyfacts_to_primary_os(
        [fact(100)], [primary(100)],
        target_class_label="Class A ordinary shares",
        security_class_gate="PASS",
    )
    assert rows[0]["reconciliation_state"] == (
        "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE"
    )
    assert rows[0]["class_validation_authorized"] is False


def test_value_conflict_is_explicit() -> None:
    rows, readout = reconcile_companyfacts_to_primary_os(
        [fact(100)], [primary(90)],
        target_class_label="Common Stock",
        security_class_gate="PASS",
    )
    assert rows[0]["reconciliation_state"] == (
        "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT"
    )
    assert readout["value_conflicts"] == 1


def test_exact_companyfacts_validation_promotes_primary_anchor() -> None:
    candidate = {
        **primary(100),
        "eligible_from_session": "2025-01-03",
        "causality_state": "AVAILABILITY_SESSION_RESOLVED",
        "attributes": {"security_class_label": "Common Stock"},
    }
    reconciliation, _ = reconcile_companyfacts_to_primary_os(
        [fact(100)], [candidate],
        target_class_label="Common Stock",
        security_class_gate="PASS",
    )
    promoted, readout = promote_companyfacts_validated_primary_anchors(
        [candidate], reconciliation,
        reconciliation_artifact_sha256="artifact-hash",
    )
    assert len(promoted) == 1
    assert promoted[0]["value"] == 100
    assert promoted[0]["quality_state"] == "ADMITTED_OS_ANCHOR"
    assert promoted[0]["attributes"]["companyfacts_reconciliation_artifact_sha256"] == "artifact-hash"
    assert readout["promoted_anchor_count"] == 1


def test_companyfacts_conflict_never_promotes_primary_anchor() -> None:
    candidate = {
        **primary(90),
        "eligible_from_session": "2025-01-03",
        "causality_state": "AVAILABILITY_SESSION_RESOLVED",
        "attributes": {"security_class_label": "Common Stock"},
    }
    reconciliation, _ = reconcile_companyfacts_to_primary_os(
        [fact(100)], [candidate],
        target_class_label="Common Stock",
        security_class_gate="PASS",
    )
    promoted, readout = promote_companyfacts_validated_primary_anchors(
        [candidate], reconciliation,
        reconciliation_artifact_sha256="artifact-hash",
    )
    assert promoted == []
    assert readout["value_conflict_count"] == 1
