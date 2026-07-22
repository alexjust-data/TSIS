from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def build_hard_full(full_current: pd.DataFrame) -> pd.DataFrame:
    return full_current.loc[full_current["severity"] == "HARD_FAIL"].copy()


def build_hard_issue_counts_full(hard_full: pd.DataFrame, flatten_tokens) -> pd.DataFrame:
    vals = pd.Series(flatten_tokens(hard_full["issues_list"].tolist()), dtype="object")
    if vals.empty:
        return pd.DataFrame(columns=["issue", "files"])
    return vals.value_counts().rename_axis("issue").reset_index(name="files")


def build_warn_counts_full(full_current: pd.DataFrame, flatten_tokens) -> pd.DataFrame:
    vals = pd.Series(flatten_tokens(full_current["warns_list"].tolist()), dtype="object")
    if vals.empty:
        return pd.DataFrame(columns=["warn", "files"])
    return vals.value_counts().rename_axis("warn").reset_index(name="files")


def build_issue_evidence_full(hard_full: pd.DataFrame, hard_issue_counts_full: pd.DataFrame) -> pd.DataFrame:
    issue_rows_full: list[dict[str, object]] = []
    for issue_name in hard_issue_counts_full["issue"].tolist():
        x = hard_full[hard_full["issues_list"].map(lambda xs: issue_name in set(xs))].copy()
        issue_rows_full.append(
            {
                "issue": issue_name,
                "files": int(len(x)),
                "tickers": int(x["ticker"].nunique()) if "ticker" in x.columns else 0,
                "dates": int(x["date"].nunique()) if "date" in x.columns else 0,
                "has_1m_warn_pct": 100.0 * x["warns_list"].map(lambda xs: "trade_price_outside_1m_range" in set(xs)).mean() if len(x) else np.nan,
                "median_off_session_pct": pd.to_numeric(x.get("m.off_session_trade_pct"), errors="coerce").median() if len(x) else np.nan,
                "median_dup_pct": pd.to_numeric(x.get("m.duplicate_excess_ratio_pct"), errors="coerce").median() if len(x) else np.nan,
                "median_vol_vs_daily": pd.to_numeric(x.get("m.trade_volume_vs_daily_ratio"), errors="coerce").median() if len(x) else np.nan,
                "median_vol_vs_1m": pd.to_numeric(x.get("m.trade_volume_vs_1m_ratio"), errors="coerce").median() if len(x) else np.nan,
            }
        )
    out = pd.DataFrame(issue_rows_full)
    if out.empty:
        return out
    return out.sort_values(["files", "has_1m_warn_pct"], ascending=[False, False]).reset_index(drop=True)


def plot_root_cause_counts_full(
    hard_issue_counts_full: pd.DataFrame,
    warn_counts_full: pd.DataFrame,
    top_n: int = 15,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    sns.barplot(
        data=hard_issue_counts_full.head(top_n),
        y="issue",
        x="files",
        color="#e76f51",
        ax=axes[0],
    )
    axes[0].set_title("Top causas de HARD_FAIL en full", fontsize=SMALL_TITLE_SIZE)
    axes[0].set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    axes[0].set_ylabel("")
    axes[0].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)

    sns.barplot(
        data=warn_counts_full.head(top_n),
        y="warn",
        x="files",
        color="#e9c46a",
        ax=axes[1],
    )
    axes[1].set_title("Top warnings del full", fontsize=SMALL_TITLE_SIZE)
    axes[1].set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    axes[1].set_ylabel("")
    axes[1].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()


def plot_issue_evidence_full(issue_evidence_full: pd.DataFrame) -> None:
    if issue_evidence_full.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    sns.barplot(data=issue_evidence_full, y="issue", x="files", color="#d62828", ax=axes[0])
    axes[0].set_title("Peso de cada issue vivo en HARD_FAIL", fontsize=SMALL_TITLE_SIZE)
    axes[0].set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    axes[0].set_ylabel("")
    axes[0].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)

    sns.barplot(
        data=issue_evidence_full,
        y="issue",
        x="has_1m_warn_pct",
        color="#2a9d8f",
        ax=axes[1],
    )
    axes[1].set_title("Confirmacion por 1m dentro de cada issue", fontsize=SMALL_TITLE_SIZE)
    axes[1].set_xlabel("has_1m_warn_pct", fontsize=SMALL_LABEL_SIZE)
    axes[1].set_ylabel("")
    axes[1].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()
