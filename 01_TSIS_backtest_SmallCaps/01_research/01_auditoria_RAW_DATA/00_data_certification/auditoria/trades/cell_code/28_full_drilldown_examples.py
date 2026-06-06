from __future__ import annotations

import pandas as pd


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
