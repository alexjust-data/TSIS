from __future__ import annotations

from pathlib import Path

import pandas as pd


CACHE_ROOT = Path(globals().get("CACHE_ROOT", Path.cwd() / "cache_v2"))


def _read(name: str) -> pd.DataFrame:
    path = CACHE_ROOT / name
    if not path.exists():
        print(f"[warn] missing artifact: {path}")
        return pd.DataFrame()
    return pd.read_parquet(path)


reference_endpoint_inventory = _read("reference_endpoint_inventory.parquet")
reference_download_audit_summary = _read("reference_download_audit_summary.parquet")
reference_download_error_summary = _read("reference_download_error_summary.parquet")
reference_schema_summary = _read("reference_schema_summary.parquet")
reference_overview_404_case_index = _read("reference_overview_404_case_index.parquet")
reference_overview_404_summary = _read("reference_overview_404_summary.parquet")
reference_identity_snapshot = _read("reference_identity_snapshot.parquet")
reference_identity_quality_summary = _read("reference_identity_quality_summary.parquet")
reference_identity_case_index = _read("reference_identity_case_index.parquet")
reference_listing_snapshots = _read("reference_listing_snapshots.parquet")
reference_listing_snapshot_summary = _read("reference_listing_snapshot_summary.parquet")
reference_ticker_presence_timeline = _read("reference_ticker_presence_timeline.parquet")
reference_snapshot_presence_gaps = _read("reference_snapshot_presence_gaps.parquet")
reference_remap_candidates = _read("reference_remap_candidates.parquet")
reference_transient_symbol_review = _read("reference_transient_symbol_review.parquet")
reference_instrument_type_summary = _read("reference_instrument_type_summary.parquet")
reference_exchange_summary = _read("reference_exchange_summary.parquet")
reference_events_exploded = _read("reference_events_exploded.parquet")
reference_event_type_summary = _read("reference_event_type_summary.parquet")
reference_split_case_index = _read("reference_split_case_index.parquet")
reference_splits_summary = _read("reference_splits_summary.parquet")
reference_dividend_case_index = _read("reference_dividend_case_index.parquet")
reference_dividends_summary = _read("reference_dividends_summary.parquet")
reference_overview_market_identity_links = _read("reference_overview_market_identity_links.parquet")
reference_split_market_link_candidates = _read("reference_split_market_link_candidates.parquet")
reference_split_daily_link_candidates = _read("reference_split_daily_link_candidates.parquet")
reference_split_1m_link_candidates = _read("reference_split_1m_link_candidates.parquet")
reference_event_halt_link_candidates = _read("reference_event_halt_link_candidates.parquet")
reference_event_quotes_link_candidates = _read("reference_event_quotes_link_candidates.parquet")
reference_causal_alignment_summary = _read("reference_causal_alignment_summary.parquet")
