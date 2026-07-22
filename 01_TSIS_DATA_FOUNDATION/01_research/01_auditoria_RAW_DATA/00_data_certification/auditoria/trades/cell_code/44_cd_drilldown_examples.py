from __future__ import annotations

import pandas as pd
import pyarrow.parquet as pq


def contains_token_full(value, token):
    if token is None:
        return False
    return token in set(value)


def build_focus_examples_full(full_current: pd.DataFrame, hard_issue_counts_full: pd.DataFrame, warn_counts_full: pd.DataFrame):
    focus_issue_full = hard_issue_counts_full.iloc[0]["issue"] if not hard_issue_counts_full.empty else None
    focus_warn_full = warn_counts_full.iloc[0]["warn"] if not warn_counts_full.empty else None

    issue_examples_full = (
        full_current.loc[
            full_current["issues_list"].map(lambda xs: contains_token_full(xs, focus_issue_full)),
            [
                "ticker", "date", "severity", "batch_id", "file",
                "m.price_min", "m.price_max", "m.trade_vwap", "m.vw",
                "m.ohlcv_1m_low_min", "m.ohlcv_1m_high_max",
                "m.trade_volume_vs_daily_ratio", "m.trade_volume_vs_1m_ratio",
                "m.possible_price_scale_factor_vs_daily", "m.possible_price_scale_factor_vs_1m",
                "issues_list", "warns_list",
            ],
        ]
        .sort_values(["ticker", "date"])
        .head(30)
    )

    warn_examples_full = (
        full_current.loc[
            full_current["warns_list"].map(lambda xs: contains_token_full(xs, focus_warn_full)),
            [
                "ticker", "date", "severity", "batch_id", "file",
                "m.duplicate_excess_ratio_pct", "m.max_trades_same_timestamp",
                "m.off_session_trade_pct", "m.trade_volume_vs_daily_ratio",
                "m.trade_volume_vs_1m_ratio", "issues_list", "warns_list",
            ],
        ]
        .sort_values(["ticker", "date"])
        .head(30)
    )
    return focus_issue_full, focus_warn_full, issue_examples_full, warn_examples_full


def build_focus_examples_full_chunked(
    current_parquet: str,
    mod00: dict,
    hard_issue_counts_full: pd.DataFrame,
    warn_counts_full: pd.DataFrame,
    max_examples: int = 30,
):
    focus_issue_full = hard_issue_counts_full.iloc[0]["issue"] if not hard_issue_counts_full.empty else None
    focus_warn_full = warn_counts_full.iloc[0]["warn"] if not warn_counts_full.empty else None
    if focus_issue_full is None and focus_warn_full is None:
        empty = pd.DataFrame()
        return focus_issue_full, focus_warn_full, empty, empty

    pf = pq.ParquetFile(current_parquet)
    issue_frames: list[pd.DataFrame] = []
    warn_frames: list[pd.DataFrame] = []

    for row_group_idx in range(pf.num_row_groups):
        chunk = pf.read_row_group(
            row_group_idx,
            columns=["ticker", "date", "severity", "batch_id", "file", "issues", "warns", "metrics_json"],
        ).to_pandas()
        if chunk.empty:
            continue

        chunk = mod00["normalize_event_like_df"](chunk)
        if focus_issue_full is not None:
            issue_frames.append(
                chunk.loc[
                    chunk["issues_list"].map(lambda xs: contains_token_full(xs, focus_issue_full)),
                    [
                        "ticker", "date", "severity", "batch_id", "file",
                        "m.price_min", "m.price_max", "m.trade_vwap", "m.vw",
                        "m.ohlcv_1m_low_min", "m.ohlcv_1m_high_max",
                        "m.trade_volume_vs_daily_ratio", "m.trade_volume_vs_1m_ratio",
                        "m.possible_price_scale_factor_vs_daily", "m.possible_price_scale_factor_vs_1m",
                        "issues_list", "warns_list",
                    ],
                ]
            )
        if focus_warn_full is not None:
            warn_frames.append(
                chunk.loc[
                    chunk["warns_list"].map(lambda xs: contains_token_full(xs, focus_warn_full)),
                    [
                        "ticker", "date", "severity", "batch_id", "file",
                        "m.duplicate_excess_ratio_pct", "m.max_trades_same_timestamp",
                        "m.off_session_trade_pct", "m.trade_volume_vs_daily_ratio",
                        "m.trade_volume_vs_1m_ratio", "issues_list", "warns_list",
                    ],
                ]
            )

    issue_examples_full = (
        pd.concat(issue_frames, ignore_index=True).sort_values(["ticker", "date"]).head(max_examples)
        if issue_frames
        else pd.DataFrame()
    )
    warn_examples_full = (
        pd.concat(warn_frames, ignore_index=True).sort_values(["ticker", "date"]).head(max_examples)
        if warn_frames
        else pd.DataFrame()
    )
    return focus_issue_full, focus_warn_full, issue_examples_full, warn_examples_full
