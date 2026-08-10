"""Validate the frozen TA-3 sample before broad Binding A execution."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from run_trading_activity_ta3_binding_a import (
    OFFICIAL_TRADE_ROOT,
    atomic_json,
    load_and_verify_sample,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-manifest", required=True, type=Path)
    parser.add_argument("--base-config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def run(sample_manifest: Path, base_config_path: Path) -> dict[str, object]:
    manifest, paths = load_and_verify_sample(sample_manifest.resolve())
    base_config = json.loads(base_config_path.read_text(encoding="utf-8"))
    if base_config["sources"]["raw_trade_root"] != OFFICIAL_TRADE_ROOT:
        raise ValueError("Base config does not use the governed G trade root")

    blocks = pd.read_parquet(paths["blocks"])
    targets = pd.read_parquet(paths["targets"])
    scope = pd.read_parquet(paths["scope"])
    block_ids = set(blocks["block_id"])
    checks: dict[str, bool] = {
        "block_count_240": len(blocks) == 240 and len(block_ids) == 240,
        "target_count_2400": len(targets) == 2400,
        "scope_block_resolution": set(scope["block_id"]) == block_ids,
        "target_block_resolution": set(targets["block_id"]) == block_ids,
        "scope_block_session_unique": not scope.duplicated(
            ["block_id", "session_date"]
        ).any(),
        "ten_targets_per_block": targets.groupby("block_id").size().eq(10).all(),
    }

    source_paths = scope["source_path"].astype(str).str.replace("\\", "/", regex=False)
    checks["official_g_paths_only"] = source_paths.str.startswith(
        f"{OFFICIAL_TRADE_ROOT}/"
    ).all()
    declared_exists = scope["source_exists"].astype(bool)
    filesystem_exists = source_paths.map(lambda value: Path(value).is_file())
    filesystem_mismatch_rows = int((declared_exists != filesystem_exists).sum())
    checks["source_exists_matches_filesystem"] = filesystem_mismatch_rows == 0

    calendar = pd.read_parquet(base_config["sources"]["calendar_path"])
    calendar = calendar.loc[
        calendar["calendar"] == base_config["scope"]["calendar"]
    ].copy()
    calendar["session_date"] = pd.to_datetime(calendar["session_date"]).dt.date
    scope["session_date"] = pd.to_datetime(scope["session_date"]).dt.date
    noncontiguous: list[str] = []
    for block_id, block_scope in scope.groupby("block_id"):
        dates = set(block_scope["session_date"])
        expected = set(
            calendar.loc[
                (calendar["session_date"] >= min(dates))
                & (calendar["session_date"] <= max(dates)),
                "session_date",
            ]
        )
        if dates != expected:
            noncontiguous.append(str(block_id))
    checks["all_blocks_exact_xnys_ranges"] = not noncontiguous
    checks = {key: bool(value) for key, value in checks.items()}

    result: dict[str, object] = {
        "preflight_id": "trading_activity_ta3_binding_a_preflight_v0_1",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "sample_manifest": str(sample_manifest.resolve()),
        "official_trade_source_root": OFFICIAL_TRADE_ROOT,
        "legacy_root_fallback": "PROHIBITED",
        "metrics": {
            "blocks": int(len(blocks)),
            "targets": int(len(targets)),
            "scope_rows": int(len(scope)),
            "available_scope_rows": int(declared_exists.sum()),
            "unavailable_scope_rows": int((~declared_exists).sum()),
            "filesystem_mismatch_rows": filesystem_mismatch_rows,
            "noncontiguous_blocks": len(noncontiguous),
            "projected_binding_a_rows": manifest["summary"][
                "expected_binding_a_rows"
            ]["total"],
        },
        "checks": checks,
        "noncontiguous_block_sample": noncontiguous[:20],
        "preflight_gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion_status": "NOT_AUTHORIZED",
    }
    return result


def main() -> int:
    args = parse_args()
    result = run(args.sample_manifest, args.base_config)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, indent=2))
    return 0 if result["preflight_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
