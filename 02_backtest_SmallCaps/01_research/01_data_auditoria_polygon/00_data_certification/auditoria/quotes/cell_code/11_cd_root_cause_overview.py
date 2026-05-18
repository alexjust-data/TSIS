from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd


def _build_token_counts(series: pd.Series, label: str) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for values in series:
        for token in values:
            counter[str(token)] += 1
    out = pd.DataFrame(counter.items(), columns=[label, "files"]).sort_values("files", ascending=False).reset_index(drop=True)
    if not out.empty:
        out["pct"] = out["files"] / out["files"].sum() * 100.0
    return out


def build_hard_issue_counts_cd(df: pd.DataFrame) -> pd.DataFrame:
    hard = df.loc[df["severity"].eq("HARD_FAIL"), "issues_list"]
    return _build_token_counts(hard, "issue")


def build_warn_counts_cd(df: pd.DataFrame) -> pd.DataFrame:
    warn = df.loc[df["has_warn"], "warns_list"]
    return _build_token_counts(warn, "warn")


def build_issue_root_view_cd(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    hard = df.loc[df["severity"].eq("HARD_FAIL"), ["root", "issues_list"]]
    for _, row in hard.iterrows():
        for issue in row["issues_list"]:
            rows.append({"root": row["root"], "issue": issue})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.groupby(["issue", "root"]).size().rename("files").reset_index()


def build_warn_severity_view_cd(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base = df.loc[df["has_warn"], ["severity", "warns_list"]]
    for _, row in base.iterrows():
        for warn in row["warns_list"]:
            rows.append({"severity": row["severity"], "warn": warn})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.groupby(["warn", "severity"]).size().rename("files").reset_index()


def plot_root_cause_overview_cd(hard_issue_counts: pd.DataFrame, warn_counts: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    hard_top = hard_issue_counts.head(10)
    axes[0].barh(hard_top["issue"][::-1], hard_top["files"][::-1], color="#e76f51")
    axes[0].set_title("Top HARD_FAIL issues")
    axes[0].set_xlabel("files")

    warn_top = warn_counts.head(10)
    axes[1].barh(warn_top["warn"][::-1], warn_top["files"][::-1], color="#e9c46a")
    axes[1].set_title("Top warns")
    axes[1].set_xlabel("files")

    fig.tight_layout()

