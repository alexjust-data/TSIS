from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import yaml

from .certify import EXPECTED_KEYS
from .manifest_lineage import sha256_file, verify_artifacts
from .quality_certification import certify_outcome_quality, certify_partition_schemas
from .scope_certification import certify_exact_scope_and_sources


FINAL_DERIVED_KEYS = {
    "coverage_by_year": ["year"],
    "case_index": ["episode_id"],
    "activation_case_index": ["activation_case_id"],
    "activation_event_statistics": ["activation_family", "activation_label", "event_label"],
    "cohort_statistics": ["activation_family", "activation_label", "offset_session"],
    "cycle_cohort_statistics": ["activation_family", "activation_label", "offset_session"],
}


def certify_run(run_root: Path, config_path: Path, mode: str) -> dict:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    forbidden_terms = tuple(config["statistics"]["forbidden_terms"]) + (
        "future_split_factor",
    )
    final_root = run_root / "final"
    manifest = json.loads((final_root / "run_manifest.json").read_text(encoding="utf-8"))
    checks: dict[str, dict] = {}
    overall = True
    for table_name, keys in EXPECTED_KEYS.items():
        path = final_root / f"{table_name}.parquet"
        schema_names = pq.ParquetFile(path).schema_arrow.names
        key_frame = pd.read_parquet(path, columns=keys)
        duplicate_keys = int(key_frame.duplicated(keys).sum())
        null_keys = int(key_frame[keys].isna().any(axis=1).sum())
        forbidden = sorted(
            name for name in schema_names if any(term in name.lower() for term in forbidden_terms)
        )
        passed = duplicate_keys == 0 and null_keys == 0 and not forbidden
        overall = overall and passed
        checks[table_name] = {
            "rows": int(pq.ParquetFile(path).metadata.num_rows),
            "duplicate_keys": duplicate_keys,
            "null_keys": null_keys,
            "forbidden_columns": forbidden,
            "status": "pass" if passed else "fail",
        }

    for table_name, keys in FINAL_DERIVED_KEYS.items():
        path = final_root / f"{table_name}.parquet"
        schema_names = pq.ParquetFile(path).schema_arrow.names
        key_frame = pd.read_parquet(path, columns=keys)
        duplicate_keys = int(key_frame.duplicated(keys).sum())
        null_keys = int(key_frame[keys].isna().any(axis=1).sum())
        forbidden = sorted(
            name for name in schema_names
            if any(term in name.lower() for term in forbidden_terms)
        )
        passed = duplicate_keys == 0 and null_keys == 0 and not forbidden
        overall = overall and passed
        checks[table_name] = {
            "rows": int(pq.ParquetFile(path).metadata.num_rows),
            "duplicate_keys": duplicate_keys,
            "null_keys": null_keys,
            "forbidden_columns": forbidden,
            "status": "pass" if passed else "fail",
        }

    sessions_path = final_root / "session_observables.parquet"
    universe = pd.read_parquet(sessions_path, columns=["ticker", "date"])
    expected_tickers = int(config["scope"]["expected_tickers"])
    expected_rows = int(config["scope"]["expected_raw_rows"])
    scope_checks = {
        "observed_tickers": int(universe["ticker"].nunique()),
        "observed_rows": int(len(universe)),
        "min_date": str(pd.to_datetime(universe["date"]).min().date()),
        "max_date": str(pd.to_datetime(universe["date"]).max().date()),
    }
    if mode == "full":
        scope_pass = (
            scope_checks["observed_tickers"] == expected_tickers
            and scope_checks["observed_rows"] == expected_rows
        )
    else:
        scope_pass = scope_checks["observed_tickers"] > 0 and scope_checks["observed_rows"] > 0
    overall = overall and scope_pass
    checks["scope"] = {**scope_checks, "status": "pass" if scope_pass else "fail"}

    schema_equivalence = certify_partition_schemas(run_root)
    outcome_quality = certify_outcome_quality(final_root)
    checks["partition_schema_equivalence"] = schema_equivalence
    checks["outcome_quality"] = outcome_quality

    exact_scope = certify_exact_scope_and_sources(
        final_root, Path(config["data"]["universe_activity_path"]), mode
    )
    artifact_integrity = verify_artifacts(manifest.get("artifacts", {}))
    lineage = manifest.get("lineage", {})
    upstream_path = Path(lineage.get("upstream_audit_manifest", "__missing__"))
    lineage_violations = {
        "missing_code_commit": int(not bool(lineage.get("code_commit"))),
        "config_hash_mismatch": int(
            lineage.get("config_sha256") != sha256_file(config_path)
        ),
        "upstream_manifest_missing": int(not upstream_path.exists()),
        "upstream_hash_mismatch": int(
            upstream_path.exists()
            and lineage.get("upstream_audit_manifest_sha256") != sha256_file(upstream_path)
        ),
    }
    lineage_integrity = {
        "status": "pass" if not any(lineage_violations.values()) else "fail",
        "violations": lineage_violations,
    }
    checks["exact_scope_and_sources"] = exact_scope
    checks["artifact_integrity"] = artifact_integrity
    checks["lineage_integrity"] = lineage_integrity
    overall = (
        overall
        and schema_equivalence["status"] == "pass"
        and outcome_quality["status"] == "pass"
        and exact_scope["status"] == "pass"
        and artifact_integrity["status"] == "pass"
        and lineage_integrity["status"] == "pass"
    )

    result = {
        "status": "pass" if overall else "fail",
        "mode": mode,
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path.resolve()),
        "run_manifest": str((final_root / "run_manifest.json").resolve()),
        "checks": checks,
    }
    (final_root / "terminal_certification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    readout = [
        "# Daily Pattern Atlas Certification",
        "",
        f"Status: `{result['status']}`  ",
        f"Mode: `{mode}`  ",
        f"Certified at: `{result['certified_at']}`",
        "",
        "## Checks",
        "",
    ]
    for name, check in checks.items():
        readout.append(f"- `{name}`: `{check['status']}`")
    (final_root / "certification_readout.md").write_text("\n".join(readout) + "\n", encoding="utf-8")
    manifest["status"] = "pass" if overall else "fail"
    manifest["terminal_certification"] = str((final_root / "terminal_certification.json").resolve())
    (final_root / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--mode", choices=("probe", "full"), required=True)
    args = parser.parse_args()
    result = certify_run(args.run_root.resolve(), args.config.resolve(), args.mode)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
