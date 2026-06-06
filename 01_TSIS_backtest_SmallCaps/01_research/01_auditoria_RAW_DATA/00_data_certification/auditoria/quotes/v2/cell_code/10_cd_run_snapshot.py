from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]
SEVERITY_PALETTE = {
    "PASS": "#2a9d8f",
    "SOFT_FAIL": "#e9c46a",
    "HARD_FAIL": "#e76f51",
}


def build_snapshot_cd(df: pd.DataFrame, current_parquet_cd) -> pd.DataFrame:
    out = {
        "current_parquet": str(current_parquet_cd),
        "rows_total": int(len(df)),
        "ticker_n": int(df["ticker"].nunique()),
        "date_min": str(df["date"].min().date()),
        "date_max": str(df["date"].max().date()),
        "root_c_rows": int(df["root"].eq("C").sum()),
        "root_d_rows": int(df["root"].eq("D").sum()),
        "rows_median": float(df["rows"].median()),
        "rows_p90": float(df["rows"].quantile(0.90)),
        "rows_p99": float(df["rows"].quantile(0.99)),
        "crossed_ratio_median_pct": float(df["m.crossed_ratio_pct"].fillna(0).median()),
        "crossed_ratio_p99_pct": float(df["m.crossed_ratio_pct"].fillna(0).quantile(0.99)),
        "timestamp_out_of_partition_rows": int(df["m.timestamp_out_of_partition_day"].fillna(False).sum()),
    }
    return pd.DataFrame([out])


def build_severity_counts_cd(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df["severity"]
        .value_counts(dropna=False)
        .rename_axis("severity")
        .reset_index(name="files")
    )
    counts["pct"] = counts["files"] / max(len(df), 1) * 100.0
    counts["severity"] = pd.Categorical(counts["severity"], categories=SEVERITY_ORDER, ordered=True)
    return counts.sort_values("severity").reset_index(drop=True)


def build_root_mix_cd(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby(["root", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    pivot = out.pivot(index="root", columns="severity", values="files").fillna(0).reindex(columns=SEVERITY_ORDER, fill_value=0)
    pivot["total"] = pivot.sum(axis=1)
    for sev in SEVERITY_ORDER:
        pivot[f"{sev.lower()}_pct"] = pivot[sev] / pivot["total"].replace(0, pd.NA) * 100.0
    return pivot.reset_index()


def plot_snapshot_cd(sev_counts: pd.DataFrame, root_mix: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    axes[0].bar(
        sev_counts["severity"].astype(str),
        sev_counts["files"],
        color=[SEVERITY_PALETTE.get(x, "#888888") for x in sev_counts["severity"].astype(str)],
    )
    axes[0].set_title("Severidad C+D")
    axes[0].set_ylabel("files")

    root_plot = root_mix.set_index("root")[SEVERITY_ORDER]
    root_plot.plot(kind="bar", stacked=True, ax=axes[1], color=[SEVERITY_PALETTE[x] for x in SEVERITY_ORDER])
    axes[1].set_title("Mix por root ganador")
    axes[1].set_ylabel("files")
    axes[1].legend(title="severity")

    fig.tight_layout()

