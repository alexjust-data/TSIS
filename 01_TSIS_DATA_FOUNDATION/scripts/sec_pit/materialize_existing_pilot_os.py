#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.resolver import resolve_daily_os  # noqa: E402
from sec_pit.storage import atomic_write_json  # noqa: E402


def normalize_measurement_date(value: str | None) -> str | None:
    if not value:
        return None
    for pattern in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value.strip(), pattern).date().isoformat()
        except ValueError:
            continue
    return None


def instrument_row(path: Path, ticker: str) -> dict:
    columns = ["instrument_id", "ticker", "cik", "share_class_figi", "is_common_stock", "valid_from", "valid_to"]
    frame = pq.read_table(path, columns=columns).to_pandas()
    matches = frame[frame["ticker"].str.upper().eq(ticker.upper())]
    common = matches[matches["is_common_stock"].eq(True)]
    candidates = common if not common.empty else matches
    if candidates.empty:
        raise ValueError(f"Ticker not found in instrument master: {ticker}")
    return candidates.sort_values(["valid_to", "valid_from"], na_position="last").iloc[-1].to_dict()


def sessions_for(calendar_root: Path, instrument_id: str) -> list:
    dataset = ds.dataset(calendar_root, format="parquet", partitioning="hive")
    table = dataset.to_table(
        columns=["session_date"],
        filter=(ds.field("dataset_family") == "daily_raw")
        & (ds.field("instrument_id") == instrument_id)
        & (ds.field("expected_session") == True),  # noqa: E712
    )
    return sorted(set(table.column("session_date").to_pylist()))


def write_table(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def materialize(args: argparse.Namespace) -> dict:
    identity = instrument_row(args.instrument_master, args.ticker)
    policy = EdgarAvailabilityPolicy()
    candidates: dict[str, dict] = {}
    raw_rows = 0
    with args.candidates.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("ticker", "").upper() != args.ticker.upper():
                continue
            raw_rows += 1
            decision = policy.resolve(row.get("acceptance_datetime_edgar"), row.get("form"))
            observation_id = row["candidate_id"]
            measurement_at = normalize_measurement_date(row.get("measurement_date"))
            candidates[observation_id] = {
                "observation_id": observation_id,
                "observation_type": "SHARES_OUTSTANDING_ANCHOR_CANDIDATE",
                "cik": str(row.get("cik", "")).zfill(10),
                "accession_number": row.get("accession_number"),
                "form": row.get("form"),
                "instrument_id": identity["instrument_id"],
                "security_class_id": identity.get("share_class_figi"),
                "value": float(row["metric_value"]),
                "unit": "shares",
                "measurement_at": measurement_at,
                "effective_at": measurement_at,
                "filing_accepted_at": row.get("acceptance_datetime_edgar"),
                "eligible_from_session": decision.eligible_from_session.isoformat() if decision.eligible_from_session else None,
                "availability_policy_id": decision.policy_id,
                "source_url": None,
                "source_sha256": row.get("source_sha256"),
                "source_excerpt": row.get("source_excerpt"),
                "extraction_method": f"LEGACY_PILOT_{row.get('extraction_method', 'UNKNOWN')}",
                "quality_state": "CANDIDATE_REQUIRES_RECONCILIATION" if measurement_at else "REJECT_UNPARSEABLE_MEASUREMENT_DATE",
                "causality_state": decision.state,
                "attributes": json.dumps({
                    "legacy_source_fact_id": row.get("source_fact_id"),
                    "legacy_source_relative_path": row.get("source_relative_path"),
                    "candidate_confidence": row.get("candidate_confidence"),
                    "identity_resolution_level": row.get("identity_resolution_level"),
                }, sort_keys=True),
            }

    observations = sorted(candidates.values(), key=lambda row: (row.get("eligible_from_session") or "", row["observation_id"]))
    sessions = sessions_for(args.session_calendar_root, identity["instrument_id"])
    daily = [asdict(row) for row in resolve_daily_os(
        instrument_id=identity["instrument_id"],
        sessions=sessions,
        observations=observations,
        stale_after_days=args.stale_after_days,
        require_admitted=False,
    )]
    output = args.output_root / f"ticker={args.ticker.upper()}"
    write_table(output / "source_observations.parquet", observations)
    write_table(output / "daily_os_state.parquet", daily)
    state_counts: dict[str, int] = {}
    for row in daily:
        state_counts[row["os_state"]] = state_counts.get(row["os_state"], 0) + 1
    readout = {
        "materialization_id": "existing_sec_pilot_os_resolution_v0_1",
        "ticker": args.ticker.upper(),
        "instrument_id": identity["instrument_id"],
        "raw_candidate_rows": raw_rows,
        "deduplicated_observations": len(observations),
        "duplicate_candidate_rows_removed": raw_rows - len(observations),
        "session_rows": len(daily),
        "os_state_counts": state_counts,
        "status": "EXPERIMENTAL_LEGACY_PILOT_ONLY",
        "canonical_promotion": "NOT_AUTHORIZED",
    }
    atomic_write_json(output / "readout.json", readout)
    return readout


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Resolve existing SEC pilot O/S candidates into daily PIT state")
    value.add_argument("--ticker", required=True)
    value.add_argument("--candidates", type=Path, default=Path(r"D:\sec_float_pit_v0_1\derived\os_candidates_v0_1.jsonl"))
    value.add_argument("--instrument-master", type=Path, default=Path(r"G:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"))
    value.add_argument("--session-calendar-root", type=Path, default=Path(r"G:\TSIS\data\data_foundation_outputs\expected_data_calendar\expected_data_calendar_v0_1"))
    value.add_argument("--output-root", type=Path, default=Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1\legacy_pilot_resolution"))
    value.add_argument("--stale-after-days", type=int, default=180)
    return value


if __name__ == "__main__":
    args = parser().parse_args()
    print(json.dumps(materialize(args), indent=2, sort_keys=True))

