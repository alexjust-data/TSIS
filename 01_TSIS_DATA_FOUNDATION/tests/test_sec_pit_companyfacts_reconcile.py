import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.companyfacts_reconcile import (  # noqa: E402
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
