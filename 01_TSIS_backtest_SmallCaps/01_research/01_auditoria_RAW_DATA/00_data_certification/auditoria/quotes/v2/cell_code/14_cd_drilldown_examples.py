from __future__ import annotations

import pandas as pd


def _contains_token(tokens: list[str], target: str | None) -> bool:
    if target is None:
        return False
    return target in set(tokens or [])


def build_focus_examples_cd(df: pd.DataFrame, hard_issue_counts: pd.DataFrame, warn_counts: pd.DataFrame, top_n: int = 20):
    focus_issue = hard_issue_counts.iloc[0]["issue"] if not hard_issue_counts.empty else None
    focus_warn = warn_counts.iloc[0]["warn"] if not warn_counts.empty else None

    issue_examples = df.loc[
        df["issues_list"].map(lambda x: _contains_token(x, focus_issue)),
        [
            "ticker",
            "date",
            "root",
            "severity",
            "rows",
            "m.crossed_ratio_pct",
            "m.crossed_rows",
            "m.ask_integer_pct",
            "m.ask_eq_round_bid_pct",
            "file",
        ],
    ].sort_values(["m.crossed_ratio_pct", "rows"], ascending=False).head(top_n)

    warn_examples = df.loc[
        df["warns_list"].map(lambda x: _contains_token(x, focus_warn)),
        [
            "ticker",
            "date",
            "root",
            "severity",
            "rows",
            "m.crossed_ratio_pct",
            "m.crossed_rows",
            "m.timestamp_out_of_partition_day",
            "file",
        ],
    ].sort_values(["m.crossed_ratio_pct", "rows"], ascending=False).head(top_n)

    return focus_issue, focus_warn, issue_examples, warn_examples

