"""Materialize neutral lifecycle observations from acquired SEC primary documents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.lifecycle_extract import extract_lifecycle_observation  # noqa: E402
from sec_pit.storage import append_jsonl, atomic_write_json  # noqa: E402

DEFAULT_ACQUISITION_RUN = Path(
    r"D:\TSIS\fundamental_context\sec_pit_v0_1\replays"
    r"\sec_pit_7t_lifecycle_primary_v0_1"
)
DEFAULT_OUTPUT_ROOT = Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(arguments: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *arguments],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquisition-run", type=Path, default=DEFAULT_ACQUISITION_RUN)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--source-metadata-run", type=Path)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    acquisition_run = args.acquisition_run.resolve()
    output_root = args.output_root.resolve()
    run_root = output_root / "replays" / args.run_id
    run_root.mkdir(parents=True, exist_ok=False)

    acquisition_manifest = json.loads(
        (acquisition_run / "final_manifest.json").read_text(encoding="utf-8")
    )
    source_metadata_run = (
        args.source_metadata_run.resolve()
        if args.source_metadata_run
        else Path(acquisition_manifest["source_run"])
    )
    gates = pd.read_parquet(source_metadata_run / "lifecycle_gate_matrix.parquet")
    plan_path = acquisition_run / "lifecycle_primary_acquisition_plan.parquet"
    result_path = acquisition_run / "lifecycle_primary_acquisition_results.parquet"
    plan = pd.read_parquet(plan_path)
    results = pd.read_parquet(result_path)
    source_rows = plan.merge(
        results[
            [
                "ticker",
                "accession_number",
                "sha256",
                "object_path",
                "bytes",
                "content_type",
                "status",
            ]
        ],
        on=["ticker", "accession_number"],
        how="inner",
        validate="one_to_one",
    )
    if len(source_rows) != len(plan):
        raise ValueError("Acquisition plan/result parity failed before extraction")
    if not source_rows["status"].eq("FETCHED").all():
        raise ValueError("All lifecycle source documents must be FETCHED")

    manifest: dict[str, Any] = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "command_line": sys.argv,
        "cwd": Path.cwd().as_posix(),
        "host": socket.gethostname(),
        "wrapper_pid": os.getpid(),
        "git_branch": git_value(["branch", "--show-current"]),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["status", "--porcelain"])),
        "acquisition_run": acquisition_run.as_posix(),
        "acquisition_final_manifest_sha256": sha256_file(
            acquisition_run / "final_manifest.json"
        ),
        "acquisition_plan_sha256": sha256_file(plan_path),
        "acquisition_results_sha256": sha256_file(result_path),
        "source_metadata_run": source_metadata_run.as_posix(),
        "input_document_count": len(source_rows),
        "output_root": output_root.as_posix(),
        "run_root": run_root.as_posix(),
        "overwrite_policy": "FORBIDDEN",
        "promotion_status": "NOT_AUTHORIZED",
        "success_criteria": (
            "one neutral observation per acquired document; no effective or "
            "first/last trade dates inferred"
        ),
    }
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": utc_now(),
            "expected_alive": True,
        },
    )

    first_seen = dict(
        zip(gates["ticker"].astype(str), gates["first_observed_snapshot"], strict=True)
    )
    observations: list[dict[str, Any]] = []
    mentions: list[dict[str, Any]] = []
    for index, source in enumerate(source_rows.to_dict("records"), start=1):
        observation, source_mentions = extract_lifecycle_observation(
            source,
            first_observed_snapshot=first_seen.get(str(source["ticker"])),
        )
        observations.append(observation)
        mentions.extend(source_mentions)
        heartbeat = {
            "run_id": args.run_id,
            "observed_at_utc": utc_now(),
            "status": "RUNNING",
            "stage": "EXTRACT_LIFECYCLE_PRIMARY",
            "wrapper_pid": os.getpid(),
            "completed": index,
            "total": len(source_rows),
            "ticker": source["ticker"],
            "accession_number": source["accession_number"],
        }
        atomic_write_json(run_root / "heartbeat_latest.json", heartbeat)
        append_jsonl(run_root / "heartbeat.jsonl", heartbeat)

    observation_frame = pd.DataFrame(observations)
    mention_frame = pd.DataFrame(mentions)
    observation_frame.to_parquet(
        run_root / "lifecycle_source_observations.parquet", index=False
    )
    mention_frame.to_parquet(
        run_root / "lifecycle_security_mentions.parquet", index=False
    )

    item_rows = observation_frame[
        observation_frame["candidate_type"].eq("ITEM_3_01_DISCLOSURE_CANDIDATE")
    ]
    hard_failures = {
        "observation_count_not_50": len(observation_frame) != 50,
        "duplicate_observations": bool(
            observation_frame.duplicated(["ticker", "accession_number"]).any()
        ),
        "missing_source_hash": bool(observation_frame["source_sha256"].isna().any()),
        "missing_evidence_snippet": bool(
            observation_frame["evidence_snippet"].fillna("").eq("").any()
        ),
        "resolved_effective_date_present": bool(
            observation_frame["event_effective_at"].notna().any()
        ),
        "resolved_first_trade_present": bool(
            observation_frame["first_trade_at"].notna().any()
        ),
        "resolved_last_trade_present": bool(
            observation_frame["last_trade_at"].notna().any()
        ),
        "cnobp_present": bool(observation_frame["ticker"].eq("CNOBP").any()),
        "item_301_section_missing": bool(
            (~item_rows["item_3_01_section_found"]).any()
        ),
    }
    status = "PASS_WITH_RESTRICTIONS" if not any(hard_failures.values()) else "FAIL"
    readout = {
        "run_id": args.run_id,
        "status": status,
        "observation_rows": len(observation_frame),
        "security_mention_rows": len(mention_frame),
        "rows_by_candidate_type": {
            str(key): int(value)
            for key, value in observation_frame.groupby("candidate_type").size().items()
        },
        "rows_by_identity_timing_state": {
            str(key): int(value)
            for key, value in observation_frame.groupby("identity_timing_state").size().items()
        },
        "rows_by_target_symbol_state": {
            str(key): int(value)
            for key, value in observation_frame.groupby("target_symbol_state").size().items()
        },
        "item_3_01_section_found": int(item_rows["item_3_01_section_found"].sum()),
        "hard_failures": hard_failures,
        "event_effective_at_nonnull": int(
            observation_frame["event_effective_at"].notna().sum()
        ),
        "first_trade_at_nonnull": int(
            observation_frame["first_trade_at"].notna().sum()
        ),
        "last_trade_at_nonnull": int(
            observation_frame["last_trade_at"].notna().sum()
        ),
        "market_presence_reconciliation": "NOT_EXECUTED",
        "canonical_promotion": "NOT_AUTHORIZED",
    }
    atomic_write_json(run_root / "lifecycle_extraction_readout.json", readout)
    final = {
        **manifest,
        **readout,
        "status": "COMPLETE" if status != "FAIL" else "FAILED",
        "completed_at_utc": utc_now(),
    }
    atomic_write_json(run_root / "final_manifest.json", final)
    atomic_write_json(
        run_root / "heartbeat_latest.json",
        {
            "run_id": args.run_id,
            "observed_at_utc": utc_now(),
            "status": final["status"],
            "stage": "EXTRACTION_COMPLETE" if status != "FAIL" else "EXTRACTION_FAILED",
            "wrapper_pid": os.getpid(),
            "completed": len(observation_frame),
            "total": len(source_rows),
        },
    )
    print(json.dumps(readout, indent=2))
    return 0 if status != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())