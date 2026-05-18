from __future__ import annotations

import json
import runpy
from pathlib import Path

import pandas as pd


BASE_VIEW = Path(__file__).resolve().parent / "58_trades_file_acceptance_view.py"
RUN_DIR_LT1B = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged")
CACHE_DIR_LT1B = RUN_DIR_LT1B / "root_cause_exports" / "file_acceptance_cache_lt1b"
MANIFEST_PATH_LT1B = CACHE_DIR_LT1B / "manifest.json"


_base = runpy.run_path(str(BASE_VIEW))
globals().update(_base)


def _load_parquet(name: str) -> pd.DataFrame:
    p = CACHE_DIR_LT1B / f"{name}.parquet"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_parquet(p)


def load_manifest() -> dict:
    if not MANIFEST_PATH_LT1B.exists():
        return {}
    return json.loads(MANIFEST_PATH_LT1B.read_text(encoding="utf-8"))


def load_all_artifacts() -> dict[str, pd.DataFrame]:
    keys = [
        "layer1_integrity_summary",
        "layer1_integrity_examples",
        "sample_index",
        "raw_file_metrics",
        "condition_combo_summary",
        "condition_code_summary",
        "layer2_eligibility_summary",
        "layer2_session_profile",
        "layer2_session_mismatch",
        "layer3_tape_quality_summary",
        "layer4_reference_consistency_summary",
        "layer5_severity_real_summary",
        "layer6_policy_summary",
        "layer6_policy_examples",
    ]
    return {k: _load_parquet(k) for k in keys}


RUN_DIR_CD = RUN_DIR_LT1B
CACHE_DIR = CACHE_DIR_LT1B
MANIFEST_PATH = MANIFEST_PATH_LT1B
