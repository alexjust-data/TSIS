"""Audit finalized TA-3 Binding A outputs against the governed v0.2 schema."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq


EXPECTED = {
    "current_state": {
        "eligible_trade_count",
        "eligible_share_volume",
        "eligible_dollar_volume",
        "trade_arrival_rate",
        "median_intertrade_duration_us",
        "p10_intertrade_duration_us",
        "largest_trade_volume_share",
        "active_subwindow_fraction",
        "max_subwindow_trade_share",
        "max_subwindow_volume_share",
        "consecutive_active_subwindows",
    },
    "multiscale_contrast": {"activity_rate_multiscale_log_ratio"},
    "pit_baseline_and_surprise": {
        "trade_count_percentile_pit",
        "share_volume_percentile_pit",
        "dollar_volume_percentile_pit",
        "arrival_rate_percentile_pit",
        "trade_count_log_ratio_to_pit",
        "share_volume_log_ratio_to_pit",
        "dollar_volume_log_ratio_to_pit",
        "intertrade_duration_compression",
    },
}

REQUIRED_METADATA = {
    "feature_spec_id",
    "feature_version",
    "binding_id",
    "scope_id",
    "instrument_id",
    "ticker",
    "decision_timestamp",
    "duplicate_policy_id",
    "trade_eligibility_policy_id",
    "latency_policy_id",
    "source_dataset_id",
    "source_schema_version",
    "market_calendar_build_run_id",
    "coverage_mode",
    "quality_state",
    "lineage_manifest_id",
    "future_window_used",
}


FAMILY_METADATA = {
    "current_state": {
        "window_seconds", "subwindow_seconds", "input_event_count",
        "feature_input_max_available_at", "observation_state", "calculation_state",
    },
    "multiscale_contrast": {"feature_input_max_available_at", "calculation_state"},
    "pit_baseline_and_surprise": {
        "window_seconds", "subwindow_seconds", "baseline_candidate_id",
        "feature_input_max_available_at", "calculation_state",
    },
}


def first_parquet(directory: Path) -> Path | None:
    return next(directory.rglob("*.parquet"), None) if directory.exists() else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifests = []
    for path in args.runtime_root.rglob("final_manifest.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") == "COMPLETE" and payload.get("output_run_root"):
            manifests.append((path, payload))

    schemas: dict[str, Counter[tuple[str, ...]]] = defaultdict(Counter)
    examples: dict[tuple[str, tuple[str, ...]], str] = {}
    completed = Counter()
    lineage_values = Counter()
    missing_output_roots = []

    for _, manifest in manifests:
        run_id = manifest["run_id"]
        completed[run_id.split("__")[0]] += 1
        output_root = Path(manifest["output_run_root"])
        if not output_root.exists():
            missing_output_roots.append(str(output_root))
            continue
        for family in EXPECTED:
            parquet = first_parquet(output_root / family)
            if parquet is None:
                continue
            parquet_file = pq.ParquetFile(parquet)
            schema = tuple(parquet_file.schema_arrow.names)
            schemas[family][schema] += 1
            examples.setdefault((family, schema), str(parquet))
            if family == "current_state":
                columns = [
                    "feature_spec_id",
                    "feature_version",
                    "binding_id",
                    "scope_id",
                    "future_window_used",
                ]
                row = parquet_file.read(columns=columns).slice(0, 1).to_pylist()[0]
                lineage_values[tuple(row[column] for column in columns)] += 1

    families = {}
    for family, expected in EXPECTED.items():
        variants = []
        union = set()
        intersection = None
        for schema, count in schemas[family].items():
            names = set(schema)
            union |= names
            intersection = names if intersection is None else intersection & names
            variants.append(
                {
                    "completed_blocks": count,
                    "columns": list(schema),
                    "sample_path": examples[(family, schema)],
                }
            )
        intersection = intersection or set()
        families[family] = {
            "schema_variant_count": len(variants),
            "variants": variants,
            "expected_feature_columns": sorted(expected),
            "present_in_every_variant": sorted(expected & intersection),
            "present_in_some_variant_only": sorted((expected & union) - intersection),
            "missing_from_every_variant": sorted(expected - union),
            "required_metadata_missing_from_every_variant": sorted(
                (REQUIRED_METADATA | FAMILY_METADATA[family]) - union
            ),
        }

    result = {
        "audit_status": "PROVISIONAL_WHILE_TA3_RUNNING",
        "audit_scope": "FINALIZED_BLOCKS_ONLY",
        "completed_manifest_count": len(manifests),
        "completed_by_parent_run": dict(sorted(completed.items())),
        "missing_output_roots": missing_output_roots,
        "lineage_values": [
            {
                "completed_blocks": count,
                "feature_spec_id": values[0],
                "feature_version": values[1],
                "binding_id": values[2],
                "scope_id": values[3],
                "future_window_used": values[4],
            }
            for values, count in lineage_values.items()
        ],
        "families": families,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

