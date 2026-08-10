from __future__ import annotations

# ruff: noqa: E402
import json
import sys
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.extract import extract_cover_page_os, extract_form345_owner_snapshot
from sec_pit.metadata import filing_roles, parse_submissions_root
from sec_pit.models import FilingRecord
from sec_pit.resolver import owner_exclusion_estimate, resolve_daily_os
from sec_pit.storage import ContentAddressedStore


def test_availability_never_uses_post_cutoff_filing_same_session() -> None:
    policy = EdgarAvailabilityPolicy()
    before = policy.resolve("2025-01-06T08:30:00Z", "10-Q")  # 03:30 ET
    after = policy.resolve("2025-01-06T09:30:00Z", "10-Q")   # 04:30 ET
    late = policy.resolve("2025-01-06T23:00:00Z", "10-Q")
    assert before.eligible_from_session == date(2025, 1, 6)
    assert after.eligible_from_session == date(2025, 1, 7)
    assert late.eligible_from_session == date(2025, 1, 7)


def test_submissions_parser_preserves_accession_acceptance_and_supplements() -> None:
    payload = {
        "cik": "123",
        "filings": {
            "recent": {
                "accessionNumber": ["0000000123-25-000001"],
                "form": ["10-Q"],
                "filingDate": ["2025-05-01"],
                "reportDate": ["2025-03-31"],
                "acceptanceDateTime": ["2025-05-01T16:00:00.000Z"],
                "primaryDocument": ["form10q.htm"],
                "primaryDocDescription": ["FORM 10-Q"],
                "items": [""],
                "isXBRL": [1],
                "isInlineXBRL": [1],
                "size": [1234],
            },
            "files": [{"name": "CIK0000000123-submissions-001.json"}],
        },
    }
    records, supplements = parse_submissions_root(payload, "fixture.json")
    assert records[0].cik == "0000000123"
    assert records[0].acceptance_datetime == "2025-05-01T16:00:00.000Z"
    assert supplements == ["CIK0000000123-submissions-001.json"]


def test_filing_roles_are_source_selection_not_semantic_claims() -> None:
    record = FilingRecord("0000000001", "x", "10-K", None, None, None, None, None, None, True, True, 1, "x")
    assert filing_roles(record) == ["OS_EVIDENCE_CANDIDATE", "OWNERSHIP_EVIDENCE_CANDIDATE"]


def test_content_store_deduplicates_and_compresses(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    first = store.put(b"same evidence", ".htm")
    second = store.put(b"same evidence", ".htm")
    assert first[0] == second[0]
    assert first[1] == second[1]
    assert len(list(tmp_path.rglob("*.gz"))) == 1
    assert store.read(first[1]) == b"same evidence"


def test_cover_page_os_extraction_preserves_source_and_causality() -> None:
    payload = b"<html><body>13,578,356 shares of the Registrant's Common Stock outstanding as of March 10, 2006</body></html>"
    observations = extract_cover_page_os(
        payload,
        cik="0000012239",
        accession_number="0001104659-06-021236",
        form="10-K",
        accepted_at="2006-03-31T20:35:58.000Z",
        instrument_id="instrument:domh",
        security_class_id="figi:domh",
        source_url="https://example.test/filing.htm",
        source_sha256="abc",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert len(observations) == 1
    assert observations[0].value == 13_578_356
    assert observations[0].measurement_at == "2006-03-10"
    assert observations[0].eligible_from_session == "2006-04-03"


def test_cover_page_os_does_not_capture_authorized_or_issuable_shares() -> None:
    payload = b"""<html>750,000,000 shares of Common Stock authorized and 10,000,000 shares of Preferred Stock. The company had 35,963,169 shares of Common Stock outstanding as of August 9, 2024. Separately, 1,107,500 shares of Common Stock have been issued to purchasers.</html>"""
    rows = extract_cover_page_os(
        payload,
        cik="0001838163",
        accession_number="a",
        form="10-Q",
        accepted_at="2024-08-14T20:25:36.000Z",
        instrument_id="i",
        security_class_id="s",
        source_url="x",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )
    assert {row.value for row in rows} == {35_963_169}

def test_form4_xml_separates_derivatives() -> None:
    payload = b"""<ownershipDocument><issuer><issuerCik>123</issuerCik></issuer><reportingOwner><reportingOwnerId><rptOwnerCik>9</rptOwnerCik><rptOwnerName>A Holder</rptOwnerName></reportingOwnerId></reportingOwner><nonDerivativeTable><nonDerivativeHolding><securityTitle><value>Common Stock</value></securityTitle><postTransactionAmounts><sharesOwnedFollowingTransaction><value>1200</value></sharesOwnedFollowingTransaction><ownershipNature><directOrIndirectOwnership><value>D</value></directOrIndirectOwnership></ownershipNature></postTransactionAmounts></nonDerivativeHolding></nonDerivativeTable><derivativeTable><derivativeHolding><securityTitle><value>Option</value></securityTitle><postTransactionAmounts><sharesOwnedFollowingTransaction><value>300</value></sharesOwnedFollowingTransaction><ownershipNature><directOrIndirectOwnership><value>D</value></directOrIndirectOwnership></ownershipNature></postTransactionAmounts></derivativeHolding></derivativeTable></ownershipDocument>"""
    rows = extract_form345_owner_snapshot(payload, cik="123", accession_number="a", form="4", accepted_at="2025-01-06T15:00:00Z", source_url="x", source_sha256="h", availability_policy=EdgarAvailabilityPolicy())
    assert {row.attributes["holding_type"] for row in rows} == {"NON_DERIVATIVE", "DERIVATIVE"}
    assert sum(row.value or 0 for row in rows if row.attributes["holding_type"] == "NON_DERIVATIVE") == 1200
    non_derivative = next(
        row for row in rows if row.attributes["holding_type"] == "NON_DERIVATIVE"
    )
    assert non_derivative.attributes["supported_issued_common_shares"] == 1200


def test_daily_os_resolver_is_causal_and_does_not_backfill_future_anchor() -> None:
    observations = [{
        "observation_id": "a",
        "observation_type": "SHARES_OUTSTANDING_ANCHOR_CANDIDATE",
        "value": 10_000_000,
        "measurement_at": "2025-01-02",
        "eligible_from_session": "2025-01-06",
        "causality_state": "AVAILABILITY_SESSION_RESOLVED",
        "quality_state": "ADMITTED_OS_ANCHOR",
    }]
    rows = resolve_daily_os(instrument_id="i", sessions=[date(2025, 1, 3), date(2025, 1, 6)], observations=observations)
    assert rows[0].os_state == "OS_UNAVAILABLE"
    assert rows[1].shares_outstanding_estimate_as_known == 10_000_000


def test_float_stays_unavailable_without_sufficient_ownership_coverage() -> None:
    result = owner_exclusion_estimate(shares_outstanding=10_000_000, unique_supported_excluded_shares=1_000_000, ownership_coverage_state="PARTIAL")
    assert result["float_owner_exclusion_estimate"] is None
    assert result["estimation_state"] == "OWNERSHIP_COVERAGE_INSUFFICIENT"


def test_plan_mode_creates_governed_artifacts(tmp_path: Path) -> None:
    instrument_master = tmp_path / "instrument_master.parquet"
    pq.write_table(pa.table({
        "instrument_id": ["instrument:test"],
        "ticker": ["TEST"],
        "cik": ["123"],
        "share_class_figi": ["BBGTEST"],
        "is_common_stock": [True],
        "valid_from": [None],
        "valid_to": [None],
    }), instrument_master)
    import subprocess
    output = tmp_path / "output"
    result = subprocess.run([
        sys.executable,
        str(SCRIPTS / "sec_pit" / "run_one_ticker_pilot.py"),
        "--instrument-master", str(instrument_master),
        "--output-root", str(output),
        "--ticker", "TEST",
        "--run-id", "fixture_run",
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    run_root = output / "runs" / "fixture_run"
    assert json.loads((run_root / "final_manifest.json").read_text())["result"] == "PLAN_ONLY"
    assert (run_root / "pre_manifest.json").exists()
    assert (run_root / "heartbeat.jsonl").exists()
