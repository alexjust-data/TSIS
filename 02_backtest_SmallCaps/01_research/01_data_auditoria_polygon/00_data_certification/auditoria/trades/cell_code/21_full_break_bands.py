from __future__ import annotations


def build_band_df(daily_break_full):
    band_df = daily_break_full.copy()
    band_df["abs_break_bucket"] = pd.cut(band_df["break_abs_max"], bins=[-np.inf, 0.01, 0.05, 0.10, 0.25, 0.50, 1.0, 5.0, np.inf], labels=["<=0.01", "0.01-0.05", "0.05-0.10", "0.10-0.25", "0.25-0.50", "0.50-1", "1-5", ">5"])
    band_df["pct_break_bucket"] = pd.cut(band_df["break_pct_span_max"], bins=[-np.inf, 1, 5, 10, 25, 50, 100, 500, 1000, np.inf], labels=["<=1%", "1-5%", "5-10%", "10-25%", "25-50%", "50-100%", "100-500%", "500-1000%", ">1000%"])
    return band_df


def build_band_counts(band_df):
    abs_bucket_counts = band_df["abs_break_bucket"].value_counts(dropna=False).sort_index().rename_axis("bucket").reset_index(name="files")
    pct_bucket_counts = band_df["pct_break_bucket"].value_counts(dropna=False).sort_index().rename_axis("bucket").reset_index(name="files")
    return abs_bucket_counts, pct_bucket_counts


def plot_band_counts(abs_bucket_counts, pct_bucket_counts):
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    sns.barplot(data=abs_bucket_counts, x="bucket", y="files", color="#457b9d", ax=axes[0])
    axes[0].set_title("Ruptura absoluta por bandas")
    axes[0].set_xlabel("break_abs_max")
    axes[0].set_ylabel("files")
    axes[0].tick_params(axis="x", rotation=45)
    sns.barplot(data=pct_bucket_counts, x="bucket", y="files", color="#2a9d8f", ax=axes[1])
    axes[1].set_title("Ruptura relativa al rango daily por bandas")
    axes[1].set_xlabel("break_pct_span_max")
    axes[1].set_ylabel("files")
    axes[1].tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.show()


def run_full_break_bands(daily_break_full):
    band_df = build_band_df(daily_break_full)
    abs_bucket_counts, pct_bucket_counts = build_band_counts(band_df)
    display(abs_bucket_counts)
    display(pct_bucket_counts)
    plot_band_counts(abs_bucket_counts, pct_bucket_counts)
    return band_df, abs_bucket_counts, pct_bucket_counts
