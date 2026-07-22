from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]


def flatten_token_series(series: Iterable[object]) -> list[str]:
    out: list[str] = []
    for value in series:
        if value is None:
            continue
        if isinstance(value, list):
            out.extend(str(x) for x in value if pd.notna(x))
        else:
            out.append(str(value))
    return out


def token_counts(series: pd.Series, col_name: str) -> pd.DataFrame:
    vals = pd.Series(flatten_token_series(series), dtype="object")
    if vals.empty:
        return pd.DataFrame(columns=[col_name, "files"])
    return vals.value_counts().rename_axis(col_name).reset_index(name="files")


def build_run_comparison(
    cur_left: pd.DataFrame,
    cur_right: pd.DataFrame,
    left_label: str,
    right_label: str,
) -> pd.DataFrame:
    right_scale_cols = [c for c in cur_right.columns if c.startswith("m.scale_mismatch")]

    cmp = (
        cur_left[["file_key", "ticker", "date", "severity", "issues_list", "warns_list"]]
        .rename(
            columns={
                "severity": f"severity_{left_label}",
                "issues_list": f"issues_{left_label}",
                "warns_list": f"warns_{left_label}",
            }
        )
        .merge(
            cur_right[
                ["file_key", "severity", "issues_list", "warns_list"] + right_scale_cols
            ].rename(
                columns={
                    "severity": f"severity_{right_label}",
                    "issues_list": f"issues_{right_label}",
                    "warns_list": f"warns_{right_label}",
                }
            ),
            on="file_key",
            how="inner",
        )
    )

    cmp["transition"] = cmp[f"severity_{left_label}"] + " -> " + cmp[f"severity_{right_label}"]
    return cmp


def build_severity_comparison(
    cur_left: pd.DataFrame,
    cur_right: pd.DataFrame,
    left_label: str,
    right_label: str,
) -> pd.DataFrame:
    sev_left = (
        cur_left["severity"]
        .value_counts()
        .reindex(SEVERITY_ORDER, fill_value=0)
        .rename_axis("severity")
        .reset_index(name="files")
    )
    sev_left["version"] = left_label

    sev_right = (
        cur_right["severity"]
        .value_counts()
        .reindex(SEVERITY_ORDER, fill_value=0)
        .rename_axis("severity")
        .reset_index(name="files")
    )
    sev_right["version"] = right_label

    return pd.concat([sev_left, sev_right], ignore_index=True)


def build_transition_counts(cmp_df: pd.DataFrame) -> pd.DataFrame:
    return (
        cmp_df["transition"]
        .value_counts()
        .rename_axis("transition")
        .reset_index(name="files")
    )


def build_reclassified_view(
    cmp_df: pd.DataFrame,
    left_label: str,
    right_label: str,
    from_severity: str = "HARD_FAIL",
    to_severity: str = "SOFT_FAIL",
) -> pd.DataFrame:
    transition = f"{from_severity} -> {to_severity}"
    out = cmp_df[cmp_df["transition"] == transition].copy()
    out.attrs["left_label"] = left_label
    out.attrs["right_label"] = right_label
    out.attrs["transition"] = transition
    return out


def build_hard_issue_comparison(
    cur_left: pd.DataFrame,
    cur_right: pd.DataFrame,
    left_label: str,
    right_label: str,
) -> pd.DataFrame:
    issues_left = token_counts(
        cur_left.loc[cur_left["severity"] == "HARD_FAIL", "issues_list"],
        "issue",
    )
    issues_left["version"] = left_label

    issues_right = token_counts(
        cur_right.loc[cur_right["severity"] == "HARD_FAIL", "issues_list"],
        "issue",
    )
    issues_right["version"] = right_label

    return pd.concat([issues_left, issues_right], ignore_index=True)


def build_top_hard_issues(hard_issue_cmp: pd.DataFrame, top_n: int = 12) -> list[str]:
    if hard_issue_cmp.empty:
        return []
    return (
        hard_issue_cmp.groupby("issue", as_index=False)["files"]
        .sum()
        .sort_values("files", ascending=False)
        .head(top_n)["issue"]
        .tolist()
    )


def build_scale_confidence_counts(reclassified_df: pd.DataFrame) -> pd.DataFrame:
    if "m.scale_mismatch_confidence" not in reclassified_df.columns:
        return pd.DataFrame(columns=["scale_mismatch_confidence", "files"])
    return (
        reclassified_df["m.scale_mismatch_confidence"]
        .fillna("missing")
        .value_counts()
        .rename_axis("scale_mismatch_confidence")
        .reset_index(name="files")
    )


def plot_run_comparison_overview(
    sev_cmp: pd.DataFrame,
    transition_counts: pd.DataFrame,
    hard_issue_cmp: pd.DataFrame,
    scale_conf: pd.DataFrame,
    left_label: str,
    right_label: str,
    top_n_transitions: int = 10,
    top_n_issues: int = 12,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))

    sns.barplot(
        data=sev_cmp,
        x="severity",
        y="files",
        hue="version",
        order=SEVERITY_ORDER,
        ax=axes[0, 0],
    )
    axes[0, 0].set_title(f"Severidades: {left_label} vs {right_label}")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("files")

    sns.barplot(
        data=transition_counts.head(top_n_transitions),
        y="transition",
        x="files",
        color="#457b9d",
        ax=axes[0, 1],
    )
    axes[0, 1].set_title("Top transiciones de severidad")
    axes[0, 1].set_xlabel("files")
    axes[0, 1].set_ylabel("")

    top_issues = build_top_hard_issues(hard_issue_cmp, top_n=top_n_issues)
    hard_issue_plot = hard_issue_cmp[hard_issue_cmp["issue"].isin(top_issues)]
    sns.barplot(
        data=hard_issue_plot,
        y="issue",
        x="files",
        hue="version",
        ax=axes[1, 0],
    )
    axes[1, 0].set_title("Top causas que permanecen en HARD_FAIL")
    axes[1, 0].set_xlabel("files")
    axes[1, 0].set_ylabel("")

    if not scale_conf.empty:
        sns.barplot(
            data=scale_conf,
            y="scale_mismatch_confidence",
            x="files",
            color="#e9c46a",
            ax=axes[1, 1],
        )
        axes[1, 1].set_title("Scale mismatch confidence en HARD_FAIL -> SOFT_FAIL")
        axes[1, 1].set_xlabel("files")
        axes[1, 1].set_ylabel("")
    else:
        axes[1, 1].axis("off")

    plt.tight_layout()
    plt.show()


def display_reclassified_summary(
    reclassified_df: pd.DataFrame,
    left_label: str,
    right_label: str,
    top_n: int = 15,
) -> None:
    issues_col = f"issues_{left_label}"
    warns_col = f"warns_{right_label}"

    issues_before = token_counts(reclassified_df[issues_col], f"issue_{left_label}")
    warns_after = token_counts(reclassified_df[warns_col], f"warn_{right_label}")

    display(Markdown(f"### Reclasificados `{left_label}: HARD_FAIL -> {right_label}: SOFT_FAIL`"))
    display(Markdown(f"- `total reclasificados`: `{len(reclassified_df):,}`"))

    display(Markdown(f"#### Issues en `{left_label}` antes de la relajación"))
    display(issues_before.head(top_n))

    display(Markdown(f"#### Warns en `{right_label}` después de la relajación"))
    display(warns_after.head(top_n))

    cols_show = [
        "ticker",
        "date",
        f"severity_{left_label}",
        f"severity_{right_label}",
        issues_col,
        warns_col,
        "m.scale_mismatch_confidence",
        "m.scale_mismatch_detected",
        "file_key",
    ]
    cols_show = [c for c in cols_show if c in reclassified_df.columns]

    display(Markdown("#### Ejemplos concretos reclasificados"))
    display(reclassified_df[cols_show].sort_values(["ticker", "date"]).head(top_n))
