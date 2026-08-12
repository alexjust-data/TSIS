#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sec_pit import build_stratified_owner_case_configs
from sec_pit import run_no_network_os_probe
from sec_pit import run_no_network_owner_exclusion_probe
from sec_pit.storage import append_jsonl, atomic_write_json


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_complete(path: Path, allowed_statuses: set[str]) -> bool:
    if not path.is_file():
        return False
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("status") in allowed_statuses
    except (OSError, ValueError, TypeError):
        return False


def configs_complete(path: Path, expected_tickers: set[str]) -> bool:
    index_path = path / "index.json"
    if not index_path.is_file():
        return False
    try:
        rows = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return False
    ready = {str(row["ticker"]) for row in rows if row.get("status") == "READY"}
    if ready != expected_tickers:
        return False
    return all(
        Path(str(row["config_path"])).is_file()
        and file_sha256(Path(str(row["config_path"]))) == row.get("config_sha256")
        for row in rows
        if row.get("status") == "READY"
    )


def quarantine_incomplete(path: Path, batch_root: Path) -> Path:
    resolved = path.resolve()
    output_root = batch_root.parent.parent.resolve()
    if not resolved.is_relative_to(output_root):
        raise ValueError(f"refusing to move outside governed output root: {resolved}")
    quarantine = batch_root / "incomplete_runs"
    quarantine.mkdir(parents=True, exist_ok=True)
    destination = quarantine / f"{path.name}__{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}"
    shutil.move(str(path), str(destination))
    return destination


def execute(
    *,
    config_path: Path,
    probe_root: Path,
    acquisition_ledger: Path,
    output_root: Path,
    run_id: str,
    resume: bool,
    companyfacts_observations: Path | None = None,
) -> Path:
    config_path = config_path.resolve()
    probe_root = probe_root.resolve()
    acquisition_ledger = acquisition_ledger.resolve()
    output_root = output_root.resolve()
    companyfacts_observations = (
        companyfacts_observations.resolve()
        if companyfacts_observations is not None
        else None
    )
    if (
        companyfacts_observations is not None
        and not companyfacts_observations.is_file()
    ):
        raise FileNotFoundError(companyfacts_observations)
    batch_root = output_root / "batches" / run_id
    cases = json.loads((probe_root / "case_matrix.json").read_text(encoding="utf-8"))
    eligible = sorted(
        (row for row in cases if row.get("probe_gate") == "ELIGIBLE"),
        key=lambda row: str(row["ticker"]),
    )
    tickers = [str(row["ticker"]) for row in eligible]
    components = [
        Path(__file__).resolve(),
        Path(run_no_network_os_probe.__file__).resolve(),
        Path(run_no_network_owner_exclusion_probe.__file__).resolve(),
        Path(build_stratified_owner_case_configs.__file__).resolve(),
    ]
    identity = {
        "config_path": config_path.as_posix(),
        "config_sha256": file_sha256(config_path),
        "probe_root": probe_root.as_posix(),
        "probe_manifest_sha256": file_sha256(probe_root / "final_manifest.json"),
        "acquisition_ledger": acquisition_ledger.as_posix(),
        "acquisition_ledger_sha256": file_sha256(acquisition_ledger),
        "companyfacts_observations": (
            companyfacts_observations.as_posix()
            if companyfacts_observations is not None
            else None
        ),
        "companyfacts_observations_sha256": (
            file_sha256(companyfacts_observations)
            if companyfacts_observations is not None
            else None
        ),
        "component_sha256": {path.name: file_sha256(path) for path in components},
        "eligible_tickers": tickers,
    }
    pre_path = batch_root / "pre_manifest.json"
    if batch_root.exists():
        if not resume or not pre_path.is_file():
            raise FileExistsError(batch_root)
        prior = json.loads(pre_path.read_text(encoding="utf-8"))
        if any(prior.get(key) != value for key, value in identity.items()):
            raise ValueError("resume identity mismatch; create a new versioned batch")
    else:
        batch_root.mkdir(parents=True)
        atomic_write_json(
            pre_path,
            {
                "run_id": run_id,
                "created_at_utc": utc_now(),
                "status": "RUNNING",
                "mode": "NO_NETWORK_LOCAL_RESOLUTION_BATCH",
                "network_requests_authorized": False,
                "wrapper_pid": os.getpid(),
                **identity,
            },
        )
        atomic_write_json(batch_root / "pid_manifest.json", {"wrapper_pid": os.getpid(), "created_at_utc": utc_now()})

    state: dict[str, Any] = {
        "status": "RUNNING",
        "stage": "OS_RESOLUTION",
        "total_cases": len(tickers),
        "os_completed": 0,
        "owner_completed": 0,
        "current_ticker": None,
        "failed": 0,
    }

    def heartbeat() -> None:
        virtual = psutil.virtual_memory()
        payload = {
            **state,
            "observed_at_utc": utc_now(),
            "wrapper_pid": os.getpid(),
            "wrapper_alive": psutil.pid_exists(os.getpid()),
            "system_cpu_percent": psutil.cpu_percent(interval=None),
            "available_memory_gib": virtual.available / (1024**3),
            "process_rss_gib": psutil.Process().memory_info().rss / (1024**3),
        }
        atomic_write_json(batch_root / "heartbeat_latest.json", payload)
        append_jsonl(batch_root / "heartbeat.jsonl", payload)

    os_template = f"{run_id}__os__{{ticker_lower}}"
    owner_template = f"{run_id}__owner__{{ticker_lower}}"
    try:
        heartbeat()
        for ticker in tickers:
            state["current_ticker"] = ticker
            heartbeat()
            case_run_id = os_template.format(ticker_lower=ticker.lower())
            case_root = output_root / "runs" / case_run_id
            final_path = case_root / "final_manifest.json"
            if not manifest_complete(final_path, {"COMPLETE"}):
                if case_root.exists():
                    quarantine_incomplete(case_root, batch_root)
                run_no_network_os_probe.execute(
                    config_path=config_path,
                    probe_root=probe_root,
                    acquisition_ledger=acquisition_ledger,
                    ticker=ticker,
                    output_root=output_root,
                    run_id=case_run_id,
                    companyfacts_observations=companyfacts_observations,
                )
            state["os_completed"] += 1
            heartbeat()

        state["stage"] = "OWNER_CONFIGS"
        heartbeat()
        configs_name = f"owner_case_configs__{run_id}"
        configs_path = probe_root / configs_name
        expected = set(tickers)
        if not configs_complete(configs_path, expected):
            if configs_path.exists():
                quarantine_incomplete(configs_path, batch_root)
            build_stratified_owner_case_configs.execute(
                config_path=config_path,
                probe_root=probe_root,
                acquisition_ledger=acquisition_ledger,
                os_output_root=output_root,
                os_run_template=os_template,
                owner_output_root=output_root,
                output_directory_name=configs_name,
            )
        index = json.loads((configs_path / "index.json").read_text(encoding="utf-8"))
        config_by_ticker = {
            str(row["ticker"]): Path(str(row["config_path"]))
            for row in index
            if row.get("status") == "READY"
        }

        state["stage"] = "OWNER_EXCLUSION_RESOLUTION"
        for ticker in tickers:
            state["current_ticker"] = ticker
            heartbeat()
            case_run_id = owner_template.format(ticker_lower=ticker.lower())
            case_root = output_root / "runs" / case_run_id
            final_path = case_root / "final_manifest.json"
            if not manifest_complete(
                final_path,
                {"COMPLETE_EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING", "COMPLETE_WITH_BLOCKERS"},
            ):
                if case_root.exists():
                    quarantine_incomplete(case_root, batch_root)
                run_no_network_owner_exclusion_probe.execute(config_by_ticker[ticker], case_run_id)
            state["owner_completed"] += 1
            heartbeat()

        state.update({"status": "COMPLETE", "stage": "FINAL", "current_ticker": None})
        final = {
            **json.loads(pre_path.read_text(encoding="utf-8")),
            **state,
            "ended_at_utc": utc_now(),
            "os_run_template": os_template,
            "owner_run_template": owner_template,
            "owner_configs_path": configs_path.as_posix(),
            "network_requests": 0,
        }
        atomic_write_json(batch_root / "final_manifest.json", final)
        heartbeat()
        return batch_root
    except Exception as exc:
        state.update({"status": "FAILED", "stage": "FINAL", "failed": 1, "failure_reason": f"{type(exc).__name__}: {exc}"})
        atomic_write_json(batch_root / "final_manifest.json", {**json.loads(pre_path.read_text(encoding="utf-8")), **state, "ended_at_utc": utc_now()})
        heartbeat()
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--acquisition-ledger", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--companyfacts-observations", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(
        config_path=args.config,
        probe_root=args.probe_root,
        acquisition_ledger=args.acquisition_ledger,
        output_root=args.output_root,
        run_id=args.run_id,
        resume=args.resume,
        companyfacts_observations=args.companyfacts_observations,
    ))
