#!/usr/bin/env python
"""Freeze the deterministic 4,824-instrument SEC PIT acquisition cohorts without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

UNIVERSE_COLUMNS = ("ticker", "first_seen_date", "last_observed_date", "status_rebuilt")
MASTER_COLUMNS = (
    "instrument_id",
    "ticker",
    "cik",
    "name",
    "primary_exchange",
    "share_class_figi",
    "is_common_stock",
    "active_in_reference",
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shard_for(instrument_id: str, count: int) -> int:
    return int(hashlib.sha256(instrument_id.encode()).hexdigest(), 16) % count


def atomic_json(path: Path, payload: Any) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=Path(__file__).resolve().parents[3], text=True
        ).strip()
    except Exception:
        return None


def build_acquisition_order(
    universe: pd.DataFrame,
    master: pd.DataFrame,
    *,
    expected_count: int,
    cohort_sizes: list[int],
    shard_count: int,
) -> pd.DataFrame:
    missing_universe = set(UNIVERSE_COLUMNS).difference(universe.columns)
    missing_master = set(MASTER_COLUMNS).difference(master.columns)
    if missing_universe or missing_master:
        raise ValueError(
            f"missing required columns: universe={sorted(missing_universe)} "
            f"master={sorted(missing_master)}"
        )
    if sum(cohort_sizes) != expected_count:
        raise ValueError("cohort sizes must sum exactly to the expected parent-universe count")
    if len(universe) != expected_count or universe["ticker"].nunique() != expected_count:
        raise ValueError(f"parent universe must contain exactly {expected_count:,} unique tickers")
    if universe[list(UNIVERSE_COLUMNS[:3])].isna().any().any():
        raise ValueError("ticker and universe dates must be complete")
    if master["ticker"].duplicated().any():
        raise ValueError("instrument master must contain one row per ticker")

    frame = universe[list(UNIVERSE_COLUMNS)].merge(
        master[list(MASTER_COLUMNS)], on="ticker", how="left", validate="one_to_one"
    )
    if frame[["instrument_id", "cik"]].isna().any().any():
        missing = frame.loc[
            frame[["instrument_id", "cik"]].isna().any(axis=1), "ticker"
        ].tolist()
        raise ValueError(f"every ticker requires instrument identity and CIK: {missing[:20]}")

    frame["first_seen_date"] = pd.to_datetime(frame["first_seen_date"], errors="raise")
    frame["last_observed_date"] = pd.to_datetime(frame["last_observed_date"], errors="raise")
    if frame["first_seen_date"].gt(frame["last_observed_date"]).any():
        raise ValueError("first_seen_date cannot be after last_observed_date")

    frame = frame.sort_values(
        ["last_observed_date", "ticker"], ascending=[False, True], kind="mergesort"
    ).reset_index(drop=True)
    frame.insert(0, "selection_order", range(1, len(frame) + 1))

    cohort_sequence: list[int] = []
    cohort_ids: list[str] = []
    cohort_orders: list[int] = []
    offset = 0
    for sequence, size in enumerate(cohort_sizes, start=1):
        cohort_sequence.extend([sequence] * size)
        cohort_ids.extend([f"C{sequence:02d}_{size:04d}"] * size)
        cohort_orders.extend(range(1, size + 1))
        offset += size
    if offset != len(frame):
        raise AssertionError("cohort assignment did not cover the complete frame")
    frame.insert(1, "cohort_sequence", cohort_sequence)
    frame.insert(2, "cohort_id", cohort_ids)
    frame.insert(3, "cohort_selection_order", cohort_orders)
    frame["download_priority_year"] = frame["last_observed_date"].dt.year.astype(int)
    frame["shard"] = frame["instrument_id"].map(
        lambda value: shard_for(str(value), shard_count)
    )
    frame["instrument_identity_group_size"] = (
        frame.groupby("instrument_id")["ticker"].transform("size").astype(int)
    )
    frame["instrument_identity_tickers_json"] = frame.groupby("instrument_id")[
        "ticker"
    ].transform(lambda values: json.dumps(sorted(set(values)), separators=(",", ":")))
    frame["instrument_identity_cik_count"] = (
        frame.groupby("instrument_id")["cik"].transform("nunique").astype(int)
    )
    frame["instrument_identity_reused_in_parent_universe"] = frame[
        "instrument_identity_group_size"
    ].gt(1)
    frame["instrument_identity_cik_conflict"] = frame[
        "instrument_identity_cik_count"
    ].gt(1)

    if not frame["last_observed_date"].is_monotonic_decreasing:
        raise AssertionError("global acquisition order is not date-descending")
    if frame["ticker"].duplicated().any():
        raise ValueError("the frozen acquisition order must be unique by ticker")
    return frame


def powershell_commands(
    *, output: Path, runtime_root: Path, object_root: Path, cohort_files: list[Path],
    requests_per_second: float, minimum_memory_gib: float,
) -> list[dict[str, Any]]:
    runner = Path(__file__).resolve().with_name("run_submissions_metadata_profile.py")
    monitor = Path(__file__).resolve().with_name("monitor_sec_pit_run.ps1")
    commands = []
    for sequence, cohort_path in enumerate(cohort_files, start=1):
        run_root = runtime_root / "metadata" / f"cohort_{sequence:02d}"
        base = (
            f'python "{runner}" --candidate-pool "{cohort_path}" '
            f'--output "{run_root}" --object-root "{object_root}" '
            f'--user-agent "$env:SEC_USER_AGENT" '
            f'--requests-per-second {requests_per_second:g} '
            f'--telemetry-interval-seconds 10 '
            f'--minimum-available-memory-gib {minimum_memory_gib:g}'
        )
        commands.append({
            "cohort_sequence": sequence,
            "cohort_path": cohort_path.as_posix(),
            "run_root": run_root.as_posix(),
            "launch_command": base,
            "resume_command": f"{base} --resume",
            "monitor_command": (
                f'& "{monitor}" -RunRoot "{run_root}" -Compact -IntervalSeconds 10'
            ),
            "safe_stop": "Ctrl+C in the launch terminal; then resume with the frozen cohort input",
            "launch_gate": "HUMAN_CONTROLLED_ONE_COHORT_AT_A_TIME",
        })
    return commands


def execute(config_path: Path, output: Path) -> Path:
    config_path = config_path.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"output exists; create a new versioned preflight: {output}")
    output.mkdir(parents=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_paths = {
        "parent_universe": Path(config["parent_universe_path"]).resolve(),
        "instrument_master": Path(config["instrument_master_path"]).resolve(),
    }
    pre_manifest = {
        "run_id": output.name,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "config_path": config_path.as_posix(),
        "config_sha256": sha256_file(config_path),
        "source_artifacts": {
            name: {"path": path.as_posix(), "sha256": sha256_file(path)}
            for name, path in source_paths.items()
        },
        "host": socket.gethostname(),
        "wrapper_pid": os.getpid(),
        "git_branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty_state": bool(git_value("status", "--porcelain")),
        "network_access": "PROHIBITED_AND_NOT_USED",
        "primary_document_download": "NOT_AUTHORIZED",
    }
    atomic_json(output / "pre_manifest.json", pre_manifest)

    universe = pd.read_parquet(source_paths["parent_universe"])
    master = pd.read_parquet(source_paths["instrument_master"])
    cohort_sizes = [int(value) for value in config["cohort_sizes"]]
    frame = build_acquisition_order(
        universe,
        master,
        expected_count=int(config["parent_universe_expected_count"]),
        cohort_sizes=cohort_sizes,
        shard_count=int(config["shard_count"]),
    )

    full_path = output / "full_universe_acquisition_order.parquet"
    frame.to_parquet(full_path, index=False)
    frame.to_csv(output / "full_universe_acquisition_order.csv", index=False)
    cohort_files: list[Path] = []
    summaries: list[dict[str, Any]] = []
    for sequence, size in enumerate(cohort_sizes, start=1):
        cohort = frame.loc[frame["cohort_sequence"].eq(sequence)].copy()
        cohort["selection_order"] = cohort["cohort_selection_order"]
        cohort_path = output / f"cohort_{sequence:02d}_{size:04d}.parquet"
        cohort.to_parquet(cohort_path, index=False)
        cohort.to_csv(cohort_path.with_suffix(".csv"), index=False)
        cohort_files.append(cohort_path)
        summaries.append({
            "cohort_sequence": sequence,
            "cohort_id": cohort["cohort_id"].iloc[0],
            "count": len(cohort),
            "global_order_first": int(frame.loc[frame["cohort_sequence"].eq(sequence), "selection_order"].min()),
            "global_order_last": int(frame.loc[frame["cohort_sequence"].eq(sequence), "selection_order"].max()),
            "newest_last_observed_date": cohort["last_observed_date"].max().date().isoformat(),
            "oldest_last_observed_date": cohort["last_observed_date"].min().date().isoformat(),
            "priority_year_counts": {
                str(year): int(count)
                for year, count in cohort["download_priority_year"].value_counts().sort_index(ascending=False).items()
            },
            "shard_counts": {
                str(shard): int(count)
                for shard, count in cohort["shard"].value_counts().sort_index().items()
            },
            "parquet_path": cohort_path.as_posix(),
            "parquet_sha256": sha256_file(cohort_path),
        })
    pd.DataFrame(summaries).to_json(output / "cohort_summary.json", orient="records", indent=2)

    commands = powershell_commands(
        output=output,
        runtime_root=Path(config["runtime_root"]).resolve(),
        object_root=Path(config["content_addressed_object_root"]).resolve(),
        cohort_files=cohort_files,
        requests_per_second=float(config["requests_per_second"]),
        minimum_memory_gib=float(config["minimum_available_memory_gib"]),
    )
    atomic_json(output / "operator_launch_plan.json", {
        "status": "AWAITING_HUMAN_LAUNCH",
        "launch_order": [1, 2, 3, 4, 5],
        "concurrency": 1,
        "environment_prerequisite": "SEC_USER_AGENT must identify the organization and contain a contact email",
        "commands": commands,
    })

    output_names = [
        "full_universe_acquisition_order.parquet",
        "full_universe_acquisition_order.csv",
        "cohort_summary.json",
        "operator_launch_plan.json",
        *[path.name for path in cohort_files],
        *[path.with_suffix(".csv").name for path in cohort_files],
    ]
    final = {
        **pre_manifest,
        "status": "COMPLETE",
        "completed_at_utc": utc_now(),
        "preflight_gate": "PASS",
        "parent_universe_count": len(frame),
        "unique_ticker_count": int(frame["ticker"].nunique()),
        "unique_instrument_count": int(frame["instrument_id"].nunique()),
        "reused_instrument_identity_row_count": int(
            frame["instrument_identity_reused_in_parent_universe"].sum()
        ),
        "reused_instrument_identity_group_count": int(
            frame.loc[
                frame["instrument_identity_reused_in_parent_universe"], "instrument_id"
            ].nunique()
        ),
        "instrument_identity_cik_conflict_row_count": int(
            frame["instrument_identity_cik_conflict"].sum()
        ),
        "cohort_sizes": cohort_sizes,
        "priority_order": config["priority_order"],
        "global_order_is_date_descending": bool(frame["last_observed_date"].is_monotonic_decreasing),
        "cohort_summaries": summaries,
        "metadata_download": "AWAITING_HUMAN_LAUNCH_COHORT_01",
        "primary_document_download": "NOT_AUTHORIZED_PENDING_METADATA_SELECTION_AND_COHORT_GATE",
        "automatic_promotion": "NOT_AUTHORIZED",
        "network_requests": 0,
        "next_gate": "HUMAN_LAUNCH_AND_REVIEW_METADATA_COHORT_01",
        "output_artifacts": {
            name: sha256_file(output / name) for name in output_names
        },
    }
    atomic_json(output / "final_manifest.json", final)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    print(execute(arguments.config, arguments.output))
