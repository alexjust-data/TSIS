"""Certify finalized Binding A shard probes before broad materialization."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


def parquet_files(root: Path, family: str) -> list[Path]:
    return sorted((root / family).rglob("*.parquet"))


def read_family(root: Path, family: str) -> pd.DataFrame:
    frames = [pq.ParquetFile(path).read().to_pandas() for path in parquet_files(root, family)]
    if not frames:
        raise ValueError(f"No {family} parquet files under {root}")
    return pd.concat(frames, ignore_index=True)


def assert_close(left: pd.Series, right: pd.Series, label: str) -> None:
    mask = left.notna() & right.notna()
    if not mask.any():
        return
    difference = (left.loc[mask].astype(float) - right.loc[mask].astype(float)).abs()
    if (difference > 1e-12).any():
        raise AssertionError(f"{label}: max difference {difference.max()}")


def validate_run(root: Path) -> dict:
    current = read_family(root, "current_state")
    multiscale = read_family(root, "multiscale_contrast")
    baseline = read_family(root, "pit_baseline_and_surprise")

    expected_identity = {
        "feature_spec_id": "trading_activity_binding_a_exact_specification",
        "feature_version": "v0_2",
        "binding_id": "trading_activity_binding_a_candidate_v0_2",
        "duplicate_policy_id": "PRESERVE_EXACT_DUPLICATES_PRIMARY_V0_1",
        "coverage_mode": "INFERRED_FROM_SUCCESSFUL_FULL_RTH_REQUEST",
    }
    for family_name, frame in (
        ("current_state", current),
        ("multiscale_contrast", multiscale),
        ("pit_baseline_and_surprise", baseline),
    ):
        for column, expected in expected_identity.items():
            values = set(frame[column].dropna().astype(str))
            if values != {expected}:
                raise AssertionError(f"{family_name}.{column}: {values}")
        if frame["future_window_used"].fillna(True).any():
            raise AssertionError(f"{family_name}: future_window_used")

    calculated = current["calculation_state"].eq("CALCULATED")
    assert_close(
        current.loc[calculated, "trade_arrival_rate"],
        current.loc[calculated, "eligible_trade_count"]
        / current.loc[calculated, "window_seconds"],
        "trade_arrival_rate",
    )
    for column in (
        "eligible_trade_count",
        "eligible_share_volume",
        "eligible_dollar_volume",
        "trade_arrival_rate",
        "median_intertrade_duration_us",
        "p10_intertrade_duration_us",
    ):
        values = pd.to_numeric(current[column], errors="coerce").dropna()
        if (values < 0).any():
            raise AssertionError(f"negative {column}")
    for column in (
        "largest_trade_volume_share",
        "active_subwindow_fraction",
        "max_subwindow_trade_share",
        "max_subwindow_volume_share",
    ):
        values = pd.to_numeric(current[column], errors="coerce").dropna()
        if ((values < 0) | (values > 1)).any():
            raise AssertionError(f"out-of-range {column}")

    current_index = current.set_index(["decision_timestamp", "window_seconds"])
    expected_ratios = []
    for row in multiscale.itertuples(index=False):
        short = current_index.loc[(row.decision_timestamp, row.short_window_seconds)]
        long = current_index.loc[(row.decision_timestamp, row.long_window_seconds)]
        epsilon = 1.0 / float(row.long_window_seconds)
        expected_ratios.append(
            math.log(
                (float(short.trade_arrival_rate) + epsilon)
                / (float(long.trade_arrival_rate) + epsilon)
            )
            if pd.notna(short.trade_arrival_rate) and pd.notna(long.trade_arrival_rate)
            else math.nan
        )
    assert_close(
        multiscale["activity_rate_multiscale_log_ratio"],
        pd.Series(expected_ratios, index=multiscale.index),
        "activity_rate_multiscale_log_ratio",
    )

    baseline_current = baseline.merge(
        current[
            ["decision_timestamp", "window_seconds", "median_intertrade_duration_us"]
        ],
        on=["decision_timestamp", "window_seconds"],
        how="left",
        validate="many_to_one",
    )
    expected_compression = (
        (baseline_current["baseline_median_intertrade_duration_us"] + 1.0)
        / (baseline_current["median_intertrade_duration_us"] + 1.0)
    ).map(lambda value: math.log(value) if pd.notna(value) else math.nan)
    assert_close(
        baseline_current["intertrade_duration_compression"],
        expected_compression,
        "intertrade_duration_compression",
    )
    expected_null = (
        baseline_current["baseline_median_intertrade_duration_us"].isna()
        | baseline_current["median_intertrade_duration_us"].isna()
    )
    if not baseline_current.loc[expected_null, "intertrade_duration_compression"].isna().all():
        raise AssertionError("duration compression missingness mismatch")

    return {
        "current_state_rows": len(current),
        "multiscale_rows": len(multiscale),
        "baseline_rows": len(baseline),
        "duration_compression_non_null_rows": int(
            baseline["intertrade_duration_compression"].notna().sum()
        ),
        "status": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    results = []
    schemas: dict[str, set[tuple[tuple[str, str], ...]]] = {
        "current_state": set(),
        "multiscale_contrast": set(),
        "pit_baseline_and_surprise": set(),
    }
    for final_path in sorted(args.runtime_root.glob("*/final_manifest.json")):
        final = json.loads(final_path.read_text(encoding="utf-8"))
        if final.get("final_status") != "COMPLETE":
            continue
        for completed in final["completed_blocks"]:
            block_final = (
                final_path.parent
                / "blocks"
                / completed["block_run_id"]
                / "final_manifest.json"
            )
            block = json.loads(block_final.read_text(encoding="utf-8"))
            output_root = Path(block["output_run_root"])
            for family in schemas:
                sample = parquet_files(output_root, family)[0]
                schema = pq.ParquetFile(sample).schema_arrow
                schemas[family].add(tuple((field.name, str(field.type)) for field in schema))
            results.append(
                {
                    "parent_run_id": final["run_id"],
                    "block_run_id": completed["block_run_id"],
                    **validate_run(output_root),
                }
            )

    if len(results) != 4:
        raise AssertionError(f"Expected four completed shard probes, got {len(results)}")
    schema_variants = {family: len(values) for family, values in schemas.items()}
    if any(count != 1 for count in schema_variants.values()):
        raise AssertionError(f"Cross-shard schema mismatch: {schema_variants}")

    payload = {
        "status": "PASS",
        "certification_scope": "FOUR_SHARD_BOUNDED_PRODUCTION_EQUIVALENT_PROBES",
        "schema_variants": schema_variants,
        "results": results,
        "broad_materialization_authorized_by_this_artifact": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
