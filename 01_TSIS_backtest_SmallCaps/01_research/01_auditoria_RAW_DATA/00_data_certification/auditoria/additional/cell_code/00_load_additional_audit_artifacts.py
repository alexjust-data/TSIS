from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from IPython.display import Markdown, display


DEFAULT_ADDITIONAL_AUDIT_CACHE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2"
)

CACHE_ROOT = Path(globals().get("CACHE_ROOT", DEFAULT_ADDITIONAL_AUDIT_CACHE))

manifest_path = CACHE_ROOT / "additional_build_manifest.json"
if manifest_path.exists():
    ADDITIONAL_BUILD_MANIFEST = json.loads(manifest_path.read_text(encoding="utf-8"))
else:
    ADDITIONAL_BUILD_MANIFEST = {}


def _read(name: str) -> pd.DataFrame:
    path = CACHE_ROOT / name
    if not path.exists():
        print(f"[warn] missing artifact: {path}")
        return pd.DataFrame()
    return pd.read_parquet(path)


additional_dataset_inventory = _read("additional_dataset_inventory.parquet")
additional_effective_coverage_summary = _read("additional_effective_coverage_summary.parquet")
additional_family_summary = _read("additional_family_summary.parquet")
additional_schema_samples = _read("additional_schema_samples.parquet")
additional_financials_summary = _read("additional_financials_summary.parquet")
additional_news_summary = _read("additional_news_summary.parquet")
additional_news_ticker_density = _read("additional_news_ticker_density.parquet")
additional_news_multi_ticker_summary = _read("additional_news_multi_ticker_summary.parquet")
additional_news_event_index = _read("additional_news_event_index.parquet")
additional_news_market_link_candidates = _read("additional_news_market_link_candidates.parquet")
additional_news_link_summary = _read("additional_news_link_summary.parquet")
additional_corporate_actions_summary = _read("additional_corporate_actions_summary.parquet")
additional_ipos_summary = _read("additional_ipos_summary.parquet")
additional_macro_calendar_summary = _read("additional_macro_calendar_summary.parquet")
additional_ipo_event_index = _read("additional_ipo_event_index.parquet")
additional_ipo_market_link_candidates = _read("additional_ipo_market_link_candidates.parquet")
additional_ipo_link_summary = _read("additional_ipo_link_summary.parquet")
additional_corp_actions_reference_overlap = _read("additional_corp_actions_reference_overlap.parquet")
additional_corp_actions_reference_overlap_summary = _read("additional_corp_actions_reference_overlap_summary.parquet")

display(Markdown(f"**CACHE_ROOT**: `{CACHE_ROOT}`"))
