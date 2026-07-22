from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DEFAULT_CACHE_DIR = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2"
)


def load_manifest(cache_dir: Path | str = DEFAULT_CACHE_DIR) -> dict:
    cache_dir = Path(cache_dir)
    return json.loads((cache_dir / "manifest.json").read_text(encoding="utf-8"))


def load_build_log(cache_dir: Path | str = DEFAULT_CACHE_DIR) -> dict:
    cache_dir = Path(cache_dir)
    return json.loads((cache_dir / "build_log.json").read_text(encoding="utf-8"))


def load_artifact(name: str, cache_dir: Path | str = DEFAULT_CACHE_DIR) -> pd.DataFrame:
    cache_dir = Path(cache_dir)
    path = cache_dir / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_parquet(path)


def load_all_core_artifacts(cache_dir: Path | str = DEFAULT_CACHE_DIR) -> dict[str, pd.DataFrame]:
    names = [
        "source_quality_summary",
        "field_completeness_summary",
        "canonical_event_summary",
        "duplicate_analysis",
        "cross_source_overlap_summary",
        "multisource_builder_reconciliation",
        "nasdaq_final_residual_rows",
        "ticker_halt_coverage_summary",
        "ticker_year_halt_presence",
        "event_taxonomy_summary",
        "halt_event_windows",
        "halts_lt1b_event_index",
        "halts_intraday_overlay_index",
        "halts_quotes_trades_visual_cases",
        "halts_quotes_link_candidates",
        "halts_trades_link_candidates",
        "event_window_alignment_summary",
    ]
    return {name: load_artifact(name, cache_dir=cache_dir) for name in names}
