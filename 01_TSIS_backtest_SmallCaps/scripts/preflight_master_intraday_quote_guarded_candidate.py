from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATASET_ID = "master_intraday_bar_table_v0_2_candidate_quote_guarded"
PREFLIGHT_ID = "master_intraday_bar_table_v0_2_quote_guarded_preflight_v0_1"

DEFAULT_CONFIG = Path(
    "C:/TSIS_Data/01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/"
    "master_intraday_bar_table_quote_guarded_candidate_v0_2.json"
)
DEFAULT_OUTPUT_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/"
    "master_intraday_quote_guarded_candidate_preflight_v0_1"
)

REQUIRED_SAMPLE_COLUMNS = {
    "quote_guarded_view",
    "ticker",
    "ts_utc",
    "minute_utc",
    "minute_ny",
    "session_date",
    "repair_state",
    "repair_reason",
    "quote_guarded_repair_applied",
    "o_raw",
    "h_raw",
    "l_raw",
    "c_raw",
    "o_qg",
    "h_qg",
    "l_qg",
    "c_qg",
    "vw",
    "v",
    "n",
    "vw_quote_guarded_status",
    "quote_bid_floor",
    "quote_ask_cap",
    "quote_count",
    "source_ohlcv_path",
    "source_quotes_path",
    "manifest_created_at_utc",
    "run_root",
}

REQUIRED_ADDED_COLUMNS = {
    "quote_guarded_view",
    "quote_guarded_repair_applied",
    "repair_state",
    "repair_reason",
    "vw_quote_guarded_status",
    "quote_bid_floor",
    "quote_ask_cap",
    "quote_count",
    "source_quote_guarded_repair_manifest",
    "source_quote_guarded_run_id",
    "source_quotes_root",
    "source_quotes_root_state",
    "requires_rebuild_after_e_quotes_parity",
    "requires_rebuild_after_quote_guarded_e_promotion",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def _path_from_config(value: str) -> Path:
    return Path(value)


def run_preflight(config_path: Path, output_root: Path, created_at_utc: str | None = None) -> dict[str, Any]:
    cfg = _load_json(config_path)
    created_at = created_at_utc or _utc_now()
    failures: list[str] = []
    warnings: list[str] = []

    if cfg.get("dataset_id") != DATASET_ID:
        failures.append("dataset_id_mismatch")
    allowed_promotion_states = {
        "candidate_contract_defined_not_materialized",
        "scoped_candidate_materialized_not_official",
    }
    if cfg.get("promotion_state") not in allowed_promotion_states:
        failures.append("promotion_state_not_allowed")
    if cfg.get("official_dataset_created") is not False:
        failures.append("official_dataset_created_must_be_false")
    if cfg.get("safe_to_launch_full_materialization") is not False:
        failures.append("safe_to_launch_full_materialization_must_be_false")
    if cfg.get("full_universe_claim") is not False:
        failures.append("full_universe_claim_must_be_false")
    if cfg.get("raw_ohlcv_1m_mutation_allowed") is not False:
        failures.append("raw_ohlcv_1m_mutation_allowed_must_be_false")
    if cfg.get("creates_full_corrected_tree") is not False:
        failures.append("creates_full_corrected_tree_must_be_false")

    required_columns = set(cfg.get("required_added_columns", []))
    missing_required_added_columns = sorted(REQUIRED_ADDED_COLUMNS - required_columns)
    if missing_required_added_columns:
        failures.append("required_added_columns_missing")

    target = Path(cfg.get("target_dataset_path", ""))
    for forbidden_raw in cfg.get("must_not_write_paths", []):
        forbidden = Path(forbidden_raw)
        try:
            if target == forbidden or forbidden in target.parents:
                failures.append("target_inside_forbidden_path")
        except RuntimeError:
            failures.append("target_path_comparison_failed")

    bridge = cfg.get("current_bridge_sources", {})
    official = cfg.get("official_quote_guarded_sources", {})
    minute_root_raw = bridge.get("minute_root", "")
    quotes_root_raw = bridge.get("quotes_root", "")
    quote_guarded_root_raw = official.get("quote_guarded_output_root", bridge.get("output_root", ""))
    repair_manifest_raw = official.get("repair_manifest", bridge.get("official_quote_guarded_manifest", ""))
    repair_summary_raw = official.get("repair_summary", bridge.get("official_quote_guarded_summary", ""))
    repair_sample_raw = official.get("repair_sample", bridge.get("official_quote_guarded_sample", ""))
    consolidation_summary_raw = official.get("consolidation_summary", "")

    minute_root = _path_from_config(minute_root_raw)
    quotes_root = _path_from_config(quotes_root_raw)
    quote_guarded_root = _path_from_config(quote_guarded_root_raw)
    repair_manifest = _path_from_config(repair_manifest_raw)
    repair_summary = _path_from_config(repair_summary_raw)
    repair_sample = _path_from_config(repair_sample_raw)
    consolidation_summary = _path_from_config(consolidation_summary_raw)

    path_checks = {
        "minute_root_exists": bool(minute_root_raw) and minute_root.exists(),
        "quotes_root_exists": bool(quotes_root_raw) and quotes_root.exists(),
        "quote_guarded_root_exists": bool(quote_guarded_root_raw) and quote_guarded_root.exists(),
        "repair_manifest_exists": bool(repair_manifest_raw) and repair_manifest.exists(),
        "repair_summary_exists": bool(repair_summary_raw) and repair_summary.exists(),
        "repair_sample_exists": bool(repair_sample_raw) and repair_sample.exists(),
        "consolidation_summary_exists": bool(consolidation_summary_raw) and consolidation_summary.exists(),
    }
    for check, ok in path_checks.items():
        if not ok:
            failures.append(check.replace("_exists", "_missing"))

    summary: dict[str, Any] = {}
    consolidation: dict[str, Any] = {}
    if repair_summary.exists():
        summary = _load_json(repair_summary)
        if summary.get("status") != "PASS":
            failures.append("repair_summary_status_not_pass")
        if int(summary.get("manifest_rows", -1)) != int(official.get("manifest_rows", -2)):
            failures.append("repair_summary_manifest_rows_mismatch")
        if int(summary.get("completed_tickers", -1)) != int(official.get("completed_tickers", -2)):
            failures.append("repair_summary_completed_tickers_mismatch")
        if int(summary.get("missing_tickers", -1)) != int(official.get("missing_tickers", -2)):
            failures.append("repair_summary_missing_tickers_mismatch")
        if Path(summary.get("manifest_path", "")) != repair_manifest:
            failures.append("repair_summary_manifest_path_mismatch")
    if consolidation_summary.exists():
        consolidation = _load_json(consolidation_summary)
        if consolidation.get("status") != "PASS":
            failures.append("consolidation_summary_status_not_pass")
        if summary and consolidation.get("manifest_rows") != summary.get("manifest_rows"):
            failures.append("consolidation_summary_manifest_rows_mismatch")

    sample_columns: list[str] = []
    if repair_sample.exists():
        sample_columns = _read_csv_header(repair_sample)
        missing_sample_columns = sorted(REQUIRED_SAMPLE_COLUMNS - set(sample_columns))
        if missing_sample_columns:
            failures.append("repair_sample_required_columns_missing")
    else:
        missing_sample_columns = sorted(REQUIRED_SAMPLE_COLUMNS)

    if bridge.get("quotes_root_state") != "provisional_d_legacy_recovery_root_pending_e_parity":
        warnings.append("quotes_root_state_not_expected_provisional_value")
    if bridge.get("official_quote_guarded_root_state") != "promoted_manifest_available":
        failures.append("official_quote_guarded_root_state_not_promoted_manifest_available")
    if bridge.get("repair_run_state") != "PASS_promoted_lt1b_manifest":
        failures.append("repair_run_state_not_pass_promoted_lt1b_manifest")

    validations = {
        "validator_status": "passed" if not failures else "failed",
        "validator_hard_fail_count": len(failures),
        "validator_warning_count": len(warnings),
        "hard_failures": failures,
        "warnings": warnings,
        "path_checks": path_checks,
        "required_added_columns_missing": missing_required_added_columns,
        "repair_sample_required_columns_missing": missing_sample_columns,
        "repair_sample_column_count": len(sample_columns),
    }

    report = {
        "preflight_id": PREFLIGHT_ID,
        "dataset_id": DATASET_ID,
        "created_at_utc": created_at,
        "config_path": _as_posix(config_path),
        "materialization_scope": cfg.get("materialization_scope"),
        "promotion_state": cfg.get("promotion_state"),
        "full_universe_claim": cfg.get("full_universe_claim"),
        "official_dataset_created": cfg.get("official_dataset_created"),
        "safe_to_launch_full_materialization": cfg.get("safe_to_launch_full_materialization"),
        "storage_model": cfg.get("storage_model"),
        "raw_ohlcv_1m_root": _as_posix(minute_root),
        "quotes_root": _as_posix(quotes_root),
        "quotes_root_state": bridge.get("quotes_root_state"),
        "quote_guarded_output_root": _as_posix(quote_guarded_root),
        "repair_manifest": _as_posix(repair_manifest),
        "repair_summary": _as_posix(repair_summary),
        "repair_sample": _as_posix(repair_sample),
        "consolidation_summary": _as_posix(consolidation_summary),
        "repair_manifest_size_bytes": repair_manifest.stat().st_size if path_checks["repair_manifest_exists"] else None,
        "repair_summary_sha256": _sha256_file(repair_summary) if path_checks["repair_summary_exists"] else None,
        "repair_sample_sha256": _sha256_file(repair_sample) if path_checks["repair_sample_exists"] else None,
        "summary_status": summary.get("status"),
        "manifest_rows": summary.get("manifest_rows"),
        "universe_tickers": summary.get("universe_tickers"),
        "completed_tickers": summary.get("completed_tickers"),
        "missing_tickers": summary.get("missing_tickers"),
        "selected_repair_shards": summary.get("selected_repair_shards"),
        "skipped_out_scope_shards": summary.get("skipped_out_scope_shards"),
        "sample_columns": sample_columns,
        "validations": validations,
        "next_allowed_action": "builder_preflight_design_or_small_scope_candidate_only" if not failures else "fix_preflight_failures",
        "not_allowed_actions": [
            "overwrite_raw_ohlcv_1m",
            "write_into_master_intraday_bar_table_v0_1",
            "claim_full_universe_state_table",
            "enable_ml_rl_alphaevolve",
        ],
    }

    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / "master_intraday_quote_guarded_candidate_preflight_v0_1.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preflight master_intraday_bar_table_v0_2 quote-guarded candidate without materialization."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--created-at-utc", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    report = run_preflight(args.config, args.output_root, args.created_at_utc)
    print(json.dumps(report["validations"], indent=2))
    if report["validations"]["validator_status"] != "passed":
        raise SystemExit(1)
    print(f"Wrote {args.output_root / 'master_intraday_quote_guarded_candidate_preflight_v0_1.json'}")


if __name__ == "__main__":
    main()
