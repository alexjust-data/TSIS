from __future__ import annotations


def build_daily_break_full(full_current, target_issue: str = "trade_price_outside_daily_range"):
    daily_break_full = full_current[
        full_current["issues_list"].map(lambda xs: target_issue in set(xs))
    ].copy()
    daily_break_full["daily_low"] = pd.to_numeric(daily_break_full["m.l"], errors="coerce")
    daily_break_full["daily_high"] = pd.to_numeric(daily_break_full["m.h"], errors="coerce")
    daily_break_full["trade_min"] = pd.to_numeric(daily_break_full["m.price_min"], errors="coerce")
    daily_break_full["trade_max"] = pd.to_numeric(daily_break_full["m.price_max"], errors="coerce")
    daily_break_full["daily_span"] = daily_break_full["daily_high"] - daily_break_full["daily_low"]
    daily_break_full["break_below_abs"] = (daily_break_full["daily_low"] - daily_break_full["trade_min"]).clip(lower=0)
    daily_break_full["break_above_abs"] = (daily_break_full["trade_max"] - daily_break_full["daily_high"]).clip(lower=0)
    daily_break_full["break_below_pct_span"] = 100 * daily_break_full["break_below_abs"] / daily_break_full["daily_span"].replace(0, np.nan)
    daily_break_full["break_above_pct_span"] = 100 * daily_break_full["break_above_abs"] / daily_break_full["daily_span"].replace(0, np.nan)
    daily_break_full["break_side"] = "both"
    daily_break_full.loc[(daily_break_full["break_below_abs"] > 0) & (daily_break_full["break_above_abs"] <= 0), "break_side"] = "below_only"
    daily_break_full.loc[(daily_break_full["break_above_abs"] > 0) & (daily_break_full["break_below_abs"] <= 0), "break_side"] = "above_only"
    daily_break_full["break_abs_max"] = daily_break_full[["break_below_abs", "break_above_abs"]].max(axis=1)
    daily_break_full["break_pct_span_max"] = daily_break_full[["break_below_pct_span", "break_above_pct_span"]].max(axis=1)
    return daily_break_full


def display_daily_break_summary(daily_break_full):
    display(pd.DataFrame([{
        "files": len(daily_break_full),
        "tickers": daily_break_full["ticker"].nunique(),
        "dates": daily_break_full["date"].nunique(),
        "below_only": int((daily_break_full["break_side"] == "below_only").sum()),
        "above_only": int((daily_break_full["break_side"] == "above_only").sum()),
        "both": int((daily_break_full["break_side"] == "both").sum()),
    }]))


def plot_daily_break_overview(daily_break_full):
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    sns.barplot(data=daily_break_full["break_side"].value_counts().rename_axis("break_side").reset_index(name="files"), x="break_side", y="files", color="#e76f51", ax=axes[0, 0])
    axes[0, 0].set_title("Tipo de ruptura vs rango daily")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("files")
    sns.histplot(data=daily_break_full, x="break_below_abs", bins=100, color="#457b9d", ax=axes[0, 1])
    axes[0, 1].set_title("Magnitud absoluta del corte por abajo")
    axes[0, 1].set_xlabel("daily_low - trade_min")
    axes[0, 1].set_ylabel("files")
    axes[0, 1].set_xscale("log")
    sns.histplot(data=daily_break_full, x="break_above_abs", bins=100, color="#d62828", ax=axes[1, 0])
    axes[1, 0].set_title("Magnitud absoluta del corte por arriba")
    axes[1, 0].set_xlabel("trade_max - daily_high")
    axes[1, 0].set_ylabel("files")
    axes[1, 0].set_xscale("log")
    sns.histplot(data=daily_break_full, x="break_pct_span_max", bins=100, color="#2a9d8f", ax=axes[1, 1])
    axes[1, 1].set_title("Magnitud relativa al rango daily")
    axes[1, 1].set_xlabel("max break / daily_span (%)")
    axes[1, 1].set_ylabel("files")
    axes[1, 1].set_xscale("log")
    plt.tight_layout()
    plt.show()


def plot_daily_break_temporal(daily_break_full):
    tmp = daily_break_full.copy()
    tmp["month"] = pd.to_datetime(tmp["date"]).dt.to_period("M").astype(str)
    month_side = tmp.groupby(["month", "break_side"]).size().rename("files").reset_index()
    month_side_pivot = month_side.pivot(index="month", columns="break_side", values="files").fillna(0).sort_index()
    month_mag = tmp.groupby("month", as_index=False).agg(files=("file", "size"), median_break_abs_max=("break_abs_max", "median"), p95_break_abs_max=("break_abs_max", lambda s: s.quantile(0.95)), median_break_pct_span_max=("break_pct_span_max", "median"), p95_break_pct_span_max=("break_pct_span_max", lambda s: s.quantile(0.95))).sort_values("month")
    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
    month_side_pivot.plot(kind="bar", stacked=True, color={"below_only": "#457b9d", "above_only": "#d62828", "both": "#6a4c93"}, ax=axes[0])
    axes[0].set_title("Ruptura por mes y lado")
    axes[0].set_ylabel("files")
    axes[0].set_xlabel("")
    axes[1].plot(month_mag["month"], month_mag["median_break_pct_span_max"], label="median pct span", color="#2a9d8f")
    axes[1].plot(month_mag["month"], month_mag["p95_break_pct_span_max"], label="p95 pct span", color="#f4a261")
    axes[1].set_title("Severidad temporal de la ruptura")
    axes[1].set_ylabel("pct of daily span")
    axes[1].set_xlabel("month")
    axes[1].legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


def build_top_breaks(daily_break_full, top_n: int = 50):
    top_breaks = daily_break_full[["ticker","date","severity","break_side","break_below_abs","break_above_abs","break_below_pct_span","break_above_pct_span","break_abs_max","break_pct_span_max","m.trade_vwap","m.vw","m.possible_price_scale_factor_vs_daily","m.possible_price_scale_factor_vs_1m","m.trade_volume_vs_daily_ratio","m.trade_volume_vs_1m_ratio","file"]].sort_values(["break_pct_span_max", "break_abs_max"], ascending=[False, False])
    return top_breaks.head(top_n), top_breaks


def run_full_break_overview(full_current, target_issue: str = "trade_price_outside_daily_range", top_n: int = 50):
    daily_break_full = build_daily_break_full(full_current, target_issue=target_issue)
    display_daily_break_summary(daily_break_full)
    plot_daily_break_overview(daily_break_full)
    plot_daily_break_temporal(daily_break_full)
    top_breaks_head, top_breaks = build_top_breaks(daily_break_full, top_n=top_n)
    display(top_breaks_head)
    return daily_break_full, top_breaks
