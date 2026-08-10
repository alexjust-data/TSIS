from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

TARGET_TIMING = "WITHIN_OR_AFTER_OBSERVED_TARGET_INTERVAL"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _review_fields(accession: str) -> dict[str, object]:
    fields: dict[str, dict[str, object]] = {
        "0000950170-24-097653": {"review_date": "2024-08-12", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Notice explicitly states no immediate delisting and continued NYSE trading."},
        "0000950170-24-104047": {"review_date": "2024-08-29", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Market-capitalization noncompliance notice; no immediate delisting."},
        "0001193125-26-084412": {"review_date": "2026-03-02", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "NYSE commenced proceedings, but trading continued pending appeal."},
        "0001193125-26-104434": {"review_date": "2026-03-06", "boundary_authority": "OBSERVED_EXCHANGE_TRADING_END_CANDIDATE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Filing states NYSE suspension after market close; Form 25 remained conditional and OTC trading continued."},
        "0001140361-25-037402": {"review_date": "2025-10-07", "boundary_authority": "NONE", "class_scope": "NON_TARGET_WARRANT", "review_note": "Section 12(b) registration covers warrants, not BBBY common stock."},
        "0001628280-26-052552": {"review_date": "2026-08-14", "boundary_authority": "SCHEDULED_EXCHANGE_TRADING_END_CANDIDATE", "class_scope": "TARGET_COMMON_STOCK_AND_WARRANT", "review_note": "Scheduled NYSE end and Nasdaq start are forward-looking as of filing; require subsequent confirmation."},
        "0001354457-24-000148": {"review_date": "2024-03-15", "boundary_authority": "NONE", "class_scope": "NON_TARGET_UNIT", "review_note": "Form 25 applies to Unit, not BNAI common stock."},
        "0001493152-25-001052": {"review_date": "2024-12-30", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Bid-price noncompliance notice explicitly has no current effect on listing."},
        "0001838163-25-000009": {"review_date": "2025-05-21", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Late-report noncompliance notice explicitly has no immediate listing effect."},
        "0001641172-25-017452": {"review_date": "2025-07-01", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Extension of compliance period; not compliance regained or delisting."},
        "0001641172-25-025734": {"review_date": "2025-08-21", "boundary_authority": "NONE", "class_scope": "TARGET_COMMON_STOCK", "review_note": "Late-report noncompliance notice explicitly has no immediate listing effect."},
        "0001013762-23-005135": {"review_date": "2023-10-11", "boundary_authority": "NONE", "class_scope": "NON_TARGET_PREFERRED_RIGHT", "review_note": "Section 12(b) registration covers Series Q preferred purchase rights, not DOMH common stock."},
    }
    return fields[accession]


def run(config_path: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_root = Path(config["source_run"])
    output_root = Path(config["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)
    source_path = source_root / "lifecycle_source_observations.parquet"
    source = pd.read_parquet(source_path)
    target = source[source["identity_timing_state"].eq(TARGET_TIMING)].copy()
    expected = set(config["decisions"])
    actual = set(target["accession_number"])
    if actual != expected:
        raise ValueError(f"review accession mismatch: missing={expected-actual}, unexpected={actual-expected}")

    rows = []
    for record in target.to_dict("records"):
        accession = record["accession_number"]
        fields = _review_fields(accession)
        events = config["decisions"][accession]
        rows.append({
            "ticker": record["ticker"],
            "instrument_id": record["instrument_id"],
            "security_class_id": record["security_class_id"],
            "cik": record["cik"],
            "accession_number": accession,
            "form": record["form"],
            "filing_date": record["filing_date"],
            "filing_accepted_at": record["filing_accepted_at"],
            "eligible_from_session": record["eligible_from_session"],
            "reviewed_event_types_json": json.dumps(events),
            "review_date": fields["review_date"],
            "class_scope": fields["class_scope"],
            "boundary_authority": fields["boundary_authority"],
            "legal_list_date": None,
            "legal_delist_date": None,
            "review_note": fields["review_note"],
            "source_sha256": record["source_sha256"],
            "source_object_path": record["source_object_path"],
            "review_policy_id": config["policy_id"],
            "promotion_status": config["promotion_status"],
        })
    reviewed = pd.DataFrame(rows).sort_values(["ticker", "filing_date", "accession_number"])
    ledger_path = output_root / "target_interval_filing_review_ledger.parquet"
    reviewed.to_parquet(ledger_path, index=False)
    reviewed.to_csv(output_root / "target_interval_filing_review_ledger.csv", index=False)

    now = datetime.now(UTC).isoformat()
    manifest = {
        "run_id": output_root.name,
        "status": "PASS_WITH_RESTRICTIONS",
        "created_at_utc": now,
        "policy_id": config["policy_id"],
        "source_run": str(source_root),
        "source_observations_sha256": _sha256(source_path),
        "reviewed_filing_count": len(reviewed),
        "boundary_authority_counts": reviewed["boundary_authority"].value_counts().to_dict(),
        "class_scope_counts": reviewed["class_scope"].value_counts().to_dict(),
        "legal_list_dates_admitted": int(reviewed["legal_list_date"].notna().sum()),
        "legal_delist_dates_admitted": int(reviewed["legal_delist_date"].notna().sum()),
        "parent_universe_scale_authorized": False,
        "output_sha256": _sha256(ledger_path),
    }
    (output_root / "final_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    print(run(args.config))


if __name__ == "__main__":
    main()
