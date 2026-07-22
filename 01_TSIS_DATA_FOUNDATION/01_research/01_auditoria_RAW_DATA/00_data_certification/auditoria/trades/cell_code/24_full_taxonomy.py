from __future__ import annotations


def build_tax_df(daily_break_full, dup_heavy_threshold: float = 1.0):
    tax_df = daily_break_full.copy()
    tax_df["confirmed_by_1m"] = tax_df["warns_list"].map(lambda xs: "trade_price_outside_1m_range" in set(xs))
    tax_df["has_scale_warn"] = tax_df["warns_list"].map(lambda xs: bool({"possible_corporate_action_scale_mismatch", "possible_corporate_action_scale_mismatch_vs_daily", "possible_corporate_action_scale_mismatch_vs_1m"} & set(xs)))
    tax_df["has_dup_warn"] = tax_df["warns_list"].map(lambda xs: bool({"duplicate_exact_trade_rows_present", "duplicate_excess_ratio_gt_threshold"} & set(xs)))
    tax_df["dup_heavy"] = pd.to_numeric(tax_df["m.duplicate_excess_ratio_pct"], errors="coerce").fillna(0) >= float(dup_heavy_threshold)
    tax_df["taxonomy"] = "other"
    tax_df.loc[tax_df["confirmed_by_1m"] & (~tax_df["has_scale_warn"]) & (~tax_df["dup_heavy"]), "taxonomy"] = "confirmed_by_1m_and_not_scale"
    tax_df.loc[tax_df["confirmed_by_1m"] & tax_df["dup_heavy"], "taxonomy"] = "confirmed_by_1m_and_dup_heavy"
    tax_df.loc[~tax_df["confirmed_by_1m"], "taxonomy"] = "not_confirmed_by_1m"
    return tax_df


def build_taxonomy_summary(tax_df):
    taxonomy_summary = tax_df.groupby("taxonomy", observed=False).agg(files=("file", "size"), tickers=("ticker", "nunique"), dates=("date", "nunique"), pct_scale_warn=("has_scale_warn", lambda s: 100 * s.mean()), pct_dup_warn=("has_dup_warn", lambda s: 100 * s.mean()), pct_off_session=("warns_list", lambda s: 100 * s.map(lambda xs: "off_session_trades_present" in set(xs)).mean()), median_abs_break=("break_abs_max", "median"), p95_abs_break=("break_abs_max", lambda s: s.quantile(0.95)), median_pct_break=("break_pct_span_max", "median"), p95_pct_break=("break_pct_span_max", lambda s: s.quantile(0.95))).reset_index().sort_values("files", ascending=False)
    for col in ["pct_scale_warn", "pct_dup_warn", "pct_off_session", "median_abs_break", "p95_abs_break", "median_pct_break", "p95_pct_break"]:
        taxonomy_summary[col] = pd.to_numeric(taxonomy_summary[col], errors="coerce").round(3)
    return taxonomy_summary


def plot_taxonomy_summary(taxonomy_summary):
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    sns.barplot(data=taxonomy_summary, x="taxonomy", y="files", color="#457b9d", ax=axes[0, 0])
    axes[0, 0].set_title("Files por taxonomia")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("files")
    axes[0, 0].tick_params(axis="x", rotation=20)
    sns.barplot(data=taxonomy_summary, x="taxonomy", y="pct_dup_warn", color="#d62828", ax=axes[0, 1])
    axes[0, 1].set_title("% con duplicados por taxonomia")
    axes[0, 1].set_xlabel("")
    axes[0, 1].set_ylabel("pct")
    axes[0, 1].tick_params(axis="x", rotation=20)
    sns.barplot(data=taxonomy_summary, x="taxonomy", y="median_abs_break", color="#2a9d8f", ax=axes[1, 0])
    axes[1, 0].set_title("Mediana de ruptura absoluta")
    axes[1, 0].set_xlabel("")
    axes[1, 0].set_ylabel("median_abs_break")
    axes[1, 0].tick_params(axis="x", rotation=20)
    sns.barplot(data=taxonomy_summary, x="taxonomy", y="median_pct_break", color="#f4a261", ax=axes[1, 1])
    axes[1, 1].set_title("Mediana de ruptura relativa")
    axes[1, 1].set_xlabel("")
    axes[1, 1].set_ylabel("median_pct_break")
    axes[1, 1].tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.show()


def run_full_taxonomy(daily_break_full, dup_heavy_threshold: float = 1.0):
    tax_df = build_tax_df(daily_break_full, dup_heavy_threshold=dup_heavy_threshold)
    taxonomy_summary = build_taxonomy_summary(tax_df)
    display(taxonomy_summary)
    plot_taxonomy_summary(taxonomy_summary)
    return tax_df, taxonomy_summary
