
from scripts.sec_pit.review_target_interval_filings import _review_fields


def test_all_review_decisions_are_present_and_nonempty() -> None:
    accessions = [
        "0000950170-24-097653", "0000950170-24-104047", "0001193125-26-084412",
        "0001193125-26-104434", "0001140361-25-037402", "0001628280-26-052552",
        "0001354457-24-000148", "0001493152-25-001052", "0001838163-25-000009",
        "0001641172-25-017452", "0001641172-25-025734", "0001013762-23-005135",
    ]
    decisions = [_review_fields(accession) for accession in accessions]
    assert len(decisions) == 12
    assert all(decision["review_note"] for decision in decisions)


def test_non_target_security_classes_are_explicit() -> None:
    assert _review_fields("0001140361-25-037402")["class_scope"] == "NON_TARGET_WARRANT"
    assert _review_fields("0001354457-24-000148")["class_scope"] == "NON_TARGET_UNIT"
    assert _review_fields("0001013762-23-005135")["class_scope"] == "NON_TARGET_PREFERRED_RIGHT"


def test_suspension_is_not_legal_delisting() -> None:
    review = _review_fields("0001193125-26-104434")
    assert review["boundary_authority"] == "OBSERVED_EXCHANGE_TRADING_END_CANDIDATE"


def test_scheduled_transfer_requires_confirmation() -> None:
    review = _review_fields("0001628280-26-052552")
    assert review["boundary_authority"] == "SCHEDULED_EXCHANGE_TRADING_END_CANDIDATE"
