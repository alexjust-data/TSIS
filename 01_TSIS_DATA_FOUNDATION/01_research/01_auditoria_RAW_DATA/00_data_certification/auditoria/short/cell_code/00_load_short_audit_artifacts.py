from __future__ import annotations

from pathlib import Path

import pandas as pd


DEFAULT_CACHE_ROOT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2"
)


CACHE_ROOT = Path(globals().get("CACHE_ROOT", DEFAULT_CACHE_ROOT))


def _read(name: str) -> pd.DataFrame:
    path = CACHE_ROOT / name
    if not path.exists():
        print(f"[warn] missing artifact: {path}")
        return pd.DataFrame()
    return pd.read_parquet(path)


short_provider_inventory = _read("short_provider_inventory.parquet")
short_provider_comparison_summary = _read("short_provider_comparison_summary.parquet")
short_only_polygon_tickers = _read("short_only_polygon_tickers.parquet")
short_only_finra_tickers = _read("short_only_finra_tickers.parquet")
short_interest_arithmetic_checks = _read("short_interest_arithmetic_checks.parquet")
short_volume_arithmetic_checks = _read("short_volume_arithmetic_checks.parquet")
short_reference_identity_summary = _read("short_reference_identity_summary.parquet")
short_identity_links = _read("short_identity_links.parquet")
short_possible_reuse_mix = _read("short_possible_reuse_mix.parquet")
short_outside_life_window = _read("short_outside_life_window.parquet")
short_volume_market_link_candidates = _read("short_volume_market_link_candidates.parquet")
short_volume_halt_link_candidates = _read("short_volume_halt_link_candidates.parquet")
short_causal_alignment_summary = _read("short_causal_alignment_summary.parquet")
short_interest_market_context_candidates = _read("short_interest_market_context_candidates.parquet")
short_interest_context_summary = _read("short_interest_context_summary.parquet")
