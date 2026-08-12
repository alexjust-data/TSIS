#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


REGISTRATION_FORMS = {"8-A", "8-A/A", "8-A12B", "8-A12B/A", "8-A12G", "8-A12G/A"}
DELISTING_FORMS = {"25", "25-NSE"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lifecycle_row(case: dict, inventory: pd.DataFrame) -> dict:
    forms = inventory["form"].fillna("").astype(str).str.upper()
    dates = pd.to_datetime(inventory["filing_date"], errors="coerce")
    items = inventory["items"].fillna("").astype(str)
    registration = dates[forms.isin(REGISTRATION_FORMS)].dropna()
    delisting = dates[forms.isin(DELISTING_FORMS)].dropna()
    item_301 = dates[items.str.split(",").map(
        lambda values: any(value.strip() == "3.01" for value in values)
    )].dropna()
    exchange_end = pd.concat([delisting, item_301]).max() if len(delisting) + len(item_301) else pd.NaT
    states = []
    if len(registration):
        states.append("REGISTRATION_METADATA_CANDIDATE")
    if len(delisting):
        states.append("FORM_25_METADATA_CANDIDATE")
    if len(item_301):
        states.append("ITEM_3_01_METADATA_CANDIDATE")
    return {
        "ticker": case["ticker"], "cik": case["cik"],
        "instrument_id": case["instrument_id"],
        "security_class_id": case.get("security_class_id"),
        "market_first_daily_date": str(case["first_seen_date"])[:10],
        "market_last_daily_date": str(case["last_observed_date"])[:10],
        "market_trade_presence_state": "PARENT_UNIVERSE_OBSERVED_WINDOW_ONLY",
        "sec_registration_candidate_count": len(registration),
        "sec_delisting_candidate_count": len(delisting),
        "sec_item_3_01_candidate_count": len(item_301),
        "sec_first_registration_candidate": registration.min() if len(registration) else None,
        "sec_exchange_end_candidate": exchange_end if pd.notna(exchange_end) else None,
        "sec_boundary_state": "+".join(states) if states else "NO_METADATA_BOUNDARY_CANDIDATE",
        "sec_legal_list_date": None, "sec_legal_delist_date": None,
        "comparison_state": "CANDIDATE_REQUIRES_PRIMARY_DOCUMENT_AND_MARKET_RECONCILIATION",
        "promotion_status": "NOT_AUTHORIZED",
    }


def execute(cases_path: Path, inventory_template: str, output: Path) -> Path:
    cases_path, output = cases_path.resolve(), output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    rows, input_hashes = [], {"cases": sha256_file(cases_path)}
    for case in cases:
        path = Path(inventory_template.format(ticker_lower=case["ticker"].lower(), ticker=case["ticker"])).resolve()
        input_hashes[f"inventory_{case['ticker']}"] = sha256_file(path)
        rows.append(lifecycle_row(case, pd.read_parquet(path)))
    frame = pd.DataFrame(rows).sort_values("ticker")
    if len(frame) != len(cases) or frame["ticker"].nunique() != len(cases):
        raise ValueError("lifecycle ledger grain failure")
    if frame["sec_legal_list_date"].notna().any() or frame["sec_legal_delist_date"].notna().any():
        raise ValueError("metadata-only lifecycle must not populate legal dates")
    ledger = output / "lifecycle_window_reconciliation.parquet"
    frame.to_parquet(ledger, index=False)
    frame.to_csv(output / "lifecycle_window_reconciliation.csv", index=False)
    manifest = {
        "run_id": output.name, "status": "COMPLETE", "created_at_utc": datetime.now(UTC).isoformat(),
        "case_count": len(frame), "policy_id": "sec_pit_metadata_lifecycle_candidate_v0_1",
        "legal_dates_admitted": 0, "primary_documents_used": 0,
        "comparison_state_counts": frame["comparison_state"].value_counts().to_dict(),
        "input_hashes": input_hashes, "output_sha256": sha256_file(ledger),
        "next_gate": "PREDOWNLOAD_CONTROL",
    }
    (output / "final_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--inventory-template", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args.cases, args.inventory_template, args.output))
