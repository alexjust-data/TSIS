from __future__ import annotations

from pathlib import Path
from typing import Iterable
import shutil

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, clear_output, display


DEFAULT_BUCKETS = [
    "vw_edge_absmax_only",
    "vw_warn_minor_or_material",
    "vw_low_ratio_limited_days",
    "vw_mid_ratio_illiquid_regime",
    "vw_high_ratio_illiquid_regime",
    "hard_invalid_parse_or_price",
]

DEFAULT_MODES = {
    "all_no_good": DEFAULT_BUCKETS,
    "hard_invalid": ["hard_invalid_parse_or_price"],
    "vw_flags": [
        "vw_edge_absmax_only",
        "vw_warn_minor_or_material",
        "vw_low_ratio_limited_days",
        "vw_mid_ratio_illiquid_regime",
        "vw_high_ratio_illiquid_regime",
    ],
    "bad_only": ["hard_invalid_parse_or_price"],
}

HARD_INVALID_BUCKETS = {"hard_invalid_parse_or_price"}


def _to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _safe_col(frame: pd.DataFrame, name: str, default: float | str | None = np.nan) -> pd.Series:
    if name in frame.columns:
        return frame[name]
    return pd.Series([default] * len(frame), index=frame.index)


def prepare_daily_inspection_df(
    cur: pd.DataFrame,
    buckets: Iterable[str] | None = None,
) -> pd.DataFrame:
    buckets = list(buckets or DEFAULT_BUCKETS)
    inspect_df = cur[cur["daily_refined_bucket"].isin(buckets)].copy()
    for col in [
        "vw_ratio_pct",
        "vw_outside_range_abs_max",
        "vw_outside_range_pct_of_vw_max",
        "vw_problem_days",
        "rows_after_parse",
        "n_per_day",
        "v_per_day",
        "coverage_ratio_vs_business_days",
        "year",
    ]:
        if col in inspect_df.columns:
            inspect_df[col] = _to_num(inspect_df[col])
    inspect_df["ticker"] = inspect_df["ticker"].astype(str).str.upper()
    inspect_df = inspect_df.sort_values(
        ["daily_refined_bucket", "vw_ratio_pct", "vw_outside_range_abs_max"],
        ascending=[True, False, False],
    )
    return inspect_df


def resolve_buckets_for_mode(cur: pd.DataFrame, mode: str) -> list[str]:
    if mode in DEFAULT_MODES:
        return [b for b in DEFAULT_MODES[mode] if "daily_refined_bucket" in cur.columns]

    if mode == "non_good_quality":
        if "quality_policy" not in cur.columns:
            return [b for b in DEFAULT_BUCKETS if b not in HARD_INVALID_BUCKETS]
        x = cur[
            (cur["quality_policy"].astype(str).str.lower() != "good")
            & (~cur["daily_refined_bucket"].astype(str).isin(HARD_INVALID_BUCKETS))
        ].copy()
        return sorted(x["daily_refined_bucket"].dropna().astype(str).unique().tolist())

    if mode == "flagged_quality":
        if "quality_policy" not in cur.columns:
            return DEFAULT_MODES["vw_flags"]
        x = cur[
            cur["quality_policy"]
            .astype(str)
            .str.lower()
            .isin(["review", "recoverable_with_flag", "review_not_rehabilitated"])
            & (~cur["daily_refined_bucket"].astype(str).isin(HARD_INVALID_BUCKETS))
        ].copy()
        return sorted(x["daily_refined_bucket"].dropna().astype(str).unique().tolist())

    return DEFAULT_BUCKETS


def load_daily_file_view(path_str: str | Path) -> pd.DataFrame:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_parquet(path).copy()
    if "date" not in df.columns:
        raise ValueError(f"{path} no contiene columna 'date'")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["o", "h", "l", "c", "v", "vw", "n", "t"]:
        if col in df.columns:
            df[col] = _to_num(df[col])

    df = df.dropna(subset=["date"]).sort_values("date").copy()

    has_ohlc = all(col in df.columns for col in ["o", "h", "l", "c"])
    if has_ohlc:
        df["invalid_price_flag"] = (
            (df["o"] <= 0) | (df["h"] <= 0) | (df["l"] <= 0) | (df["c"] <= 0)
        )
        df["high_low_inversion_flag"] = df["h"] < df["l"]
    else:
        df["invalid_price_flag"] = False
        df["high_low_inversion_flag"] = False

    if all(col in df.columns for col in ["v", "vw", "l", "h"]):
        df["vw_below_low_flag"] = (df["v"] > 0) & (df["vw"] < df["l"])
        df["vw_above_high_flag"] = (df["v"] > 0) & (df["vw"] > df["h"])
        df["vw_outside_range_flag"] = df["vw_below_low_flag"] | df["vw_above_high_flag"]
        low_gap = (df["l"] - df["vw"]).clip(lower=0)
        high_gap = (df["vw"] - df["h"]).clip(lower=0)
        df["vw_outside_range_abs"] = pd.concat([low_gap, high_gap], axis=1).max(axis=1)
        span = (df["h"] - df["l"]).replace(0, np.nan)
        df["vw_outside_range_pct_of_span"] = 100.0 * df["vw_outside_range_abs"] / span
    else:
        df["vw_below_low_flag"] = False
        df["vw_above_high_flag"] = False
        df["vw_outside_range_flag"] = False
        df["vw_outside_range_abs"] = np.nan
        df["vw_outside_range_pct_of_span"] = np.nan

    df["hard_invalid_flag"] = df["invalid_price_flag"] | df["high_low_inversion_flag"]
    return df


def build_case_options(sub: pd.DataFrame, top_n: int = 250) -> list[tuple[str, int]]:
    opts: list[tuple[str, int]] = []
    for idx, row in sub.head(top_n).iterrows():
        ratio = row.get("vw_ratio_pct", np.nan)
        abs_max = row.get("vw_outside_range_abs_max", np.nan)
        label = (
            f"{row['ticker']} | {int(row['year']) if pd.notna(row.get('year')) else 'NA'} "
            f"| ratio={ratio:.2f}% | abs_max={abs_max:.4f}"
        )
        opts.append((label, idx))
    return opts


def render_daily_case_panel(
    row: pd.Series,
    inspect_df: pd.DataFrame,
    *,
    figsize: tuple[int, int] = (20, 18),
) -> None:
    file_path = row["file"]
    bucket = row["daily_refined_bucket"]
    peers = inspect_df[inspect_df["daily_refined_bucket"] == bucket].copy()

    display(
        Markdown(
            "\n".join(
                [
                    "## Caso seleccionado",
                    f"- `ticker`: `{row['ticker']}`",
                    f"- `year`: `{row.get('year')}`",
                    f"- `bucket`: `{bucket}`",
                    f"- `quality_policy`: `{row.get('quality_policy', 'NA')}`",
                    f"- `issues`: `{row.get('issues', 'NA')}`",
                    f"- `warns`: `{row.get('warns', 'NA')}`",
                    f"- `file`: `{file_path}`",
                ]
            )
        )
    )

    daily_df = load_daily_file_view(file_path)
    problem = daily_df[daily_df["vw_outside_range_flag"] | daily_df["hard_invalid_flag"]].copy()

    if str(bucket) in HARD_INVALID_BUCKETS:
        _render_hard_invalid_case_panel(row, inspect_df, daily_df, problem, figsize=figsize)
        return

    sns.set_theme(style="whitegrid", context="talk")
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.0, 1.1])

    ax1 = fig.add_subplot(gs[0, :])
    if all(col in daily_df.columns for col in ["l", "h"]):
        ax1.fill_between(
            daily_df["date"], daily_df["l"], daily_df["h"], color="#bfd7ea", alpha=0.35, label="low/high"
        )
    if "c" in daily_df.columns:
        ax1.plot(daily_df["date"], daily_df["c"], color="#1d3557", lw=1.1, label="close")
    if "vw" in daily_df.columns:
        vw_ok = daily_df[~daily_df["vw_outside_range_flag"]].copy()
        vw_bad = daily_df[daily_df["vw_outside_range_flag"]].copy()
        if not vw_ok.empty:
            ax1.scatter(
                vw_ok["date"],
                vw_ok["vw"],
                s=16,
                c="#457b9d",
                alpha=0.85,
                label="vw dentro de rango",
            )
        if not vw_bad.empty:
            ax1.scatter(
                vw_bad["date"],
                vw_bad["vw"],
                s=42,
                c="#d62828",
                alpha=0.95,
                label="vw fuera de rango",
                zorder=5,
            )
    invalid = daily_df[daily_df["hard_invalid_flag"]]
    if not invalid.empty and "c" in invalid.columns:
        ax1.scatter(invalid["date"], invalid["c"], s=50, c="#6a040f", marker="x", label="hard invalid")
    ax1.set_title("A. Hecho: rango diario, close y vw; los puntos rojos marcan dias fuera de rango")
    ax1.set_ylabel("price")
    ax1.legend(loc="best")

    ax2 = fig.add_subplot(gs[1, 0])
    if not problem.empty:
        sns.barplot(
            x=problem["date"].dt.strftime("%Y-%m-%d"),
            y=problem["vw_outside_range_abs"].fillna(0),
            color="#e76f51",
            ax=ax2,
        )
        ax2.tick_params(axis="x", rotation=90)
    ax2.set_title("B. Detalle: desvio absoluto por fecha problematica")
    ax2.set_ylabel("abs deviation")

    ax3 = fig.add_subplot(gs[1, 1])
    if not problem.empty:
        sns.barplot(
            x=problem["date"].dt.strftime("%Y-%m-%d"),
            y=problem["vw_outside_range_pct_of_span"].fillna(0),
            color="#f4a261",
            ax=ax3,
        )
        ax3.tick_params(axis="x", rotation=90)
    ax3.set_title("C. Detalle: desvio relativo al span por fecha")
    ax3.set_ylabel("% of span")

    ax4 = fig.add_subplot(gs[2, 0])
    peer_ratio = _to_num(_safe_col(peers, "vw_ratio_pct")).dropna()
    if not peer_ratio.empty:
        sns.histplot(peer_ratio, bins=30, color="#8ecae6", ax=ax4)
        case_ratio = float(row.get("vw_ratio_pct", np.nan))
        if pd.notna(case_ratio):
            ax4.axvline(case_ratio, color="#d62828", linestyle="--", lw=2)
    ax4.set_title("D. Contexto: distribucion del ratio dentro del bucket")
    ax4.set_xlabel("vw_ratio_pct")

    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis("off")
    case_ratio = float(row.get("vw_ratio_pct", np.nan))
    case_abs = float(row.get("vw_outside_range_abs_max", np.nan))
    ratio_pctile = float((peer_ratio <= case_ratio).mean() * 100.0) if not peer_ratio.empty and pd.notna(case_ratio) else np.nan
    peer_abs = _to_num(_safe_col(peers, "vw_outside_range_abs_max")).dropna()
    abs_pctile = float((peer_abs <= case_abs).mean() * 100.0) if not peer_abs.empty and pd.notna(case_abs) else np.nan

    summary = pd.DataFrame(
        [
            ("bucket", bucket),
            ("rows_after_parse", row.get("rows_after_parse", np.nan)),
            ("vw_problem_days", row.get("vw_problem_days", np.nan)),
            ("vw_ratio_pct", row.get("vw_ratio_pct", np.nan)),
            ("vw_abs_max", row.get("vw_outside_range_abs_max", np.nan)),
            ("vw_pct_of_vw_max", row.get("vw_outside_range_pct_of_vw_max", np.nan)),
            ("coverage_ratio", row.get("coverage_ratio_vs_business_days", np.nan)),
            ("n_per_day", row.get("n_per_day", np.nan)),
            ("v_per_day", row.get("v_per_day", np.nan)),
            ("bucket_ratio_percentile", ratio_pctile),
            ("bucket_abs_percentile", abs_pctile),
        ],
        columns=["metric", "value"],
    )
    tbl = ax5.table(cellText=summary.values, colLabels=summary.columns, loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.5)
    ax5.set_title("E. Contexto: resumen del caso dentro del bucket", pad=20)

    fig.suptitle(f"{row['ticker']} | {row.get('year')} | {bucket}", fontsize=18, y=0.995)
    plt.tight_layout()
    plt.show()

    if not problem.empty:
        top_problem = problem[
            [c for c in ["date", "o", "h", "l", "c", "vw", "v", "n", "vw_outside_range_abs", "vw_outside_range_pct_of_span"] if c in problem.columns]
        ].sort_values(
            [c for c in ["vw_outside_range_abs", "vw_outside_range_pct_of_span"] if c in problem.columns],
            ascending=False,
        ).head(15)
        display(Markdown("### Top filas problematicas"))
        display(top_problem)


def _render_hard_invalid_case_panel(
    row: pd.Series,
    inspect_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    problem: pd.DataFrame,
    *,
    figsize: tuple[int, int] = (20, 18),
) -> None:
    bucket = row["daily_refined_bucket"]
    peers = inspect_df[inspect_df["daily_refined_bucket"] == bucket].copy()

    display(
        Markdown(
            "\n".join(
                [
                    "## Caso hard invalid seleccionado",
                    f"- `ticker`: `{row['ticker']}`",
                    f"- `year`: `{row.get('year')}`",
                    f"- `bucket`: `{bucket}`",
                    f"- `quality_policy`: `{row.get('quality_policy', 'NA')}`",
                    f"- `issues`: `{row.get('issues', 'NA')}`",
                    f"- `warns`: `{row.get('warns', 'NA')}`",
                    f"- `file`: `{row['file']}`",
                ]
            )
        )
    )

    invalid_rows = daily_df[daily_df["hard_invalid_flag"]].copy()
    vw_problem = daily_df[daily_df["vw_outside_range_flag"]].copy()

    fig = _build_hard_invalid_figure(row, peers, daily_df, invalid_rows, vw_problem)
    plt.show()

    ax5 = fig.axes[-1]
    ax5.axis("off")
    summary = pd.DataFrame(
        [
            ("ticker", row["ticker"]),
            ("year", row.get("year")),
            ("bucket", bucket),
            ("quality_policy", row.get("quality_policy", np.nan)),
            ("rows_after_parse", row.get("rows_after_parse", np.nan)),
            ("invalid_rows", len(invalid_rows)),
            ("vw_problem_days", row.get("vw_problem_days", np.nan)),
            ("coverage_ratio", row.get("coverage_ratio_vs_business_days", np.nan)),
            ("file", row.get("file", "")),
        ],
        columns=["metric", "value"],
    )
    if not invalid_rows.empty:
        display(Markdown("### Filas invalidas duras"))
        cols = [c for c in ["date", "o", "h", "l", "c", "vw", "v", "n", "invalid_price_flag", "high_low_inversion_flag", "hard_invalid_flag"] if c in invalid_rows.columns]
        display(invalid_rows[cols].head(25))
    elif not vw_problem.empty:
        display(Markdown("### Filas marcadas por vw en un caso hard invalid"))
        cols = [c for c in ["date", "o", "h", "l", "c", "vw", "v", "n", "vw_outside_range_abs", "vw_outside_range_pct_of_span"] if c in vw_problem.columns]
        display(vw_problem[cols].head(25))


def _build_hard_invalid_figure(
    row: pd.Series,
    peers: pd.DataFrame,
    daily_df: pd.DataFrame,
    invalid_rows: pd.DataFrame,
    vw_problem: pd.DataFrame,
):
    sns.set_theme(style="whitegrid", context="talk")
    fig = plt.figure(figsize=(22, 20))
    gs = fig.add_gridspec(4, 2, height_ratios=[1.0, 1.15, 1.15, 0.9])

    ax1 = fig.add_subplot(gs[0, :])
    if all(col in daily_df.columns for col in ["l", "h"]):
        ax1.fill_between(daily_df["date"], daily_df["l"], daily_df["h"], color="#bfd7ea", alpha=0.28, label="low/high")
    if "c" in daily_df.columns:
        ax1.plot(daily_df["date"], daily_df["c"], color="#1d3557", lw=1.15, label="close")
    if not invalid_rows.empty:
        y = invalid_rows["c"] if "c" in invalid_rows.columns else np.zeros(len(invalid_rows))
        ax1.scatter(invalid_rows["date"], y, s=70, c="#6a040f", marker="x", label="hard invalid")
    ax1.set_title("A. Contexto del file con fechas invalidas marcadas")
    ax1.legend(loc="best")

    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    ax2.axis("off")
    ax3.axis("off")
    _draw_hard_invalid_cut_criteria(ax2, ax3, invalid_rows)

    candidates = invalid_rows.copy()
    if candidates.empty:
        candidates = vw_problem.copy()
    candidates = candidates.head(2)
    sub_axes = [fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])]
    for ax, (_, bad_row) in zip(sub_axes, candidates.iterrows()):
        _draw_single_day_failure(ax, bad_row)
    for ax in sub_axes[len(candidates):]:
        ax.axis("off")

    ax4 = fig.add_subplot(gs[3, 0])
    peer_rows = _to_num(_safe_col(peers, "rows_after_parse")).dropna()
    if not peer_rows.empty:
        sns.histplot(peer_rows, bins=30, color="#8ecae6", ax=ax4)
        case_rows = float(row.get("rows_after_parse", np.nan))
        if pd.notna(case_rows):
            ax4.axvline(case_rows, color="#d62828", linestyle="--", lw=2)
    ax4.set_title("D. Contexto del bucket: rows_after_parse")

    ax5 = fig.add_subplot(gs[3, 1])
    ax5.axis("off")
    summary = pd.DataFrame(
        [
            ("ticker", row.get("ticker")),
            ("year", row.get("year")),
            ("bucket", row.get("daily_refined_bucket")),
            ("quality_policy", row.get("quality_policy", np.nan)),
            ("rows_after_parse", row.get("rows_after_parse", np.nan)),
            ("invalid_rows", len(invalid_rows)),
            ("vw_problem_days", row.get("vw_problem_days", np.nan)),
            ("coverage_ratio", row.get("coverage_ratio_vs_business_days", np.nan)),
            ("file", row.get("file", "")),
        ],
        columns=["metric", "value"],
    )
    tbl = ax5.table(cellText=summary.values, colLabels=summary.columns, loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.5)
    ax5.set_title("E. Resumen del caso", pad=20)

    fig.suptitle(f"{row.get('ticker')} | {row.get('year')} | {row.get('daily_refined_bucket')}", fontsize=18, y=0.995)
    plt.tight_layout()
    return fig


def _draw_hard_invalid_cut_criteria(ax_left, ax_right, invalid_rows: pd.DataFrame) -> None:
    invalid_price = invalid_rows[invalid_rows.get("invalid_price_flag", False)].copy()
    high_low = invalid_rows[invalid_rows.get("high_low_inversion_flag", False)].copy()

    left_lines = ["B. Criterio fisico: invalid_price_rows"]
    if invalid_price.empty:
        left_lines.append("Sin filas con OHLC <= 0")
    else:
        for _, r in invalid_price.head(10).iterrows():
            parts = []
            for c in ["o", "h", "l", "c"]:
                v = r.get(c, np.nan)
                if pd.notna(v) and v <= 0:
                    parts.append(f"{c}={v}")
            left_lines.append(f"{str(r['date'])[:10]} -> " + ", ".join(parts))
    ax_left.text(0.01, 0.98, "\n".join(left_lines), va="top", ha="left", family="monospace", fontsize=11)

    right_lines = ["C. Criterio fisico: high < low"]
    if high_low.empty:
        right_lines.append("Sin filas con high < low")
    else:
        for _, r in high_low.head(10).iterrows():
            right_lines.append(f"{str(r['date'])[:10]} -> high={r.get('h')} < low={r.get('l')}")
    ax_right.text(0.01, 0.98, "\n".join(right_lines), va="top", ha="left", family="monospace", fontsize=11)


def _draw_single_day_failure(ax, row: pd.Series) -> None:
    date_label = str(row.get("date"))[:10]
    o = row.get("o", np.nan)
    h = row.get("h", np.nan)
    l = row.get("l", np.nan)
    c = row.get("c", np.nan)
    vw = row.get("vw", np.nan)

    vals = [x for x in [o, h, l, c, vw] if pd.notna(x)]
    if not vals:
        ax.text(0.5, 0.5, f"{date_label}\nSin valores ploteables", ha="center", va="center")
        ax.axis("off")
        return

    ymin = min(vals)
    ymax = max(vals)
    pad = max((ymax - ymin) * 0.25, 1e-6)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_xlim(-0.5, 1.5)

    if pd.notna(l) and pd.notna(h):
        ax.vlines(0, l, h, color="#1d3557", lw=5, alpha=0.9)
        ax.hlines([l, h], -0.14, 0.14, color="#1d3557", lw=3)
        ax.text(0.18, h, f"h={h}", va="center", fontsize=10)
        ax.text(0.18, l, f"l={l}", va="center", fontsize=10)
    if pd.notna(o):
        color = "#d62828" if o <= 0 else "#2a9d8f"
        ax.hlines(o, -0.36, -0.06, color=color, lw=3)
        ax.text(-0.4, o, f"o={o}", ha="right", va="center", fontsize=10)
    if pd.notna(c):
        color = "#d62828" if c <= 0 else "#2a9d8f"
        ax.hlines(c, 0.06, 0.36, color=color, lw=3)
        ax.text(0.4, c, f"c={c}", ha="left", va="center", fontsize=10)
    if pd.notna(vw):
        ax.scatter([0.9], [vw], c="#7b2cbf", s=60, zorder=5)
        ax.text(0.96, vw, f"vw={vw}", ha="left", va="center", fontsize=10)

    notes = []
    if pd.notna(o) and o <= 0:
        notes.append("open <= 0")
    if pd.notna(h) and h <= 0:
        notes.append("high <= 0")
    if pd.notna(l) and l <= 0:
        notes.append("low <= 0")
    if pd.notna(c) and c <= 0:
        notes.append("close <= 0")
    if pd.notna(h) and pd.notna(l) and h < l:
        notes.append("high < low")
    if pd.notna(vw) and pd.notna(h) and pd.notna(l):
        if vw < l:
            notes.append("vw < low")
        elif vw > h:
            notes.append("vw > high")

    ax.set_title(f"Fila fisicamente problematica: {date_label}")
    ax.set_xticks([])
    ax.grid(True, axis="y", alpha=0.25)
    if notes:
        ax.text(0.02, 0.98, "\n".join(notes), transform=ax.transAxes, va="top", ha="left", fontsize=10, bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "#cccccc"})


def build_daily_case_selector(
    cur: pd.DataFrame,
    *,
    mode: str = "all_no_good",
    buckets: Iterable[str] | None = None,
    top_n: int = 250,
) -> widgets.VBox:
    resolved_buckets = list(buckets) if buckets is not None else resolve_buckets_for_mode(cur, mode)
    inspect_df = prepare_daily_inspection_df(cur, buckets=resolved_buckets)

    bucket_options = sorted(inspect_df["daily_refined_bucket"].dropna().astype(str).unique().tolist())
    bucket_dd = widgets.Dropdown(
        options=bucket_options,
        description="bucket",
        layout=widgets.Layout(width="340px"),
    )
    file_dd = widgets.Dropdown(description="file", layout=widgets.Layout(width="980px"))
    out = widgets.Output()

    def refresh_files(*_):
        with out:
            clear_output(wait=True)
        sub = inspect_df[inspect_df["daily_refined_bucket"] == bucket_dd.value].copy()
        file_dd.options = build_case_options(sub, top_n=top_n)
        file_dd.value = file_dd.options[0][1] if file_dd.options else None

    def render(*_):
        with out:
            clear_output(wait=True)
            if file_dd.value is None:
                display(Markdown("## Sin casos para esta seleccion"))
                return
            row = inspect_df.loc[file_dd.value]
            try:
                render_daily_case_panel(row, inspect_df)
            except FileNotFoundError as exc:
                display(Markdown("## File ausente"))
                print(str(exc))

    bucket_dd.observe(refresh_files, names="value")
    file_dd.observe(render, names="value")
    refresh_files()
    render()
    return widgets.VBox([widgets.HBox([bucket_dd]), file_dd, out])


def _select_representative_cases(bucket_df: pd.DataFrame, max_cases: int) -> pd.DataFrame:
    if bucket_df.empty:
        return bucket_df.copy()

    work = bucket_df.copy()
    metric_cols = [c for c in ["vw_ratio_pct", "vw_outside_range_abs_max", "coverage_ratio_vs_business_days"] if c in work.columns]
    for col in metric_cols:
        work[col] = _to_num(work[col])

    selected_idx: list[int] = []

    def add_index(idx) -> None:
        if idx not in selected_idx:
            selected_idx.append(idx)

    # Extremos altos por ratio y abs_max.
    if "vw_ratio_pct" in work.columns:
        for idx in work.sort_values("vw_ratio_pct", ascending=False).head(max_cases).index[: max(2, max_cases // 3)]:
            add_index(idx)
    if "vw_outside_range_abs_max" in work.columns:
        for idx in work.sort_values("vw_outside_range_abs_max", ascending=False).head(max_cases).index[: max(2, max_cases // 3)]:
            add_index(idx)

    # Casos mediana / intermedios para no sesgar solo a extremos.
    if "vw_ratio_pct" in work.columns and work["vw_ratio_pct"].notna().sum() >= 3:
        ordered = work.sort_values("vw_ratio_pct")
        for q in [0.2, 0.5, 0.8]:
            pos = min(int(round((len(ordered) - 1) * q)), len(ordered) - 1)
            add_index(ordered.index[pos])

    # Casos de coverage bajo si existen.
    if "coverage_ratio_vs_business_days" in work.columns:
        low_cov = work.sort_values("coverage_ratio_vs_business_days", ascending=True).head(max(1, max_cases // 4))
        for idx in low_cov.index:
            add_index(idx)

    # Completar muestra con espaciado regular.
    if len(selected_idx) < max_cases:
        ordered = work.sort_values(
            [c for c in ["vw_ratio_pct", "vw_outside_range_abs_max"] if c in work.columns],
            ascending=False,
        )
        positions = np.linspace(0, max(len(ordered) - 1, 0), num=min(max_cases, len(ordered)), dtype=int)
        for pos in positions:
            add_index(ordered.index[pos])
            if len(selected_idx) >= max_cases:
                break

    return work.loc[selected_idx[:max_cases]].copy()


def export_daily_case_samples(
    cur: pd.DataFrame,
    output_dir: str | Path,
    *,
    mode: str = "all_no_good",
    buckets: Iterable[str] | None = None,
    cases_per_bucket: int = 12,
    dpi: int = 140,
    clean_output_dir: bool = True,
) -> pd.DataFrame:
    resolved_buckets = list(buckets) if buckets is not None else resolve_buckets_for_mode(cur, mode)
    inspect_df = prepare_daily_inspection_df(cur, buckets=resolved_buckets)
    output_dir = Path(output_dir)
    if clean_output_dir and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict] = []

    for bucket in sorted(inspect_df["daily_refined_bucket"].dropna().astype(str).unique().tolist()):
        bucket_df = inspect_df[inspect_df["daily_refined_bucket"] == bucket].copy()
        if mode in {"hard_invalid", "bad_only"} or bucket in HARD_INVALID_BUCKETS:
            sample_df = bucket_df.copy()
        else:
            sample_df = _select_representative_cases(bucket_df, max_cases=cases_per_bucket)
        bucket_slug = bucket.lower().replace(" ", "_")
        bucket_dir = output_dir / bucket_slug
        bucket_dir.mkdir(parents=True, exist_ok=True)

        for _, row in sample_df.iterrows():
            ticker = str(row["ticker"]).upper()
            year = int(row["year"]) if pd.notna(row.get("year")) else "NA"
            stem = f"{ticker}_{year}"
            png_path = bucket_dir / f"{stem}.png"
            csv_path = bucket_dir / f"{stem}_problem_rows.csv"

            daily_df = load_daily_file_view(row["file"])
            problem = daily_df[daily_df["vw_outside_range_flag"] | daily_df["hard_invalid_flag"]].copy()

            peers = inspect_df[inspect_df["daily_refined_bucket"] == bucket].copy()
            fig = _build_export_figure(row, peers, daily_df, problem)
            fig.savefig(png_path, dpi=dpi, bbox_inches="tight")
            plt.close(fig)

            if not problem.empty:
                export_cols = [c for c in ["date", "o", "h", "l", "c", "vw", "v", "n", "vw_outside_range_abs", "vw_outside_range_pct_of_span", "invalid_price_flag", "hard_invalid_flag"] if c in problem.columns]
                problem[export_cols].sort_values(
                    [c for c in ["vw_outside_range_abs", "vw_outside_range_pct_of_span"] if c in problem.columns],
                    ascending=False,
                ).to_csv(csv_path, index=False)

            manifest_rows.append(
                {
                    "bucket": bucket,
                    "ticker": ticker,
                    "year": year,
                    "file": row.get("file", ""),
                    "image_path": str(png_path),
                    "problem_rows_csv": str(csv_path) if not problem.empty else "",
                    "vw_ratio_pct": row.get("vw_ratio_pct", np.nan),
                    "vw_outside_range_abs_max": row.get("vw_outside_range_abs_max", np.nan),
                    "coverage_ratio_vs_business_days": row.get("coverage_ratio_vs_business_days", np.nan),
                }
            )

    manifest = pd.DataFrame(manifest_rows)
    manifest_path = output_dir / "daily_case_samples_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    return manifest


def _build_export_figure(
    row: pd.Series,
    peers: pd.DataFrame,
    daily_df: pd.DataFrame,
    problem: pd.DataFrame,
):
    bucket = row["daily_refined_bucket"]
    sns.set_theme(style="whitegrid", context="talk")

    if str(bucket) in HARD_INVALID_BUCKETS:
        invalid_rows = daily_df[daily_df["hard_invalid_flag"]].copy()
        return _build_hard_invalid_figure(row, peers, daily_df, invalid_rows, problem)

    fig = plt.figure(figsize=(20, 18))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.0, 1.1])

    ax1 = fig.add_subplot(gs[0, :])
    if all(col in daily_df.columns for col in ["l", "h"]):
        ax1.fill_between(daily_df["date"], daily_df["l"], daily_df["h"], color="#bfd7ea", alpha=0.35, label="low/high")
    if "c" in daily_df.columns:
        ax1.plot(daily_df["date"], daily_df["c"], color="#1d3557", lw=1.1, label="close")
    if "vw" in daily_df.columns:
        colors = np.where(daily_df["vw_outside_range_flag"], "#d62828", "#457b9d")
        ax1.scatter(daily_df["date"], daily_df["vw"], s=16, c=colors, alpha=0.85, label="vw")
    invalid = daily_df[daily_df["hard_invalid_flag"]]
    if not invalid.empty and "c" in invalid.columns:
        ax1.scatter(invalid["date"], invalid["c"], s=50, c="#6a040f", marker="x", label="hard invalid")
    ax1.set_title("A. Hecho")
    ax1.legend(loc="best")

    ax2 = fig.add_subplot(gs[1, 0])
    if not problem.empty:
        sns.barplot(x=problem["date"].dt.strftime("%Y-%m-%d"), y=problem["vw_outside_range_abs"].fillna(0), color="#e76f51", ax=ax2)
        ax2.tick_params(axis="x", rotation=90)
    ax2.set_title("B. Desvio absoluto")

    ax3 = fig.add_subplot(gs[1, 1])
    if not problem.empty:
        sns.barplot(x=problem["date"].dt.strftime("%Y-%m-%d"), y=problem["vw_outside_range_pct_of_span"].fillna(0), color="#f4a261", ax=ax3)
        ax3.tick_params(axis="x", rotation=90)
    ax3.set_title("C. Desvio relativo al span")

    ax4 = fig.add_subplot(gs[2, 0])
    peer_ratio = _to_num(_safe_col(peers, "vw_ratio_pct")).dropna()
    if not peer_ratio.empty:
        sns.histplot(peer_ratio, bins=30, color="#8ecae6", ax=ax4)
        case_ratio = float(row.get("vw_ratio_pct", np.nan))
        if pd.notna(case_ratio):
            ax4.axvline(case_ratio, color="#d62828", linestyle="--", lw=2)
    ax4.set_title("D. Contexto bucket")

    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis("off")
    summary = pd.DataFrame(
        [
            ("ticker", row.get("ticker")),
            ("year", row.get("year")),
            ("bucket", bucket),
            ("quality_policy", row.get("quality_policy", np.nan)),
            ("rows_after_parse", row.get("rows_after_parse", np.nan)),
            ("vw_problem_days", row.get("vw_problem_days", np.nan)),
            ("vw_ratio_pct", row.get("vw_ratio_pct", np.nan)),
            ("vw_abs_max", row.get("vw_outside_range_abs_max", np.nan)),
            ("coverage_ratio", row.get("coverage_ratio_vs_business_days", np.nan)),
            ("file", row.get("file", "")),
        ],
        columns=["metric", "value"],
    )
    tbl = ax5.table(cellText=summary.values, colLabels=summary.columns, loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.4)
    ax5.set_title("E. Resumen del caso", pad=20)

    fig.suptitle(f"{row.get('ticker')} | {row.get('year')} | {bucket}", fontsize=18, y=0.995)
    plt.tight_layout()
    return fig
