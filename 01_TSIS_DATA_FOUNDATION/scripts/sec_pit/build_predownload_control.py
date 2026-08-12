# ruff: noqa: E402
"""Build the network-free SEC PIT identity and document-selection control."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import pyarrow.parquet as pq

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.models import FilingRecord
from sec_pit.predownload_control import (
    POLICY_ID,
    accession_link_state,
    filing_roles_v0_2,
    security_class_gate,
    selection_plan_v0_2,
    temporal_scope_state,
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(["git", *args], cwd=Path(__file__).resolve().parents[3], text=True).strip()
    except Exception:
        return None


def cik(value: Any) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit()).zfill(10)


def load_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    if config.get("cases"):
        return list(config["cases"])
    cases_path = Path(config["cases_path"]).resolve()
    overrides = config.get("expected_class_gate_overrides", {})
    default = config.get("default_expected_class_gate", "PASS")
    return [
        {**case, "expected_class_gate": overrides.get(case["ticker"], default)}
        for case in json.loads(cases_path.read_text(encoding="utf-8"))
    ]


def inventory_path(config: dict[str, Any], ticker: str) -> Path:
    if config.get("metadata_inventory_template"):
        return Path(config["metadata_inventory_template"].format(
            ticker=ticker, ticker_lower=ticker.lower()
        ))
    return (
        Path(config["sec_root"])
        / "runs"
        / f"{config['metadata_run_prefix']}__{ticker.lower()}"
        / "filing_inventory.parquet"
    )


def serial(value: Any) -> Any:
    if isinstance(value, list | tuple | dict):
        return value
    missing = pd.isna(value)
    return None if isinstance(missing, bool) and missing else value


def record_from_row(row: dict[str, Any]) -> FilingRecord:
    return FilingRecord(
        cik=cik(row.get("cik")), accession_number=str(row.get("accession_number") or ""),
        form=str(row.get("form") or ""), filing_date=serial(row.get("filing_date")),
        report_date=serial(row.get("report_date")), acceptance_datetime=serial(row.get("acceptance_datetime")),
        primary_document=serial(row.get("primary_document")),
        primary_document_description=serial(row.get("primary_document_description")),
        items=serial(row.get("items")), is_xbrl=serial(row.get("is_xbrl")),
        is_inline_xbrl=serial(row.get("is_inline_xbrl")),
        filing_size_bytes=serial(row.get("filing_size_bytes")), metadata_source=str(row.get("metadata_source") or ""),
    )


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--config", type=Path, required=True)
    value.add_argument("--output-root", type=Path, required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    cases = load_cases(config)
    inventory_paths = [inventory_path(config, case["ticker"]) for case in cases]
    static_inputs = [
        config_path,
        Path(config["parent_universe_path"]),
        Path(config["instrument_master_path"]),
        Path(config["lifecycle_reconciliation_path"]),
        *inventory_paths,
    ]
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"Output exists; version or remove explicitly: {output}")
    output.mkdir(parents=True)
    manifest = {
        "run_id": output.name,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": sha256(Path(__file__).resolve()),
        "policy_id": POLICY_ID,
        "config_id": config["config_id"],
        "config_path": config_path.as_posix(),
        "config_sha256": sha256(config_path),
        "git_branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty_state": bool(git_value("status", "--porcelain")),
        "network_access": "PROHIBITED_AND_NOT_USED",
        "primary_document_acquisition": "NOT_EXECUTED",
        "promotion_status": "PROBE_ONLY",
        "input_artifacts": [
            {"path": path.resolve().as_posix(), "sha256": sha256(path.resolve())}
            for path in static_inputs
        ],
        "all_tickers_root": config["all_tickers_root"],
    }
    atomic_json(output / "pre_manifest.json", manifest)
    atomic_json(output / "pid_manifest.json", {"wrapper_pid": os.getpid(), "observed_at_utc": utc_now()})

    tickers = [case["ticker"] for case in cases]
    universe = pq.read_table(config["parent_universe_path"], columns=["ticker", "first_seen_date", "last_observed_date"]).to_pandas()
    universe = universe.loc[universe["ticker"].isin(tickers)].copy()
    instruments = pq.read_table(config["instrument_master_path"], columns=[
        "instrument_id", "ticker", "name", "cik", "share_class_figi", "ticker_type_code",
        "is_common_stock", "valid_from", "valid_to",
    ]).to_pandas()
    snapshots = duckdb.connect().execute(
        """
        select ticker, cast(snapshot_date as date) snapshot_date, name, type, active,
               cik, composite_figi, share_class_figi, primary_exchange
        from read_parquet(?)
        where ticker in (select * from unnest(?))
        order by ticker, snapshot_date
        """,
        [config["all_tickers_root"], tickers],
    ).df()
    lifecycle = pd.read_parquet(config["lifecycle_reconciliation_path"])

    interval_rows: list[dict[str, Any]] = []
    link_rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    for case in cases:
        ticker = case["ticker"]
        universe_rows = universe.loc[universe["ticker"] == ticker]
        instrument_rows = instruments.loc[instruments["ticker"] == ticker]
        if len(universe_rows) != 1 or len(instrument_rows) != 1:
            raise RuntimeError(f"{ticker}: expected exactly one universe and instrument-master row")
        u = universe_rows.iloc[0].to_dict()
        scope = {key: serial(value) for key, value in instrument_rows.iloc[0].to_dict().items()}
        scope["cik"] = cik(scope["cik"])
        class_gate, class_reason = security_class_gate(scope)
        lifecycle_rows = lifecycle.loc[lifecycle["ticker"] == ticker]
        lifecycle_row = (
            {key: serial(value) for key, value in lifecycle_rows.iloc[0].to_dict().items()}
            if len(lifecycle_rows) == 1
            else {}
        )
        ticker_snapshots = snapshots.loc[snapshots["ticker"] == ticker].copy()
        figi = str(scope.get("share_class_figi") or "")
        identity_snapshots = ticker_snapshots.loc[ticker_snapshots["share_class_figi"].fillna("").eq(figi)] if figi else ticker_snapshots.loc[ticker_snapshots["cik"].map(cik).eq(scope["cik"])]
        identity_gate = "PASS" if not identity_snapshots.empty else "FAIL"
        interval_rows.append({
            "parent_universe_id": config["parent_universe_id"], "ticker": ticker,
            "instrument_id": scope["instrument_id"], "security_class_id": scope.get("share_class_figi"),
            "cik": scope["cik"], "security_name": scope.get("name"),
            "universe_first_seen_date": serial(u["first_seen_date"]),
            "universe_last_observed_date": serial(u["last_observed_date"]),
            "instrument_master_valid_from": scope.get("valid_from"), "instrument_master_valid_to": scope.get("valid_to"),
            "vendor_identity_first_snapshot": serial(identity_snapshots["snapshot_date"].min()) if not identity_snapshots.empty else None,
            "vendor_identity_last_snapshot": serial(identity_snapshots["snapshot_date"].max()) if not identity_snapshots.empty else None,
            "sec_legal_list_date": lifecycle_row.get("sec_legal_list_date"),
            "sec_legal_delist_date": lifecycle_row.get("sec_legal_delist_date"),
            "sec_exchange_end_candidate": lifecycle_row.get("sec_exchange_end_candidate"),
            "sec_boundary_state": lifecycle_row.get("sec_boundary_state"),
            "market_presence_first_session": lifecycle_row.get("market_first_daily_date"),
            "market_presence_last_session": lifecycle_row.get("market_last_daily_date"),
            "market_trade_presence_state": lifecycle_row.get("market_trade_presence_state"),
            "governed_interval_state": (
                lifecycle_row.get("comparison_state")
                or "CANDIDATE_REQUIRES_SEC_AND_MARKET_RECONCILIATION"
            ),
            "identity_gate": identity_gate, "security_class_gate": class_gate, "security_class_reason": class_reason,
        })

        inventory = pd.read_parquet(inventory_path(config, ticker))
        rows: list[dict[str, Any]] = []
        cik_candidates = [
            {key: serial(value) for key, value in row.items()}
            for row in instruments.loc[instruments["cik"].map(cik).eq(scope["cik"])].to_dict("records")
        ]
        for raw in inventory.to_dict("records"):
            row = {key: serial(value) for key, value in raw.items()}
            row["roles_v0_2"] = filing_roles_v0_2(record_from_row(row))
            row["temporal_scope_state"] = temporal_scope_state(row.get("filing_date"), u["first_seen_date"], u["last_observed_date"])
            link_state, candidates = accession_link_state(
                filing_cik=row.get("cik", ""), candidate_instruments=cik_candidates,
                filing_date=row.get("filing_date"),
            )
            row["accession_link_state"] = link_state
            row["candidate_instrument_ids"] = candidates
            rows.append(row)
            link_rows.append({
                "ticker_context": ticker, "accession_number": row.get("accession_number"),
                "filing_cik": cik(row.get("cik")), "filing_date": row.get("filing_date"),
                "temporal_scope_state": row["temporal_scope_state"], "link_state": link_state,
                "candidate_instrument_ids": candidates, "security_class_admission": "NOT_PROVEN_BY_METADATA",
            })
        plan = selection_plan_v0_2(rows, config.get("selection_capacity_documents"))
        for row in plan.selected:
            selected_rows.append({
                "ticker": ticker, "accession_number": row.get("accession_number"), "form": row.get("form"),
                "filing_date": row.get("filing_date"), "roles_v0_2": row.get("roles_v0_2"),
                "temporal_scope_state": row.get("temporal_scope_state"),
                "accession_link_state": row.get("accession_link_state"),
                "filing_size_bytes": row.get("filing_size_bytes"), "primary_document_url": row.get("primary_document_url"),
            })
        expected_class_ok = class_gate == case["expected_class_gate"]
        technical = "PASS" if identity_gate == "PASS" and plan.gate == "PASS" and expected_class_ok else "FAIL"
        acquisition = "HALT_SECURITY_CLASS" if class_gate == "FAIL" else ("ELIGIBLE_FOR_GOVERNED_REVIEW" if technical == "PASS" else "HALT_CONTROL_FAILURE")
        gate_rows.append({
            "ticker": ticker, "universe_gate": "PASS", "identity_gate": identity_gate,
            "security_class_gate": class_gate, "security_class_reason": class_reason,
            "expected_class_behavior": "PASS" if expected_class_ok else "FAIL",
            "inventory_count": len(rows), "required_document_count": plan.required_count,
            "selected_document_count": len(plan.selected), "selection_gate": plan.gate,
            "selection_reason": plan.reason, "technical_probe_gate": technical,
            "primary_document_acquisition_state": acquisition,
        })
        atomic_json(output / "heartbeat_latest.json", {"status": "RUNNING", "ticker": ticker, "observed_at_utc": utc_now()})

    intervals = pd.DataFrame(interval_rows).sort_values("ticker")
    links = pd.DataFrame(link_rows).sort_values(["ticker_context", "filing_date", "accession_number"])
    selected = pd.DataFrame(selected_rows).sort_values(["ticker", "filing_date", "accession_number"])
    gates = pd.DataFrame(gate_rows).sort_values("ticker")
    intervals.to_parquet(output / "instrument_identity_interval_ledger.parquet", index=False)
    links.to_parquet(output / "accession_instrument_link_candidates.parquet", index=False)
    selected.to_parquet(output / "document_selection_plan_v0_2.parquet", index=False)
    gates.to_parquet(output / "gate_matrix.parquet", index=False)
    gates.to_csv(output / "gate_matrix.csv", index=False)
    probe_gate = "PASS" if (gates["technical_probe_gate"] == "PASS").all() else "FAIL"
    final = {
        **manifest, "status": "COMPLETE" if probe_gate == "PASS" else "FAILED",
        "completed_at_utc": utc_now(), "case_count": len(gates), "probe_gate": probe_gate,
        "class_pass_count": int((gates["security_class_gate"] == "PASS").sum()),
        "expected_class_halt_count": int((gates["primary_document_acquisition_state"] == "HALT_SECURITY_CLASS").sum()),
        "selected_document_count": len(selected),
        "selected_filing_bytes_upper_bound": int(selected["filing_size_bytes"].fillna(0).sum()),
        "metadata_acquisition": "NOT_EXECUTED_REUSED_EXISTING_ARTIFACTS",
        "primary_document_acquisition": "NOT_EXECUTED",
        "download_authorization": "NOT_AUTHORIZED_PENDING_HUMAN_GATE",
        "parent_universe_scale": "NOT_AUTHORIZED",
        "target_snapshot_rows_sha256": hashlib.sha256(
            snapshots.to_json(orient="records", date_format="iso").encode("utf-8")
        ).hexdigest(),
        "output_artifacts": {
            name: sha256(output / name)
            for name in (
                "instrument_identity_interval_ledger.parquet",
                "accession_instrument_link_candidates.parquet",
                "document_selection_plan_v0_2.parquet",
                "gate_matrix.parquet",
                "gate_matrix.csv",
            )
        },
    }
    atomic_json(output / "final_manifest.json", final)
    atomic_json(output / "heartbeat_latest.json", {"status": final["status"], "observed_at_utc": utc_now(), "probe_gate": probe_gate})
    print(json.dumps(final, indent=2, default=str))
    return 0 if probe_gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
