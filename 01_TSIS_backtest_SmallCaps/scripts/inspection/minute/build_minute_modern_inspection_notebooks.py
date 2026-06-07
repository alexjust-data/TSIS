from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"


COMMON_SETUP = r"""
from __future__ import annotations

from pathlib import Path
import ast
import json
import math

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, clear_output, display

sns.set_theme(style="whitegrid", context="notebook")
pd.set_option("display.max_columns", 160)
pd.set_option("display.max_rows", 120)
pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 180)

PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"
EVIDENCE_ROOT = DOSSIER_DIR / "evidence_assets"
RAW_CLOSEOUT_ROOT = EVIDENCE_ROOT / "raw_1m_lt1b_closeout"
CORE_ROOT = EVIDENCE_ROOT / "core_quality"
CORE_ROOT.mkdir(parents=True, exist_ok=True)

RAW_CLOSEOUT_PATH = RAW_CLOSEOUT_ROOT / "raw_1m_lt1b_filtered_closeout.parquet"
RAW_BUCKET_SUMMARY_PATH = RAW_CLOSEOUT_ROOT / "raw_1m_lt1b_bucket_summary.csv"
RAW_EXEC_SUMMARY_PATH = RAW_CLOSEOUT_ROOT / "raw_1m_lt1b_exec_summary.csv"

def _to_num(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out

def _as_listish(value):
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            value = value.tolist()
        except Exception:
            pass
    if isinstance(value, list):
        if len(value) == 1 and isinstance(value[0], str) and value[0].strip() in {"", "[]"}:
            return []
        return value
    if isinstance(value, tuple):
        if len(value) == 1 and isinstance(value[0], str) and value[0].strip() in {"", "[]"}:
            return []
        return list(value)
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text or text == "[]":
            return []
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        except Exception:
            return [text]
    return [str(value)]

CORE_NUMERIC_COLS = [
    "m.rows_after_parse",
    "m.active_days",
    "m.active_minutes",
    "m.business_days_est",
    "m.coverage_ratio_vs_active_days_est",
    "m.dates_outside_partition_month",
    "m.duplicate_ts_utc_rows",
    "m.high_low_inversion_rows",
    "m.max_gap_days",
    "m.negative_or_zero_ohlc_rows",
    "m.negative_volume_rows",
    "m.ticker_nunique",
    "m.month_nunique",
    "m.year_nunique",
    "m.ts_utc_date_mismatch_rows",
    "m.vw_outside_range_rows",
    "m.v_sum",
    "m.n_sum",
    "vw_ratio_pct",
    "vw_per_active_day",
]

def load_raw_closeout() -> pd.DataFrame:
    df = pd.read_parquet(RAW_CLOSEOUT_PATH).copy()
    df = _to_num(df, CORE_NUMERIC_COLS)
    for col in ["issues_list", "warns_list", "m.missing_required_cols", "m.dtype_mismatches"]:
        if col in df.columns:
            df[col] = df[col].map(_as_listish)
    df["year_month"] = df["year"].astype(int).astype(str) + "-" + df["month"].astype(int).astype(str).str.zfill(2)
    df["case_key"] = df["ticker"].astype(str) + "|" + df["year"].astype(int).astype(str) + "|" + df["month"].astype(int).astype(str).str.zfill(2)
    return df

def classify_core_quality(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    missing_required = out.get("m.missing_required_cols", pd.Series([[]] * len(out), index=out.index)).map(len)
    dtype_mismatch = out.get("m.dtype_mismatches", pd.Series([[]] * len(out), index=out.index)).map(len)
    dataset_read_ok = out.get("m.dataset_read_compatible", pd.Series(True, index=out.index)).fillna(True).astype(bool)
    known_schema_merge_warning = ~dataset_read_ok
    hard_parse = out["operational_decision"].astype(str).eq("QUARANTINE_PARSE_INVALID")
    hard_price = out["operational_decision"].astype(str).eq("QUARANTINE_PRICE_INVALID")

    # `dataset_read_compatible = false` is a known aggregate schema-merge warning in
    # this historical 1m closeout. It must be preserved as a family, but it must not
    # by itself demote OHLCV core quality when the individual file parsed and core
    # price/time/volume checks are clean.
    structural_issue = missing_required.gt(0) | dtype_mismatch.gt(0)
    partition_issue = (
        out["m.dates_outside_partition_month"].fillna(0).gt(0)
        | out["m.ticker_nunique"].fillna(1).gt(1)
        | out["m.month_nunique"].fillna(1).gt(1)
        | out["m.year_nunique"].fillna(1).gt(1)
    )
    timestamp_issue = (
        out["m.duplicate_ts_utc_rows"].fillna(0).gt(0)
        | out["m.ts_utc_date_mismatch_rows"].fillna(0).gt(0)
    )
    ohlc_issue = (
        out["m.negative_or_zero_ohlc_rows"].fillna(0).gt(0)
        | out["m.high_low_inversion_rows"].fillna(0).gt(0)
    )
    volume_issue = out["m.negative_volume_rows"].fillna(0).gt(0)
    empty_or_unparsed = out["m.rows_after_parse"].fillna(0).le(0)
    sparse_review = (
        out["m.active_days"].fillna(0).lt(3)
        | out["m.coverage_ratio_vs_active_days_est"].fillna(0).lt(0.10)
    )
    gap_review = out["m.max_gap_days"].fillna(0).ge(10)

    out["readability_state"] = np.where(
        hard_parse | empty_or_unparsed,
        "bad",
        np.where(structural_issue, "review", np.where(known_schema_merge_warning, "schema_warning", "good")),
    )
    out["partition_state"] = np.where(partition_issue, "review", "good")
    out["timestamp_state"] = np.where(timestamp_issue, "review", "good")
    out["ohlc_state"] = np.where(hard_price | ohlc_issue, "bad", "good")
    out["volume_state"] = np.where(volume_issue, "bad", "good")
    out["coverage_state"] = np.where(sparse_review | gap_review, "review", "good")

    bad_core = hard_parse | hard_price | empty_or_unparsed | ohlc_issue | volume_issue
    review_core = structural_issue | partition_issue | timestamp_issue | sparse_review | gap_review
    out["core_quality_state"] = np.select(
        [bad_core, review_core],
        ["bad", "review"],
        default="good",
    )

    families = []
    for idx, row in out.iterrows():
        fam = []
        if row.get("operational_decision") == "QUARANTINE_PARSE_INVALID" or pd.to_numeric(row.get("m.rows_after_parse"), errors="coerce") <= 0:
            fam.append("parse_or_empty")
        if row.get("operational_decision") == "QUARANTINE_PRICE_INVALID" or pd.to_numeric(row.get("m.negative_or_zero_ohlc_rows"), errors="coerce") > 0 or pd.to_numeric(row.get("m.high_low_inversion_rows"), errors="coerce") > 0:
            fam.append("ohlc_price_invalid")
        if bool(row.get("m.dataset_read_compatible")) is False:
            fam.append("schema_readability_known_warning")
        if len(row.get("m.missing_required_cols", [])) > 0:
            fam.append("missing_required_cols")
        if len(row.get("m.dtype_mismatches", [])) > 0:
            fam.append("dtype_mismatch")
        if pd.to_numeric(row.get("m.dates_outside_partition_month"), errors="coerce") > 0 or pd.to_numeric(row.get("m.ticker_nunique"), errors="coerce") > 1 or pd.to_numeric(row.get("m.month_nunique"), errors="coerce") > 1 or pd.to_numeric(row.get("m.year_nunique"), errors="coerce") > 1:
            fam.append("partition_identity")
        if pd.to_numeric(row.get("m.duplicate_ts_utc_rows"), errors="coerce") > 0 or pd.to_numeric(row.get("m.ts_utc_date_mismatch_rows"), errors="coerce") > 0:
            fam.append("timestamp_integrity")
        if pd.to_numeric(row.get("m.negative_volume_rows"), errors="coerce") > 0:
            fam.append("volume_invalid")
        if pd.to_numeric(row.get("m.active_days"), errors="coerce") < 3 or pd.to_numeric(row.get("m.coverage_ratio_vs_active_days_est"), errors="coerce") < 0.10:
            fam.append("coverage_sparse")
        if pd.to_numeric(row.get("m.max_gap_days"), errors="coerce") >= 10:
            fam.append("large_internal_gap")
        if not fam:
            fam.append("core_usable")
        families.append("|".join(fam))
    out["core_issue_family"] = families

    vw_tax = out.get("vw_taxonomy", pd.Series("vw_not_flagged", index=out.index)).fillna("vw_not_flagged").astype(str)
    out["vw_quality_state"] = np.select(
        [
            vw_tax.eq("vw_mild_low_ratio") | vw_tax.eq("vw_not_flagged"),
            vw_tax.isin(["vw_moderate_ratio", "vw_severe_tiny_base", "vw_severe_small_mass"]),
            vw_tax.isin(["vw_severe_large_mass_diffuse", "vw_severe_large_mass_persistent"]),
        ],
        ["good", "review", "bad"],
        default="review",
    )
    out["vw_issue_family"] = vw_tax
    out["combined_quality_state"] = np.where(
        out["core_quality_state"].eq("bad"),
        "core_bad",
        np.where(
            out["core_quality_state"].eq("review") & out["vw_quality_state"].eq("bad"),
            "core_review_vw_bad",
            np.where(
                out["core_quality_state"].eq("review"),
                "core_review",
                np.where(out["vw_quality_state"].eq("bad"), "core_good_vw_bad", "core_good"),
            ),
        ),
    )
    out["allowed_consumption"] = np.select(
        [
            out["core_quality_state"].eq("bad"),
            out["core_quality_state"].eq("review"),
            out["core_quality_state"].eq("good") & out["vw_quality_state"].eq("bad"),
            out["core_quality_state"].eq("good") & out["vw_quality_state"].isin(["good", "review"]),
        ],
        [
            "forensic_only",
            "flagged_research_or_sensitivity",
            "ohlcv_without_vw_only",
            "controlled_ohlcv_research",
        ],
        default="forensic_review",
    )
    return out

def load_core_manifest() -> pd.DataFrame:
    manifest_path = CORE_ROOT / "minute_core_quality_manifest_v0_1.parquet"
    if manifest_path.exists():
        return pd.read_parquet(manifest_path)
    return classify_core_quality(load_raw_closeout())

def save_core_manifest(df: pd.DataFrame) -> None:
    CORE_ROOT.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CORE_ROOT / "minute_core_quality_manifest_v0_1.parquet", index=False)
    summary = []
    for col in ["core_quality_state", "vw_quality_state", "combined_quality_state", "core_issue_family", "vw_issue_family", "allowed_consumption"]:
        counts = df[col].astype(str).value_counts(dropna=False).rename_axis(col).reset_index(name="count")
        counts["pct"] = 100.0 * counts["count"] / max(len(df), 1)
        counts["dimension"] = col
        summary.append(counts.rename(columns={col: "key"}))
    pd.concat(summary, ignore_index=True).to_csv(CORE_ROOT / "minute_core_quality_family_counts_v0_1.csv", index=False)
    exec_summary = pd.DataFrame([
        {"metric": "rows", "value": len(df)},
        {"metric": "tickers", "value": df["ticker"].nunique()},
        {"metric": "year_min", "value": int(df["year"].min())},
        {"metric": "year_max", "value": int(df["year"].max())},
        {"metric": "core_good_rows", "value": int(df["core_quality_state"].eq("good").sum())},
        {"metric": "core_review_rows", "value": int(df["core_quality_state"].eq("review").sum())},
        {"metric": "core_bad_rows", "value": int(df["core_quality_state"].eq("bad").sum())},
        {"metric": "core_good_vw_bad_rows", "value": int(df["combined_quality_state"].eq("core_good_vw_bad").sum())},
    ])
    exec_summary.to_csv(CORE_ROOT / "minute_core_quality_summary_v0_1.csv", index=False)

def state_palette():
    return {
        "good": "#2f9e44",
        "review": "#f08c00",
        "bad": "#e03131",
        "core_good": "#2f9e44",
        "core_review": "#f08c00",
        "core_bad": "#e03131",
        "core_good_vw_bad": "#5c7cfa",
        "core_review_vw_bad": "#ae3ec9",
    }

def display_case_summary(row: pd.Series) -> None:
    fields = [
        "ticker", "year", "month", "case_key", "core_quality_state", "vw_quality_state",
        "combined_quality_state", "core_issue_family", "vw_issue_family", "allowed_consumption",
        "operational_decision", "final_policy_bucket_lt1b", "file",
    ]
    cols = [c for c in fields if c in row.index]
    display(pd.DataFrame([row[cols].to_dict()]))
    msg = (
        f"**Lectura institucional:** `{row.get('combined_quality_state')}`. "
        f"Core=`{row.get('core_quality_state')}`, vw=`{row.get('vw_quality_state')}`. "
        f"Consumo permitido: `{row.get('allowed_consumption')}`."
    )
    display(Markdown(msg))

def plot_case_panel(row: pd.Series) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 9), constrained_layout=True)
    fig.suptitle(f"{row.get('ticker')} {int(row.get('year'))}-{int(row.get('month')):02d} | {row.get('combined_quality_state')}", fontsize=14)

    axes[0, 0].bar(
        ["o_min", "l_min", "c_max", "h_max"],
        [row.get("m.o_min", np.nan), row.get("m.l_min", np.nan), row.get("m.c_max", np.nan), row.get("m.h_max", np.nan)],
        color=["#4c78a8", "#72b7b2", "#f58518", "#e45756"],
    )
    axes[0, 0].set_title("OHLC price envelope")
    axes[0, 0].set_ylabel("raw price")

    axes[0, 1].bar(
        ["active_days", "active_minutes", "business_days_est", "max_gap_days"],
        [row.get("m.active_days", np.nan), row.get("m.active_minutes", np.nan), row.get("m.business_days_est", np.nan), row.get("m.max_gap_days", np.nan)],
        color=["#54a24b", "#4c78a8", "#b279a2", "#e45756"],
    )
    axes[0, 1].set_title("Coverage and density")

    axes[1, 0].bar(
        ["dup_ts", "date_mismatch", "outside_month", "ohlc_invalid", "volume_invalid"],
        [
            row.get("m.duplicate_ts_utc_rows", 0),
            row.get("m.ts_utc_date_mismatch_rows", 0),
            row.get("m.dates_outside_partition_month", 0),
            row.get("m.negative_or_zero_ohlc_rows", 0) + row.get("m.high_low_inversion_rows", 0),
            row.get("m.negative_volume_rows", 0),
        ],
        color="#e03131",
    )
    axes[1, 0].set_title("Core diagnostics")
    axes[1, 0].tick_params(axis="x", rotation=20)

    axes[1, 1].bar(
        ["vw_rows", "vw_ratio_pct", "vw_per_day"],
        [row.get("m.vw_outside_range_rows", 0), row.get("vw_ratio_pct", 0), row.get("vw_per_active_day", 0)],
        color=["#5c7cfa", "#748ffc", "#91a7ff"],
    )
    axes[1, 1].set_title("VW diagnostics, secondary to core")
    plt.show()

def filtered_options(df: pd.DataFrame, filters: dict[str, str]) -> pd.DataFrame:
    out = df.copy()
    for col, val in filters.items():
        if val and val != "ALL" and col in out.columns:
            out = out[out[col].astype(str).eq(str(val))]
    return out
"""


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def write_notebook(path: Path, cells: list) -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.x"},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        nbf.write(nb, f)


def build_00_universe() -> None:
    cells = [
        md(
            """
            # Minute 00 - Universe Quality Overview `v0_1`

            Este notebook moderniza la lectura global de `ohlcv_1m_raw` en alcance `<1B>`.

            La pregunta principal no es si `vw` falla. La pregunta principal es si el universo de barras
            `ticker-month` tiene calidad core suficiente como OHLCV raw, y donde se separa esa calidad de
            la subcalidad `vw`.
            """
        ),
        code(COMMON_SETUP),
        code(
            """
            df = classify_core_quality(load_raw_closeout())
            save_core_manifest(df)
            display(Markdown("## Resumen ejecutivo"))
            display(pd.read_csv(CORE_ROOT / "minute_core_quality_summary_v0_1.csv"))
            display(Markdown("## Distribuciones principales"))
            for col in ["core_quality_state", "vw_quality_state", "combined_quality_state", "allowed_consumption"]:
                counts = df[col].astype(str).value_counts().rename_axis(col).reset_index(name="count")
                counts["pct"] = 100.0 * counts["count"] / len(df)
                display(counts)
            """
        ),
        code(
            """
            pal = state_palette()
            fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)

            for ax, col, title in [
                (axes[0,0], "core_quality_state", "Core quality state"),
                (axes[0,1], "vw_quality_state", "VW quality state"),
                (axes[1,0], "combined_quality_state", "Combined state"),
                (axes[1,1], "allowed_consumption", "Allowed consumption"),
            ]:
                counts = df[col].astype(str).value_counts().reset_index()
                counts.columns = [col, "count"]
                ax.bar(counts[col], counts["count"], color=[pal.get(x, "#4c78a8") for x in counts[col]])
                ax.set_title(title)
                ax.set_ylabel("ticker-month files")
                ax.tick_params(axis="x", rotation=25)
            plt.show()
            """
        ),
        code(
            """
            yearly = df.groupby(["year", "core_quality_state"]).size().reset_index(name="count")
            pivot = yearly.pivot(index="year", columns="core_quality_state", values="count").fillna(0)
            pivot.plot(kind="bar", stacked=True, figsize=(16, 5), color=[state_palette().get(c, "#4c78a8") for c in pivot.columns])
            plt.title("Core quality by year")
            plt.ylabel("ticker-month files")
            plt.tight_layout()
            plt.show()

            heat = df.groupby(["year", "month"]).size().reset_index(name="count").pivot(index="year", columns="month", values="count").fillna(0)
            plt.figure(figsize=(14, 7))
            sns.heatmap(heat, cmap="Blues")
            plt.title("Universe coverage heatmap by year-month")
            plt.ylabel("year")
            plt.xlabel("month")
            plt.show()
            """
        ),
        code(
            """
            display(Markdown("## Widget de exploracion global"))
            dim_dd = widgets.Dropdown(
                description="dimension",
                options=["core_quality_state", "vw_quality_state", "combined_quality_state", "core_issue_family", "vw_issue_family", "allowed_consumption"],
                value="combined_quality_state",
                layout=widgets.Layout(width="360px"),
            )
            top_n = widgets.IntSlider(description="top_n", min=5, max=50, step=5, value=15)
            out = widgets.Output()

            def render(*_):
                with out:
                    clear_output(wait=True)
                    col = dim_dd.value
                    counts = df[col].astype(str).value_counts().head(top_n.value).rename_axis(col).reset_index(name="count")
                    counts["pct"] = 100.0 * counts["count"] / len(df)
                    display(counts)
                    plt.figure(figsize=(12, 5))
                    sns.barplot(data=counts, y=col, x="count", color="#4c78a8")
                    plt.title(f"Top {top_n.value} - {col}")
                    plt.tight_layout()
                    plt.show()

            dim_dd.observe(render, names="value")
            top_n.observe(render, names="value")
            display(widgets.VBox([widgets.HBox([dim_dd, top_n]), out]))
            render()
            """
        ),
    ]
    write_notebook(DOSSIER_DIR / "minute_00_universe_quality_overview_v0_1.ipynb", cells)


def build_01_model() -> None:
    cells = [
        md(
            """
            # Minute 01 - Core Quality Model `v0_1`

            Este notebook crea el manifest moderno `core_quality` para `ohlcv_1m_raw`.

            Regla institucional:

            ```text
            core_quality_state gobierna la validez OHLCV raw.
            vw_quality_state gobierna solo consumos que usan vw.
            ```
            """
        ),
        code(COMMON_SETUP),
        code(
            """
            raw = load_raw_closeout()
            manifest = classify_core_quality(raw)
            save_core_manifest(manifest)
            display(Markdown("## Manifest generado"))
            display(pd.read_csv(CORE_ROOT / "minute_core_quality_summary_v0_1.csv"))
            display(pd.read_csv(CORE_ROOT / "minute_core_quality_family_counts_v0_1.csv").head(80))
            display(Markdown(f"`{CORE_ROOT / 'minute_core_quality_manifest_v0_1.parquet'}`"))
            """
        ),
        code(
            """
            display(Markdown("## Matriz core vs vw"))
            matrix = pd.crosstab(manifest["core_quality_state"], manifest["vw_quality_state"])
            display(matrix)
            plt.figure(figsize=(8, 5))
            sns.heatmap(matrix, annot=True, fmt=".0f", cmap="YlOrRd")
            plt.title("Core quality x VW quality")
            plt.ylabel("core_quality_state")
            plt.xlabel("vw_quality_state")
            plt.show()
            """
        ),
        code(
            """
            display(Markdown("## Widget de auditoria del modelo"))
            core_dd = widgets.Dropdown(description="core", options=["ALL"] + sorted(manifest["core_quality_state"].astype(str).unique()), value="ALL")
            vw_dd = widgets.Dropdown(description="vw", options=["ALL"] + sorted(manifest["vw_quality_state"].astype(str).unique()), value="ALL")
            family_dd = widgets.Dropdown(description="family", layout=widgets.Layout(width="520px"))
            out = widgets.Output()

            def refresh_family(*_):
                sub = filtered_options(manifest, {"core_quality_state": core_dd.value, "vw_quality_state": vw_dd.value})
                opts = ["ALL"] + sorted(sub["core_issue_family"].astype(str).unique().tolist())
                family_dd.options = opts
                if family_dd.value not in opts:
                    family_dd.value = "ALL"

            def render(*_):
                with out:
                    clear_output(wait=True)
                    sub = filtered_options(manifest, {
                        "core_quality_state": core_dd.value,
                        "vw_quality_state": vw_dd.value,
                        "core_issue_family": family_dd.value,
                    })
                    display(pd.DataFrame([{"rows": len(sub), "tickers": sub["ticker"].nunique()}]))
                    display(sub[["ticker","year","month","core_quality_state","vw_quality_state","combined_quality_state","core_issue_family","vw_issue_family","allowed_consumption"]].head(30))

            core_dd.observe(refresh_family, names="value")
            vw_dd.observe(refresh_family, names="value")
            core_dd.observe(render, names="value")
            vw_dd.observe(render, names="value")
            family_dd.observe(render, names="value")
            refresh_family()
            display(widgets.VBox([widgets.HBox([core_dd, vw_dd]), family_dd, out]))
            render()
            """
        ),
    ]
    write_notebook(DOSSIER_DIR / "minute_01_core_quality_model_v0_1.ipynb", cells)


def build_02_population() -> None:
    cells = [
        md(
            """
            # Minute 02 - Core Quality Population Readout `v0_1`

            Lectura poblacional moderna. Este notebook va de lo general a familias de problema,
            separando deuda core de deuda `vw`.
            """
        ),
        code(COMMON_SETUP),
        code(
            """
            df = load_core_manifest()
            display(Markdown("## Manifest activo"))
            display(pd.read_csv(CORE_ROOT / "minute_core_quality_summary_v0_1.csv"))
            """
        ),
        code(
            """
            cols = ["m.rows_after_parse", "m.active_days", "m.active_minutes", "m.coverage_ratio_vs_active_days_est", "m.max_gap_days", "m.vw_outside_range_rows", "vw_ratio_pct"]
            fig, axes = plt.subplots(2, 4, figsize=(18, 9), constrained_layout=True)
            axes = axes.ravel()
            for ax, col in zip(axes, cols):
                for state, color in [("good", "#2f9e44"), ("review", "#f08c00"), ("bad", "#e03131")]:
                    vals = pd.to_numeric(df.loc[df["core_quality_state"].eq(state), col], errors="coerce").dropna()
                    if len(vals):
                        ax.hist(vals.clip(upper=vals.quantile(0.99)), bins=35, alpha=0.45, label=state, color=color)
                ax.set_title(col)
                ax.legend()
            axes[-1].axis("off")
            plt.show()
            """
        ),
        code(
            """
            display(Markdown("## Familias core"))
            fam = df["core_issue_family"].astype(str).value_counts().rename_axis("core_issue_family").reset_index(name="count")
            fam["pct"] = 100.0 * fam["count"] / len(df)
            display(fam.head(50))
            plt.figure(figsize=(12, 7))
            sns.barplot(data=fam.head(25), y="core_issue_family", x="count", color="#4c78a8")
            plt.title("Top core issue families")
            plt.tight_layout()
            plt.show()
            """
        ),
        code(
            """
            display(Markdown("## Widget poblacional"))
            core_dd = widgets.Dropdown(description="core", options=["ALL"] + sorted(df["core_quality_state"].astype(str).unique()), value="ALL")
            vw_dd = widgets.Dropdown(description="vw", options=["ALL"] + sorted(df["vw_quality_state"].astype(str).unique()), value="ALL")
            comb_dd = widgets.Dropdown(description="combined", options=["ALL"] + sorted(df["combined_quality_state"].astype(str).unique()), value="ALL", layout=widgets.Layout(width="280px"))
            family_dd = widgets.Dropdown(description="family", layout=widgets.Layout(width="520px"))
            out = widgets.Output()

            def refresh_family(*_):
                sub = filtered_options(df, {"core_quality_state": core_dd.value, "vw_quality_state": vw_dd.value, "combined_quality_state": comb_dd.value})
                opts = ["ALL"] + sorted(sub["core_issue_family"].astype(str).unique().tolist())
                family_dd.options = opts
                if family_dd.value not in opts:
                    family_dd.value = "ALL"

            def render(*_):
                with out:
                    clear_output(wait=True)
                    sub = filtered_options(df, {
                        "core_quality_state": core_dd.value,
                        "vw_quality_state": vw_dd.value,
                        "combined_quality_state": comb_dd.value,
                        "core_issue_family": family_dd.value,
                    })
                    display(pd.DataFrame([{"rows": len(sub), "tickers": sub["ticker"].nunique(), "years": f"{int(sub['year'].min()) if len(sub) else 'NA'}-{int(sub['year'].max()) if len(sub) else 'NA'}"}]))
                    display(sub.groupby(["year", "core_quality_state"]).size().reset_index(name="rows").tail(30))
                    if len(sub):
                        yearly = sub.groupby(["year", "core_quality_state"]).size().reset_index(name="rows")
                        plt.figure(figsize=(12, 4))
                        sns.lineplot(data=yearly, x="year", y="rows", hue="core_quality_state", marker="o")
                        plt.title("Filtered yearly core quality")
                        plt.tight_layout()
                        plt.show()

            for w in [core_dd, vw_dd, comb_dd]:
                w.observe(refresh_family, names="value")
                w.observe(render, names="value")
            family_dd.observe(render, names="value")
            refresh_family()
            display(widgets.VBox([widgets.HBox([core_dd, vw_dd, comb_dd]), family_dd, out]))
            render()
            """
        ),
    ]
    write_notebook(DOSSIER_DIR / "minute_02_core_quality_population_readout_v0_1.ipynb", cells)


def build_03_casepack() -> None:
    cells = [
        md(
            """
            # Minute 03 - Casepack Builder `v0_1`

            Este notebook selecciona casos estratificados y permite exportar paneles visuales modernos.

            La salida esperada vive en:

            ```text
            inspection_dossiers/minute/evidence_assets/core_quality/casepacks/
            ```
            """
        ),
        code(COMMON_SETUP),
        code(
            """
            df = load_core_manifest()
            CASEPACK_ROOT = CORE_ROOT / "casepacks"
            CASEPACK_ROOT.mkdir(parents=True, exist_ok=True)

            def slug(s: str) -> str:
                return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(s)).strip("_")

            def export_case(row: pd.Series, bucket: str = "selected") -> Path:
                case_dir = CASEPACK_ROOT / slug(bucket) / f"{row['ticker']}_{int(row['year'])}_{int(row['month']):02d}"
                case_dir.mkdir(parents=True, exist_ok=True)
                fig, axes = plt.subplots(2, 2, figsize=(15, 9), constrained_layout=True)
                fig.suptitle(f"{row.get('ticker')} {int(row.get('year'))}-{int(row.get('month')):02d} | {row.get('combined_quality_state')}", fontsize=14)
                axes[0, 0].bar(["o_min", "l_min", "c_max", "h_max"], [row.get("m.o_min", np.nan), row.get("m.l_min", np.nan), row.get("m.c_max", np.nan), row.get("m.h_max", np.nan)], color=["#4c78a8", "#72b7b2", "#f58518", "#e45756"])
                axes[0, 0].set_title("00 month price envelope")
                axes[0, 1].bar(["active_days", "active_minutes", "coverage", "max_gap"], [row.get("m.active_days", np.nan), row.get("m.active_minutes", np.nan), row.get("m.coverage_ratio_vs_active_days_est", np.nan), row.get("m.max_gap_days", np.nan)], color=["#54a24b", "#4c78a8", "#b279a2", "#e45756"])
                axes[0, 1].set_title("01 density and gaps")
                axes[1, 0].bar(["dup_ts", "date_mismatch", "outside_month", "ohlc_invalid", "volume_invalid"], [row.get("m.duplicate_ts_utc_rows", 0), row.get("m.ts_utc_date_mismatch_rows", 0), row.get("m.dates_outside_partition_month", 0), row.get("m.negative_or_zero_ohlc_rows", 0) + row.get("m.high_low_inversion_rows", 0), row.get("m.negative_volume_rows", 0)], color="#e03131")
                axes[1, 0].set_title("02 core diagnostics")
                axes[1, 0].tick_params(axis="x", rotation=20)
                axes[1, 1].axis("off")
                text = "\\n".join([
                    f"core={row.get('core_quality_state')}",
                    f"vw={row.get('vw_quality_state')}",
                    f"combined={row.get('combined_quality_state')}",
                    f"core_family={row.get('core_issue_family')}",
                    f"vw_family={row.get('vw_issue_family')}",
                    f"consumption={row.get('allowed_consumption')}",
                    f"operational={row.get('operational_decision')}",
                ])
                axes[1, 1].text(0.01, 0.98, text, va="top", ha="left", family="monospace", fontsize=10)
                axes[1, 1].set_title("03 summary card")
                fig_path = case_dir / "00_core_quality_case_panel.png"
                fig.savefig(fig_path, dpi=160, bbox_inches="tight")
                plt.close(fig)
                note = f'''# Minute Case Note - {row.get("ticker")} {int(row.get("year"))}-{int(row.get("month")):02d}

## Decision

- core_quality_state: `{row.get("core_quality_state")}`
- vw_quality_state: `{row.get("vw_quality_state")}`
- combined_quality_state: `{row.get("combined_quality_state")}`
- allowed_consumption: `{row.get("allowed_consumption")}`

## Families

- core_issue_family: `{row.get("core_issue_family")}`
- vw_issue_family: `{row.get("vw_issue_family")}`
- operational_decision: `{row.get("operational_decision")}`

## Inspector Reading

This case separates OHLCV core quality from VW quality. The image shows price envelope,
coverage/density, core diagnostics, and the institutional decision card.

![case panel](00_core_quality_case_panel.png)
'''
                (case_dir / "case_note.md").write_text(note, encoding="utf-8")
                return case_dir

            display(Markdown("Loaded manifest"))
            display(df[["ticker","year","month","core_quality_state","vw_quality_state","combined_quality_state","core_issue_family","vw_issue_family","allowed_consumption"]].head())
            """
        ),
        code(
            """
            display(Markdown("## Widget selector y exportador de casepacks"))
            core_dd = widgets.Dropdown(description="core", options=["ALL"] + sorted(df["core_quality_state"].astype(str).unique()), value="ALL")
            vw_dd = widgets.Dropdown(description="vw", options=["ALL"] + sorted(df["vw_quality_state"].astype(str).unique()), value="ALL")
            family_dd = widgets.Dropdown(description="family", layout=widgets.Layout(width="520px"))
            ticker_dd = widgets.Dropdown(description="ticker", layout=widgets.Layout(width="220px"))
            ym_dd = widgets.Dropdown(description="year-month", layout=widgets.Layout(width="260px"))
            export_btn = widgets.Button(description="Export case", button_style="primary")
            out = widgets.Output()

            def refresh_family(*_):
                sub = filtered_options(df, {"core_quality_state": core_dd.value, "vw_quality_state": vw_dd.value})
                opts = ["ALL"] + sorted(sub["core_issue_family"].astype(str).unique().tolist())
                family_dd.options = opts
                if family_dd.value not in opts:
                    family_dd.value = "ALL"
                refresh_ticker()

            def refresh_ticker(*_):
                sub = filtered_options(df, {"core_quality_state": core_dd.value, "vw_quality_state": vw_dd.value, "core_issue_family": family_dd.value})
                opts = ["ALL"] + sorted(sub["ticker"].astype(str).unique().tolist())
                ticker_dd.options = opts
                if ticker_dd.value not in opts:
                    ticker_dd.value = opts[0] if opts else None
                refresh_ym()

            def refresh_ym(*_):
                sub = filtered_options(df, {"core_quality_state": core_dd.value, "vw_quality_state": vw_dd.value, "core_issue_family": family_dd.value, "ticker": ticker_dd.value})
                opts = [(f"{r.ticker} {int(r.year)}-{int(r.month):02d} | {r.combined_quality_state}", i) for i, r in sub.head(5000).iterrows()]
                ym_dd.options = opts
                ym_dd.value = opts[0][1] if opts else None

            def selected_row():
                if ym_dd.value is None:
                    return None
                return df.loc[ym_dd.value]

            def render(*_):
                with out:
                    clear_output(wait=True)
                    row = selected_row()
                    if row is None:
                        display(Markdown("No selected case."))
                        return
                    display_case_summary(row)
                    plot_case_panel(row)

            def do_export(_):
                with out:
                    row = selected_row()
                    if row is None:
                        return
                    bucket = row.get("combined_quality_state", "selected")
                    case_dir = export_case(row, bucket=bucket)
                    display(Markdown(f"Exported: `{case_dir}`"))

            for w in [core_dd, vw_dd]:
                w.observe(refresh_family, names="value")
            family_dd.observe(refresh_ticker, names="value")
            ticker_dd.observe(refresh_ym, names="value")
            ym_dd.observe(render, names="value")
            export_btn.on_click(do_export)
            refresh_family()
            display(widgets.VBox([widgets.HBox([core_dd, vw_dd]), family_dd, widgets.HBox([ticker_dd, ym_dd, export_btn]), out]))
            render()
            """
        ),
    ]
    write_notebook(DOSSIER_DIR / "minute_03_casepack_builder_v0_1.ipynb", cells)


def build_04_inspector() -> None:
    cells = [
        md(
            """
            # Minute 04 - Ticker Month Inspector `v0_1`

            Notebook interactivo principal para inspeccion humana. Permite seleccionar problema,
            ticker y mes sin editar codigo.
            """
        ),
        code(COMMON_SETUP),
        code(
            """
            df = load_core_manifest()
            display(Markdown("## Selector interactivo"))
            """
        ),
        code(
            """
            core_dd = widgets.Dropdown(description="core", options=["ALL"] + sorted(df["core_quality_state"].astype(str).unique()), value="ALL")
            vw_dd = widgets.Dropdown(description="vw", options=["ALL"] + sorted(df["vw_quality_state"].astype(str).unique()), value="ALL")
            combined_dd = widgets.Dropdown(description="combined", options=["ALL"] + sorted(df["combined_quality_state"].astype(str).unique()), value="ALL", layout=widgets.Layout(width="280px"))
            core_family_dd = widgets.Dropdown(description="core family", layout=widgets.Layout(width="560px"))
            vw_family_dd = widgets.Dropdown(description="vw family", layout=widgets.Layout(width="360px"))
            ticker_dd = widgets.Dropdown(description="ticker", layout=widgets.Layout(width="240px"))
            ym_dd = widgets.Dropdown(description="case", layout=widgets.Layout(width="520px"))
            out = widgets.Output()

            def sub_base():
                return filtered_options(df, {
                    "core_quality_state": core_dd.value,
                    "vw_quality_state": vw_dd.value,
                    "combined_quality_state": combined_dd.value,
                    "core_issue_family": core_family_dd.value,
                    "vw_issue_family": vw_family_dd.value,
                    "ticker": ticker_dd.value,
                })

            def refresh_families(*_):
                sub = filtered_options(df, {"core_quality_state": core_dd.value, "vw_quality_state": vw_dd.value, "combined_quality_state": combined_dd.value})
                c_opts = ["ALL"] + sorted(sub["core_issue_family"].astype(str).unique().tolist())
                v_opts = ["ALL"] + sorted(sub["vw_issue_family"].astype(str).unique().tolist())
                core_family_dd.options = c_opts
                vw_family_dd.options = v_opts
                if core_family_dd.value not in c_opts:
                    core_family_dd.value = "ALL"
                if vw_family_dd.value not in v_opts:
                    vw_family_dd.value = "ALL"
                refresh_tickers()

            def refresh_tickers(*_):
                sub = filtered_options(df, {
                    "core_quality_state": core_dd.value,
                    "vw_quality_state": vw_dd.value,
                    "combined_quality_state": combined_dd.value,
                    "core_issue_family": core_family_dd.value,
                    "vw_issue_family": vw_family_dd.value,
                })
                opts = ["ALL"] + sorted(sub["ticker"].astype(str).unique().tolist())
                ticker_dd.options = opts
                if ticker_dd.value not in opts:
                    ticker_dd.value = opts[0] if opts else None
                refresh_cases()

            def refresh_cases(*_):
                sub = sub_base()
                opts = [(f"{r.ticker} | {int(r.year)}-{int(r.month):02d} | {r.combined_quality_state} | {r.core_issue_family}", i) for i, r in sub.head(10000).iterrows()]
                ym_dd.options = opts
                ym_dd.value = opts[0][1] if opts else None

            def render(*_):
                with out:
                    clear_output(wait=True)
                    if ym_dd.value is None:
                        display(Markdown("No case selected."))
                        return
                    row = df.loc[ym_dd.value]
                    display_case_summary(row)
                    plot_case_panel(row)
                    cols = [
                        "m.rows_after_parse","m.active_days","m.active_minutes","m.business_days_est",
                        "m.coverage_ratio_vs_active_days_est","m.max_gap_days","m.duplicate_ts_utc_rows",
                        "m.ts_utc_date_mismatch_rows","m.dates_outside_partition_month",
                        "m.negative_or_zero_ohlc_rows","m.high_low_inversion_rows","m.negative_volume_rows",
                        "m.vw_outside_range_rows","vw_ratio_pct","vw_per_active_day"
                    ]
                    display(pd.DataFrame([row[[c for c in cols if c in row.index]].to_dict()]))

            for w in [core_dd, vw_dd, combined_dd]:
                w.observe(refresh_families, names="value")
            for w in [core_family_dd, vw_family_dd]:
                w.observe(refresh_tickers, names="value")
            ticker_dd.observe(refresh_cases, names="value")
            ym_dd.observe(render, names="value")
            refresh_families()
            display(widgets.VBox([
                widgets.HBox([core_dd, vw_dd, combined_dd]),
                widgets.HBox([core_family_dd, vw_family_dd]),
                widgets.HBox([ticker_dd, ym_dd]),
                out,
            ]))
            render()
            """
        ),
    ]
    write_notebook(DOSSIER_DIR / "minute_04_ticker_month_inspector_v0_1.ipynb", cells)


def build_05_final() -> None:
    cells = [
        md(
            """
            # Minute 05 - Final Readout `v0_1`

            Cierre moderno de lectura `minute`.

            Integra:

            - auditoria historica `01_research`;
            - closeout `<1B>`;
            - modelo core/vw separado;
            - notebooks interactivos;
            - consumo permitido.
            """
        ),
        code(COMMON_SETUP),
        code(
            """
            df = load_core_manifest()
            summary = pd.read_csv(CORE_ROOT / "minute_core_quality_summary_v0_1.csv")
            families = pd.read_csv(CORE_ROOT / "minute_core_quality_family_counts_v0_1.csv")
            display(Markdown("## Resumen core"))
            display(summary)
            display(Markdown("## Familias principales"))
            display(families.head(80))
            """
        ),
        code(
            """
            matrix = pd.crosstab(df["core_quality_state"], df["vw_quality_state"])
            display(Markdown("## Veredicto cuantitativo"))
            display(matrix)
            plt.figure(figsize=(8, 5))
            sns.heatmap(matrix, annot=True, fmt=".0f", cmap="YlGnBu")
            plt.title("Final matrix: core quality vs vw quality")
            plt.show()
            """
        ),
        md(
            """
            ## Veredicto institucional

            `ohlcv_1m_raw` debe leerse como una capa raw entendida y gobernada, no como capa
            productiva limpia sin flags.

            La mejora moderna es separar:

            - calidad core OHLCV;
            - calidad `vw`;
            - consumo permitido por combinacion.

            La regla final es:

            ```text
            core_bad invalida consumo productivo aunque vw parezca correcto.
            core_good + vw_bad permite OHLCV sin vw, pero prohibe features dependientes de vw.
            core_review exige flags o sensitivity runs.
            ```
            """
        ),
    ]
    write_notebook(DOSSIER_DIR / "minute_05_final_readout_v0_1.ipynb", cells)


def build_all() -> None:
    build_00_universe()
    build_01_model()
    build_02_population()
    build_03_casepack()
    build_04_inspector()
    build_05_final()


if __name__ == "__main__":
    build_all()
