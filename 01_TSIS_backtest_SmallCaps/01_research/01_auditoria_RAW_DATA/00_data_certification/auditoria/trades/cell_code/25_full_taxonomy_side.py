from __future__ import annotations


def build_taxonomy_side(tax_df):
    taxonomy_side = tax_df.groupby(["taxonomy", "break_side"], observed=False).agg(files=("file", "size"), median_abs_break=("break_abs_max", "median"), p95_abs_break=("break_abs_max", lambda s: s.quantile(0.95)), median_pct_break=("break_pct_span_max", "median"), p95_pct_break=("break_pct_span_max", lambda s: s.quantile(0.95))).reset_index()
    taxonomy_side["pct_in_taxonomy"] = 100 * taxonomy_side["files"] / taxonomy_side.groupby("taxonomy")["files"].transform("sum").clip(lower=1)
    for col in ["median_abs_break", "p95_abs_break", "median_pct_break", "p95_pct_break", "pct_in_taxonomy"]:
        taxonomy_side[col] = pd.to_numeric(taxonomy_side[col], errors="coerce").round(3)
    return taxonomy_side


def plot_taxonomy_side(taxonomy_side):
    display(taxonomy_side.sort_values(["taxonomy", "files"], ascending=[True, False]))
    fig, axes = plt.subplots(1, 2, figsize=(20, 7))
    sns.barplot(data=taxonomy_side, x="taxonomy", y="pct_in_taxonomy", hue="break_side", ax=axes[0])
    axes[0].set_title("% de cada lado dentro de cada taxonomia")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("pct_in_taxonomy")
    axes[0].tick_params(axis="x", rotation=20)
    sns.barplot(data=taxonomy_side, x="taxonomy", y="median_pct_break", hue="break_side", ax=axes[1])
    axes[1].set_title("Mediana de ruptura relativa por taxonomia y lado")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("median_pct_break")
    axes[1].tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.show()


def run_full_taxonomy_side(tax_df):
    taxonomy_side = build_taxonomy_side(tax_df)
    plot_taxonomy_side(taxonomy_side)
    return taxonomy_side
