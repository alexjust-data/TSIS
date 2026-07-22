from __future__ import annotations

import argparse
import json
import runpy
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


SCRIPT_00 = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\00_load_quotes_run_artifacts.py")

STAGE_ORDER = [
    "snapshot",
    "root_cause",
    "concentration",
    "microstructure",
    "focus_examples",
    "forensic",
    "taxonomy",
    "case_index",
    "crossed_gap_severity",
    "positive_cross_review",
    "manifest",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _progress_path(cache_dir: Path) -> Path:
    return cache_dir / "build_progress_cd_lt1b.json"


def _load_progress(cache_dir: Path, refresh: bool) -> dict:
    path = _progress_path(cache_dir)
    if refresh or not path.exists():
        return {
            "builder_version": "quotes_cd_lt1b_v2_resume",
            "status": "initialized",
            "updated_utc": _utc_now(),
            "stages": {stage: {"status": "pending"} for stage in STAGE_ORDER},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _write_progress(cache_dir: Path, progress: dict) -> None:
    progress["updated_utc"] = _utc_now()
    _progress_path(cache_dir).write_text(json.dumps(progress, indent=2), encoding="utf-8")


def _stage_completed(progress: dict, stage: str) -> bool:
    return progress.get("stages", {}).get(stage, {}).get("status") == "completed"


def _must_recompute(stage: str, progress: dict, refresh: bool, from_stage: str | None) -> bool:
    if refresh:
        return True
    if from_stage is not None and STAGE_ORDER.index(stage) >= STAGE_ORDER.index(from_stage):
        return True
    return not _stage_completed(progress, stage)


def _refresh_flag(args: argparse.Namespace) -> bool:
    return bool(args.refresh or args.from_stage is not None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build quotes C+D <1B> notebook artifacts without loading the full parquet in Jupyter.")
    parser.add_argument("--refresh", action="store_true", help="Rebuild artifacts even if cached.")
    parser.add_argument("--from-stage", choices=STAGE_ORDER, default=None, help="Recompute from this stage onward, reusing previous completed stages before it.")
    args = parser.parse_args()

    mod00 = runpy.run_path(str(SCRIPT_00))
    payload = mod00["load_quotes_artifacts"]()
    handle = payload["quotes_handle_cd"]
    progress = _load_progress(handle.cache_dir, refresh=args.refresh)
    progress.update(
        {
            "status": "running",
            "cache_dir": str(handle.cache_dir),
            "source_parquet": str(handle.path),
            "source_rows_full": int(handle.row_count()),
            "target_lt1b_path": None if handle.target_path is None else str(handle.target_path),
            "target_lt1b_tickers": None if handle.target_tickers is None else len(handle.target_tickers),
        }
    )
    _write_progress(handle.cache_dir, progress)

    t0 = perf_counter()
    artifacts: dict[str, object] = {}

    if not _must_recompute("snapshot", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "snapshot_artifacts_lt1b", "status": "resume_skip"}))
        snapshot_payload = mod00["build_snapshot_artifacts_cached"](handle, refresh=False)
    else:
        progress["current_stage"] = "snapshot"
        progress["stages"]["snapshot"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "snapshot_artifacts_lt1b", "status": "started"}))
        snapshot_payload = mod00["build_snapshot_artifacts_cached"](handle, refresh=_refresh_flag(args))
        progress["stages"]["snapshot"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "snapshot_artifacts_lt1b", "status": "completed"}))
    artifacts.update(snapshot_payload)

    if not _must_recompute("root_cause", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "root_cause_artifacts_lt1b", "status": "resume_skip"}))
        root_payload = mod00["build_root_cause_outputs_cached"](handle, refresh=False)
    else:
        progress["current_stage"] = "root_cause"
        progress["stages"]["root_cause"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "root_cause_artifacts_lt1b", "status": "started"}))
        root_payload = mod00["build_root_cause_outputs_cached"](handle, refresh=_refresh_flag(args))
        progress["stages"]["root_cause"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "root_cause_artifacts_lt1b", "status": "completed"}))
    artifacts.update(root_payload)

    if not _must_recompute("concentration", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "concentration_artifacts_lt1b", "status": "resume_skip"}))
        concentration_payload = mod00["build_concentration_artifacts_cached"](handle, top_n=30, refresh=False)
    else:
        progress["current_stage"] = "concentration"
        progress["stages"]["concentration"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "concentration_artifacts_lt1b", "status": "started"}))
        concentration_payload = mod00["build_concentration_artifacts_cached"](handle, top_n=30, refresh=_refresh_flag(args))
        progress["stages"]["concentration"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "concentration_artifacts_lt1b", "status": "completed"}))
    artifacts.update(concentration_payload)

    if not _must_recompute("microstructure", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "microstructure_artifacts_lt1b", "status": "resume_skip"}))
        micro_payload = mod00["build_microstructure_outputs_cached"](handle, sample_max_n=250_000, top_n=25, random_state=7, refresh=False)
    else:
        progress["current_stage"] = "microstructure"
        progress["stages"]["microstructure"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "microstructure_artifacts_lt1b", "status": "started"}))
        micro_payload = mod00["build_microstructure_outputs_cached"](handle, sample_max_n=250_000, top_n=25, random_state=7, refresh=_refresh_flag(args))
        progress["stages"]["microstructure"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "microstructure_artifacts_lt1b", "status": "completed"}))
    artifacts.update(micro_payload)

    if not _must_recompute("focus_examples", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "focus_examples_artifacts_lt1b", "status": "resume_skip"}))
        focus_issue, focus_warn, issue_examples, warn_examples = mod00["build_focus_examples_cached"](
            handle, root_payload["hard_issue_counts"], root_payload["warn_counts"], top_n=20, refresh=False
        )
    else:
        progress["current_stage"] = "focus_examples"
        progress["stages"]["focus_examples"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "focus_examples_artifacts_lt1b", "status": "started"}))
        focus_issue, focus_warn, issue_examples, warn_examples = mod00["build_focus_examples_cached"](
            handle,
            root_payload["hard_issue_counts"],
            root_payload["warn_counts"],
            top_n=20,
            refresh=_refresh_flag(args),
        )
        progress["stages"]["focus_examples"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "focus_examples_artifacts_lt1b", "status": "completed"}))
    artifacts.update(
        {
            "focus_issue": focus_issue,
            "focus_warn": focus_warn,
            "issue_examples": issue_examples,
            "warn_examples": warn_examples,
        }
    )

    if not _must_recompute("forensic", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "forensic_artifacts_lt1b", "status": "resume_skip"}))
        forensic_candidates = mod00["build_forensic_candidates_cached"](handle, initial_focus="HARD_FAIL", top_n=20, refresh=False)
    else:
        progress["current_stage"] = "forensic"
        progress["stages"]["forensic"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "forensic_artifacts_lt1b", "status": "started"}))
        forensic_candidates = mod00["build_forensic_candidates_cached"](
            handle,
            initial_focus="HARD_FAIL",
            top_n=20,
            refresh=_refresh_flag(args),
        )
        progress["stages"]["forensic"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "forensic_artifacts_lt1b", "status": "completed"}))
    artifacts["forensic_candidates"] = forensic_candidates

    if not _must_recompute("taxonomy", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "taxonomy_artifacts_lt1b", "status": "resume_skip"}))
        taxonomy_summary = mod00["build_taxonomy_summary_cached"](handle, refresh=False)
    else:
        progress["current_stage"] = "taxonomy"
        progress["stages"]["taxonomy"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "taxonomy_artifacts_lt1b", "status": "started"}))
        taxonomy_summary = mod00["build_taxonomy_summary_cached"](handle, refresh=_refresh_flag(args))
        progress["stages"]["taxonomy"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "taxonomy_artifacts_lt1b", "status": "completed"}))
    artifacts["taxonomy_summary"] = taxonomy_summary

    if not _must_recompute("case_index", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "case_index_artifacts_lt1b", "status": "resume_skip"}))
        case_index = mod00["build_case_index_cached"](
            handle, root_payload["hard_issue_counts"], root_payload["warn_counts"], top_n_per_block=50, refresh=False
        )
    else:
        progress["current_stage"] = "case_index"
        progress["stages"]["case_index"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "case_index_artifacts_lt1b", "status": "started"}))
        case_index = mod00["build_case_index_cached"](
            handle,
            root_payload["hard_issue_counts"],
            root_payload["warn_counts"],
            top_n_per_block=50,
            refresh=_refresh_flag(args),
        )
        progress["stages"]["case_index"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "case_index_artifacts_lt1b", "status": "completed"}))
    artifacts["case_index"] = case_index

    if not _must_recompute("crossed_gap_severity", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "crossed_gap_severity_artifacts_lt1b", "status": "resume_skip"}))
        crossed_gap_payload = mod00["build_crossed_gap_severity_cached"](handle, refresh=False)
    else:
        progress["current_stage"] = "crossed_gap_severity"
        progress["stages"]["crossed_gap_severity"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "crossed_gap_severity_artifacts_lt1b", "status": "started"}))
        crossed_gap_payload = mod00["build_crossed_gap_severity_cached"](handle, refresh=_refresh_flag(args))
        progress["stages"]["crossed_gap_severity"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "crossed_gap_severity_artifacts_lt1b", "status": "completed"}))
    artifacts.update(crossed_gap_payload)

    if not _must_recompute("positive_cross_review", progress, args.refresh, args.from_stage):
        print(json.dumps({"stage": "positive_cross_review_artifacts_lt1b", "status": "resume_skip"}))
        positive_cross_payload = mod00["build_positive_cross_review_cached"](handle, refresh=False)
    else:
        progress["current_stage"] = "positive_cross_review"
        progress["stages"]["positive_cross_review"] = {"status": "running", "started_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "positive_cross_review_artifacts_lt1b", "status": "started"}))
        positive_cross_payload = mod00["build_positive_cross_review_cached"](handle, refresh=_refresh_flag(args))
        progress["stages"]["positive_cross_review"] = {"status": "completed", "completed_utc": _utc_now()}
        _write_progress(handle.cache_dir, progress)
        print(json.dumps({"stage": "positive_cross_review_artifacts_lt1b", "status": "completed"}))
    artifacts.update(positive_cross_payload)

    progress["current_stage"] = "manifest"
    progress["stages"]["manifest"] = {"status": "running", "started_utc": _utc_now()}
    _write_progress(handle.cache_dir, progress)
    elapsed = perf_counter() - t0
    manifest = mod00["write_manifest"](handle, refresh=True)
    progress["stages"]["manifest"] = {"status": "completed", "completed_utc": _utc_now()}
    progress["status"] = "completed"
    progress["elapsed_sec"] = round(elapsed, 2)
    progress["current_stage"] = None
    progress["manifest_path"] = str(handle.cache_path("manifest", suffix=".json"))
    _write_progress(handle.cache_dir, progress)

    summary = {
        "elapsed_sec": round(elapsed, 2),
        "cache_dir": str(handle.cache_dir),
        "progress_path": str(_progress_path(handle.cache_dir)),
        "row_count_source_full": int(handle.row_count()),
        "target_lt1b_path": None if handle.target_path is None else str(handle.target_path),
        "target_lt1b_tickers": None if handle.target_tickers is None else len(handle.target_tickers),
        "snapshot_rows_total_lt1b": int(artifacts["snapshot"].iloc[0]["rows_total"]),
        "top_hard_issue": None if artifacts["hard_issue_counts"].empty else str(artifacts["hard_issue_counts"].iloc[0]["issue"]),
        "top_warn": None if artifacts["warn_counts"].empty else str(artifacts["warn_counts"].iloc[0]["warn"]),
        "top_taxonomy": None if artifacts["taxonomy_summary"].empty else str(artifacts["taxonomy_summary"].iloc[0]["taxonomy"]),
        "manifest_path": str(handle.cache_path("manifest", suffix=".json")),
    }
    print(json.dumps(summary, indent=2))
    print(f"artifacts_written={len(manifest['artifacts'])}")


if __name__ == "__main__":
    main()
