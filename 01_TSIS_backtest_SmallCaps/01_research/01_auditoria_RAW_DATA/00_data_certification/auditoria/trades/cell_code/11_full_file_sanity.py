from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import Markdown, display


def _safe_stat(path: Path) -> tuple[bool, float]:
    try:
        if not path.exists():
            return False, float("nan")
        return True, float(path.stat().st_size)
    except OSError:
        return False, float("nan")


file_sanity_df = full_current[
    ["file", "ticker", "date", "severity", "batch_id", "validation_kind"]
].copy()
file_sanity_df["file_path"] = file_sanity_df["file"].map(Path)

stats = file_sanity_df["file_path"].map(_safe_stat)
file_sanity_df["exists"] = stats.map(lambda x: x[0])
file_sanity_df["size_bytes"] = stats.map(lambda x: x[1])
file_sanity_df["size_mb"] = file_sanity_df["size_bytes"] / (1024 * 1024)
file_sanity_df["is_market_parquet"] = file_sanity_df["file_path"].map(
    lambda p: p.name.lower() == "market.parquet"
)
file_sanity_df["year_from_date"] = pd.to_datetime(
    file_sanity_df["date"], errors="coerce"
).dt.year
file_sanity_df["dup_file_rows"] = file_sanity_df.groupby("file")["file"].transform("size")

sanity_summary = pd.DataFrame(
    [
        {
            "rows_in_current": int(len(file_sanity_df)),
            "unique_files": int(file_sanity_df["file"].nunique()),
            "duplicate_file_rows": int((file_sanity_df["dup_file_rows"] > 1).sum()),
            "missing_files": int((~file_sanity_df["exists"]).sum()),
            "zero_byte_files": int((file_sanity_df["size_bytes"].fillna(-1) == 0).sum()),
            "non_market_named_files": int((~file_sanity_df["is_market_parquet"]).sum()),
            "median_size_mb": round(float(file_sanity_df["size_mb"].median()), 6),
            "p01_size_mb": round(float(file_sanity_df["size_mb"].quantile(0.01)), 6),
            "p99_size_mb": round(float(file_sanity_df["size_mb"].quantile(0.99)), 6),
        }
    ]
)

display(Markdown("### Sanidad física del universo full"))
display(sanity_summary.T)

missing_files_view = file_sanity_df.loc[
    ~file_sanity_df["exists"],
    ["ticker", "date", "severity", "batch_id", "file"],
].head(30)

dup_files_view = (
    file_sanity_df.loc[file_sanity_df["dup_file_rows"] > 1, ["file", "ticker", "date", "severity"]]
    .sort_values(["file", "date"])
    .head(30)
)

display(Markdown("**Missing files en `trades_current`**"))
display(missing_files_view)

display(Markdown("**Files repetidos en `trades_current`**"))
display(dup_files_view)

size_plot_df = file_sanity_df.loc[
    file_sanity_df["exists"] & file_sanity_df["size_mb"].notna()
].copy()

if not size_plot_df.empty:
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    sns.histplot(size_plot_df["size_mb"], bins=80, color="#457b9d", ax=axes[0])
    axes[0].set_title("Distribucion de size_mb en market.parquet")
    axes[0].set_xlabel("size_mb")
    axes[0].set_ylabel("files")
    axes[0].set_xscale("log")

    severity_size = (
        size_plot_df.groupby("severity", dropna=False)["size_mb"]
        .median()
        .rename("median_size_mb")
        .reset_index()
    )
    sns.barplot(data=severity_size, x="severity", y="median_size_mb", color="#2a9d8f", ax=axes[1])
    axes[1].set_title("Mediana de tamaño por severidad")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("median_size_mb")

    plt.tight_layout()
