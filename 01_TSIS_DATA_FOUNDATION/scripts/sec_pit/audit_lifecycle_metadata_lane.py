"""Audit the SEC lifecycle metadata lane against governed ticker snapshots."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def has_item(value: Any, target: str) -> bool:
    return target in {item.strip() for item in str(value or "").split(",")}


def candidate_type(form: str, items: Any, policy: dict[str, Any]) -> str | None:
    upper = str(form).upper()
    if upper in set(policy["registration_forms"]):
        return "REGISTRATION_FILING_CANDIDATE"
    if upper in set(policy["delisting_forms"]):
        return "FORM_25_FILING_CANDIDATE"
    if upper in set(policy["item_3_01_forms"]) and has_item(items, policy["item_3_01_value"]):
        return "ITEM_3_01_DISCLOSURE_CANDIDATE"
    return None


def security_class_gate(scope: dict[str, Any], snapshots: pd.DataFrame) -> tuple[str, str]:
    if snapshots.empty:
        return "FAIL", "NO_GOVERNED_TICKER_SNAPSHOTS"
    names = " ".join(snapshots["name"].dropna().astype(str).unique()).lower()
    preferred_markers = ("preferred stock", "depositary shares", "depositary share")
    if any(marker in names for marker in preferred_markers) and scope.get("is_common_stock") is True:
        return "FAIL", "REFERENCE_COMMON_FLAG_CONFLICTS_WITH_PREFERRED_OR_DEPOSITARY_NAME"
    if scope.get("is_common_stock") is not True:
        return "FAIL", "COMMON_STOCK_NOT_CONFIRMED"
    return "PASS", "COMMON_STOCK_CONFIRMED_WITHOUT_NAME_CONFLICT"


def target_identity_snapshots(scope: dict[str, Any], snapshots: pd.DataFrame) -> pd.DataFrame:
    if snapshots.empty:
        return snapshots.copy()
    share_class_figi = str(scope.get("share_class_figi") or "").strip()
    if share_class_figi and share_class_figi.lower() not in {"none", "nan"}:
        matched = snapshots.loc[
            snapshots["share_class_figi"].fillna("").astype(str).eq(share_class_figi)
        ].copy()
        if not matched.empty:
            return matched
    cik = "".join(character for character in str(scope.get("cik") or "") if character.isdigit()).zfill(10)
    snapshot_cik = (
        snapshots["cik"]
        .fillna("")
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\D", "", regex=True)
        .str.zfill(10)
    )
    return snapshots.loc[snapshot_cik.eq(cik)].copy()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--sec-root", type=Path, default=Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1"))
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    output_root = Path(policy["output_root"])
    if output_root.exists():
        raise FileExistsError(output_root)
    output_root.mkdir(parents=True)
    manifest = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "command_line": sys.argv,
        "host": socket.gethostname(),
        "wrapper_pid": os.getpid(),
        "policy_id": policy["policy_id"],
        "policy_path": args.policy.resolve().as_posix(),
        "source_metadata_prefix": policy["metadata_run_prefix"],
        "all_tickers_root": policy["all_tickers_root"],
        "output_root": output_root.as_posix(),
        "promotion_status": "NOT_AUTHORIZED",
    }
    atomic_json(output_root / "pre_manifest.json", manifest)
    atomic_json(output_root / "pid_manifest.json", {"wrapper_pid": os.getpid(), "observed_at_utc": utc_now()})

    config = json.loads(
        Path(r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\sec_pit_seven_ticker_stratified_replay_v0_1.json").read_text(encoding="utf-8")
    )
    tickers = [case["ticker"] for case in config["cases"]]
    snapshots = duckdb.connect().execute(
        """
        select ticker, cast(snapshot_date as date) snapshot_date, name, type, active,
               cik, composite_figi, share_class_figi, primary_exchange
        from read_parquet(?)
        where ticker in (select * from unnest(?))
        order by ticker, snapshot_date
        """,
        [policy["all_tickers_root"], tickers],
    ).df()

    ledger_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    for index, case in enumerate(config["cases"], start=1):
        ticker = case["ticker"]
        child = args.sec_root / "runs" / f"{policy['metadata_run_prefix']}__{ticker.lower()}"
        pre = json.loads((child / "pre_manifest.json").read_text(encoding="utf-8-sig"))
        scope = pre["scope"]
        inventory = pd.read_parquet(child / "filing_inventory.parquet")
        ticker_snapshots = snapshots.loc[snapshots["ticker"] == ticker].copy()
        identity_snapshots = target_identity_snapshots(scope, ticker_snapshots)
        class_gate, class_reason = security_class_gate(scope, identity_snapshots)

        candidates = 0
        registrations = 0
        form25 = 0
        item301 = 0
        for row in inventory.to_dict("records"):
            kind = candidate_type(row.get("form", ""), row.get("items"), policy)
            if kind is None:
                continue
            candidates += 1
            registrations += kind == "REGISTRATION_FILING_CANDIDATE"
            form25 += kind == "FORM_25_FILING_CANDIDATE"
            item301 += kind == "ITEM_3_01_DISCLOSURE_CANDIDATE"
            ledger_rows.append(
                {
                    "ticker": ticker,
                    "instrument_id": scope.get("instrument_id"),
                    "security_class_id": scope.get("share_class_figi"),
                    "cik": scope.get("cik"),
                    "candidate_type": kind,
                    "accession_number": row.get("accession_number"),
                    "form": row.get("form"),
                    "items": row.get("items"),
                    "filing_date": row.get("filing_date"),
                    "filing_accepted_at": row.get("acceptance_datetime"),
                    "eligible_from_session": row.get("eligible_from_session"),
                    "primary_document_url": row.get("primary_document_url"),
                    "filing_size_bytes": row.get("filing_size_bytes"),
                    "event_effective_at": None,
                    "event_type": None,
                    "event_resolution_state": "REQUIRES_PRIMARY_DOCUMENT_EXTRACTION",
                    "policy_id": policy["policy_id"],
                }
            )

        ciks = sorted(ticker_snapshots["cik"].dropna().astype(str).unique())
        figis = sorted(ticker_snapshots["share_class_figi"].dropna().astype(str).unique())
        identity_gate = "PASS_WITH_RESTRICTIONS" if len(ciks) > 1 or len(figis) > 1 else "PASS"
        active_last = (
            bool(identity_snapshots.sort_values("snapshot_date").iloc[-1]["active"])
            if not identity_snapshots.empty
            else None
        )
        source_gate = "PASS_WITH_RESTRICTIONS" if registrations > 0 else "FAIL"
        deep_acquisition = "HALT_SECURITY_CLASS" if class_gate == "FAIL" else "ELIGIBLE_AFTER_SELECTION_V0_2"
        gate_rows.append(
            {
                "ticker": ticker,
                "instrument_id": scope.get("instrument_id"),
                "security_class_gate": class_gate,
                "security_class_reason": class_reason,
                "identity_gate": identity_gate,
                "observed_cik_count": len(ciks),
                "observed_figi_count": len(figis),
                "ticker_history_first_snapshot": (
                    ticker_snapshots["snapshot_date"].min() if not ticker_snapshots.empty else None
                ),
                "ticker_history_last_snapshot": (
                    ticker_snapshots["snapshot_date"].max() if not ticker_snapshots.empty else None
                ),
                "first_observed_snapshot": (
                    identity_snapshots["snapshot_date"].min() if not identity_snapshots.empty else None
                ),
                "last_observed_snapshot": (
                    identity_snapshots["snapshot_date"].max() if not identity_snapshots.empty else None
                ),
                "active_at_last_snapshot": active_last,
                "registration_candidates": registrations,
                "form25_candidates": form25,
                "item_3_01_candidates": item301,
                "lifecycle_candidate_count": candidates,
                "lifecycle_source_gate": source_gate,
                "deep_acquisition_state": deep_acquisition,
            }
        )
        atomic_json(
            output_root / "heartbeat_latest.json",
            {"status": "RUNNING", "observed_at_utc": utc_now(), "current_index": index, "total_count": len(tickers), "ticker": ticker},
        )

    ledger = pd.DataFrame(ledger_rows).sort_values(["ticker", "filing_date", "accession_number"])
    gates = pd.DataFrame(gate_rows).sort_values("ticker")
    ledger.to_parquet(output_root / "lifecycle_source_candidate_ledger.parquet", index=False)
    gates.to_parquet(output_root / "lifecycle_gate_matrix.parquet", index=False)
    gates.to_csv(output_root / "lifecycle_gate_matrix.csv", index=False)

    expected_negative = set(policy["negative_control_tickers"])
    negative_correct = set(gates.loc[gates["security_class_gate"] == "FAIL", "ticker"]) == expected_negative
    aggregate = {
        "run_id": args.run_id,
        "status": "COMPLETE",
        "candidate_rows": len(ledger),
        "registration_candidates": int((ledger["candidate_type"] == "REGISTRATION_FILING_CANDIDATE").sum()),
        "form25_candidates": int((ledger["candidate_type"] == "FORM_25_FILING_CANDIDATE").sum()),
        "item_3_01_candidates": int((ledger["candidate_type"] == "ITEM_3_01_DISCLOSURE_CANDIDATE").sum()),
        "security_class_pass": int((gates["security_class_gate"] == "PASS").sum()),
        "security_class_fail": int((gates["security_class_gate"] == "FAIL").sum()),
        "negative_control_behavior": "PASS" if negative_correct else "FAIL",
        "lifecycle_metadata_lane_gate": "PASS_WITH_RESTRICTIONS" if negative_correct else "FAIL",
        "primary_document_acquisition": "NOT_EXECUTED",
        "first_last_trade_resolution": "NOT_EXECUTED",
        "promotion_status": "NOT_AUTHORIZED",
    }
    atomic_json(output_root / "lifecycle_readout.json", aggregate)
    atomic_json(output_root / "final_manifest.json", {**manifest, **aggregate, "completed_at_utc": utc_now()})
    atomic_json(output_root / "heartbeat_latest.json", {"status": "COMPLETE", "observed_at_utc": utc_now(), **aggregate})
    print(json.dumps(aggregate, indent=2))
    return 0 if aggregate["lifecycle_metadata_lane_gate"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())