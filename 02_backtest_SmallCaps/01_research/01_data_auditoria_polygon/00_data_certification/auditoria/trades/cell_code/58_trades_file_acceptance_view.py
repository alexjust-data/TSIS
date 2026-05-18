from __future__ import annotations

import json
from pathlib import Path
import ast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display


RUN_DIR_CD = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged")
CACHE_DIR = RUN_DIR_CD / "root_cause_exports" / "file_acceptance_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

TABLE_ROWS_DEFAULT = 20
TABLE_ROWS = {}
PLOT_RC = {
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
}


def get_table_rows(name: str, default: int | None = None) -> int:
    if default is None:
        default = TABLE_ROWS_DEFAULT
    return int(TABLE_ROWS.get(name, default))


def display_table(df: pd.DataFrame, name: str, sort_by: list[str] | None = None, ascending=False, default_rows: int | None = None):
    if df is None or df.empty:
        display(df)
        return
    x = df.copy()
    if sort_by:
        x = x.sort_values(sort_by, ascending=ascending)
    display(x.head(get_table_rows(name, default_rows)))


def _load_parquet(name: str) -> pd.DataFrame:
    p = CACHE_DIR / f"{name}.parquet"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_parquet(p)


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_all_artifacts() -> dict[str, pd.DataFrame]:
    keys = [
        "layer1_integrity_summary",
        "layer1_integrity_examples",
        "sample_index",
        "raw_file_metrics",
        "condition_combo_summary",
        "condition_code_summary",
        "layer2_eligibility_summary",
        "layer2_session_profile",
        "layer2_session_mismatch",
        "layer3_tape_quality_summary",
        "layer4_reference_consistency_summary",
        "layer5_severity_real_summary",
        "layer6_policy_summary",
        "layer6_policy_examples",
    ]
    return {k: _load_parquet(k) for k in keys}


def show_manifest(manifest: dict) -> None:
    if not manifest:
        display(Markdown("**manifest** no encontrado. Ejecuta primero el builder offline."))
        return
    display(Markdown(
        "  \n".join([
            f"**files_total:** {manifest.get('files_total', 'n/a'):,}",
            f"**sample_files:** {manifest.get('sample_files', 'n/a'):,}",
            f"**current parquet:** `{manifest.get('current_parquet', 'n/a')}`",
            f"**cache dir:** `{manifest.get('cache_dir', 'n/a')}`",
            f"**built_at_utc:** `{manifest.get('built_at_utc', 'n/a')}`",
            f"**batch_size:** `{manifest.get('batch_size', 'n/a')}`",
            f"**sample_per_stratum:** `{manifest.get('sample_per_stratum', 'n/a')}`",
        ])
    ))


def _metric_value(df: pd.DataFrame, metric: str) -> float:
    if df.empty:
        return np.nan
    s = df.loc[df["metric"] == metric, "value"]
    return float(s.iloc[0]) if not s.empty else np.nan


def _format_metric_label(metric: str) -> str:
    label = metric.replace("files_", "").replace("_", " ")
    return label


def _safe_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = ast.literal_eval(s)
        except Exception:
            return [s]
        return _safe_list(parsed)
    return [value]


def plot_layer1_integrity(summary: pd.DataFrame, max_metrics: int | None = None) -> None:
    if summary.empty:
        return
    metric_df = summary.copy()
    metric_df["value"] = pd.to_numeric(metric_df["value"], errors="coerce").fillna(0)

    outcomes = metric_df[metric_df["metric"].isin(["pass_files", "soft_fail_files", "hard_fail_files"])].copy()
    if not outcomes.empty:
        order = ["pass_files", "soft_fail_files", "hard_fail_files"]
        outcomes["metric"] = pd.Categorical(outcomes["metric"], categories=order, ordered=True)
        outcomes = outcomes.sort_values("metric")

    defects = metric_df[metric_df["metric"].str.startswith("files_")].copy()
    defects = defects[defects["metric"] != "files_total"].sort_values("value", ascending=False)
    if max_metrics is not None:
        defects = defects.head(int(max_metrics))

    with plt.rc_context(PLOT_RC):
        if not outcomes.empty:
            fig_height = max(7.2, 0.65 * (len(defects) + len(outcomes)) + 2.2)
            fig, axes = plt.subplots(2, 1, figsize=(10.5, fig_height), gridspec_kw={"height_ratios": [1.0, 1.35]})
            ax0, ax1 = axes
            total = max(float(_metric_value(metric_df, "files_total")), 1.0)
            colors = {
                "pass_files": "#4C72B0",
                "soft_fail_files": "#DD8452",
                "hard_fail_files": "#C44E52",
            }
            y0 = np.arange(len(outcomes))
            bars0 = ax0.barh(y0, outcomes["value"], color=[colors.get(m, "#999999") for m in outcomes["metric"]], height=0.42)
            ax0.set_yticks(y0)
            ax0.set_yticklabels([_format_metric_label(v) for v in outcomes["metric"]])
            ax0.set_title("Capa 1 | Resultado agregado")
            ax0.set_xlabel("files")
            ax0.grid(axis="x", alpha=0.2)
            ax0.invert_yaxis()
            for bar, metric, value in zip(bars0, outcomes["metric"], outcomes["value"]):
                pct = 100.0 * float(value) / total
                ax0.text(value, bar.get_y() + bar.get_height() / 2, f" {int(value):,} | {pct:.2f}%", ha="left", va="center", fontsize=8)
        else:
            fig_height = max(4.8, 0.55 * len(defects) + 1.6)
            fig, ax1 = plt.subplots(figsize=(9, fig_height))

        if defects.empty:
            ax1.text(0.5, 0.5, "Sin metricas de defecto `files_*` para graficar.", ha="center", va="center", transform=ax1.transAxes)
            ax1.set_axis_off()
        else:
            y1 = np.arange(len(defects))
            bars1 = ax1.barh(y1, defects["value"], height=0.38, color=["#C44E52" if float(v) > 0 else "#D9D9D9" for v in defects["value"]])
            ax1.set_title("Capa 1 | Defectos fisicos observados")
            ax1.set_xlabel("files")
            ax1.set_ylabel("metric")
            ax1.set_yticks(y1)
            ax1.set_yticklabels([_format_metric_label(v) for v in defects["metric"]])
            ax1.grid(axis="x", alpha=0.2)
            ax1.invert_yaxis()
            xmax = max(float(defects["value"].max()), 1.0)
            ax1.set_xlim(0, xmax * 1.12)
            for bar, value in zip(bars1, defects["value"]):
                ax1.text(value, bar.get_y() + bar.get_height() / 2, f" {int(value):,}", ha="left", va="center", fontsize=8)

        fig.suptitle("Capa 1 | Integridad del file", y=0.995, fontsize=13)
        plt.tight_layout()
        plt.show()



def show_layer1_file_example(layer1_examples: pd.DataFrame, example_idx: int = 0, n_rows: int = 12) -> None:
    if layer1_examples is None or layer1_examples.empty:
        display(Markdown("No hay ejemplos de `layer1_integrity_examples` para previsualizar files."))
        return
    if example_idx < 0 or example_idx >= len(layer1_examples):
        display(Markdown(
            f"`example_idx={example_idx}` queda fuera de rango para `layer1_integrity_examples` con {len(layer1_examples)} filas."
        ))
        return
    example = layer1_examples.iloc[int(example_idx)]
    file_path = Path(str(example["file"]))
    if not file_path.exists():
        display(Markdown(f"No se encuentra el file de ejemplo: `{file_path}`"))
        return
    try:
        preview = pd.read_parquet(file_path).head(n_rows)
    except Exception as exc:
        display(Markdown(f"No se pudo leer el file de ejemplo `{file_path}`. Error: `{exc}`"))
        return
    display(Markdown(
        "Ejemplo real del contenido del file que se está auditando en la capa 1. "
        "Esto permite ver el grano físico antes de resumir métricas."
    ))
    display(Markdown(
        f"**file:** `{file_path}`  \n"
        f"**ticker:** `{example.get('ticker', 'n/a')}`  \n"
        f"**date:** `{example.get('date', 'n/a')}`  \n"
        f"**severity en muestra:** `{example.get('severity', 'n/a')}`"
    ))
    display(preview)


def explain_layer1_metrics(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "No hay métricas de capa 1 disponibles."
    lines = [
        "`files_total`: número total de files evaluados en la capa de integridad.",
        "`files_missing_required_cols`: files a los que les faltan columnas obligatorias del schema esperado.",
        "`files_dtype_mismatch`: files donde el tipo de una o más columnas no coincide con el contrato esperado.",
        "`files_negative_price`: files con al menos un trade con `price < 0`; eso sí es físicamente inválido.",
        "`files_negative_size`: files con al menos un trade con `size < 0`; eso sí rompe la validez del volumen negociado.",
        "`files_timestamp_out_of_partition`: files con trades cuyo timestamp cae fuera del día de la partición.",
        "`files_empty_after_parse`: files que existen pero quedan vacíos tras parseo, limpieza o normalización.",
        "`files_zero_raw_rows`: files físicamente presentes pero sin filas útiles ya desde la lectura raw.",
    ]
    present = set(summary["metric"].tolist())
    filtered = [line for line in lines if line.split(":")[0].strip("`") in present]
    return (
        "En esta capa cada métrica responde a una pregunta física sobre el file.  \n"
        + "  \n".join(filtered)
    )


def plot_layer2_sessions(raw_metrics: pd.DataFrame) -> None:
    if raw_metrics.empty:
        return
    plot_df = raw_metrics[["regular_trade_pct", "prepost_trade_pct"]].copy()
    with plt.rc_context(PLOT_RC):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(plot_df["regular_trade_pct"].dropna(), bins=20, alpha=0.7, label="regular")
        ax.hist(plot_df["prepost_trade_pct"].dropna(), bins=20, alpha=0.7, label="pre/post")
        ax.set_title("Capa 2 | Mezcla de sesión en la muestra")
        ax.set_xlabel("pct de trades")
        ax.legend()
        plt.tight_layout()
        plt.show()


def build_layer2_descriptive_table(raw_metrics: pd.DataFrame, sample_index: pd.DataFrame) -> pd.DataFrame:
    off_session = pd.to_numeric(sample_index.get("m.off_session_trade_pct"), errors="coerce")
    one_m_found = pd.to_numeric(sample_index.get("m.ohlcv_1m_found"), errors="coerce")
    daily_found = pd.to_numeric(sample_index.get("m.ohlcv_daily_found"), errors="coerce")
    condition_nunique = pd.to_numeric(raw_metrics.get("condition_combo_nunique"), errors="coerce")
    rows = [
        {"metric": "sample_files", "value": len(sample_index)},
        {"metric": "files_with_off_session_pct_gt_0", "value": 100 * (off_session > 0).mean()},
        {"metric": "median_off_session_trade_pct", "value": off_session.median()},
        {"metric": "median_positive_off_session_trade_pct", "value": off_session[off_session > 0].median()},
        {"metric": "files_with_1m_reference_pct_sample_index", "value": 100 * one_m_found.mean()},
        {"metric": "files_with_daily_reference_pct_sample_index", "value": 100 * daily_found.mean()},
        {"metric": "median_condition_combo_nunique", "value": condition_nunique.median()},
        {"metric": "p95_condition_combo_nunique", "value": condition_nunique.quantile(0.95)},
    ]
    return pd.DataFrame(rows)


def plot_layer2_observability(raw_metrics: pd.DataFrame, sample_index: pd.DataFrame) -> None:
    if raw_metrics.empty or sample_index.empty:
        return
    off_session = pd.to_numeric(sample_index.get("m.off_session_trade_pct"), errors="coerce")
    combos = pd.to_numeric(raw_metrics.get("condition_combo_nunique"), errors="coerce")
    with plt.rc_context(PLOT_RC):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        axes[0].hist(off_session.dropna(), bins=20, color="#4C72B0")
        axes[0].set_title("Capa 2 | Off-session en muestra")
        axes[0].set_xlabel("pct trades off-session")
        axes[1].hist(combos.dropna(), bins=15, color="#55A868")
        axes[1].set_title("Capa 2 | Diversidad de conditions")
        axes[1].set_xlabel("n conditions_key distintas por file")
        plt.tight_layout()
        plt.show()


def plot_layer2_condition_combos(condition_combo_summary: pd.DataFrame, top_n: int = 12) -> None:
    if condition_combo_summary.empty:
        return
    plot_df = condition_combo_summary.head(int(top_n)).copy()
    with plt.rc_context(PLOT_RC):
        fig_height = max(4.5, 0.45 * len(plot_df) + 1.2)
        fig, ax = plt.subplots(figsize=(10, fig_height))
        y = np.arange(len(plot_df))
        bars = ax.barh(y, plot_df["trades"], color="#C44E52", height=0.42)
        ax.set_title("Top conditions_key en la muestra")
        ax.set_xlabel("trades")
        ax.set_yticks(y)
        ax.set_yticklabels(plot_df["conditions_key"])
        ax.grid(axis="x", alpha=0.2)
        ax.invert_yaxis()
        for bar, value in zip(bars, plot_df["trades"]):
            ax.text(value, bar.get_y() + bar.get_height() / 2, f" {int(value):,}", ha="left", va="center", fontsize=8)
        plt.tight_layout()
        plt.show()


def build_layer2_case_view(sample_index: pd.DataFrame, raw_metrics: pd.DataFrame) -> pd.DataFrame:
    if sample_index.empty:
        return pd.DataFrame()
    cols = [
        "file",
        "ticker",
        "date",
        "sample_stratum",
        "warns_list",
        "m.off_session_trade_pct",
        "m.ohlcv_1m_found",
        "m.ohlcv_daily_found",
    ]
    base = sample_index[cols].copy()
    base["warn_count"] = base["warns_list"].map(lambda x: len(_safe_list(x)))
    base["warns_joined"] = base["warns_list"].map(lambda x: ", ".join(map(str, _safe_list(x))))
    if not raw_metrics.empty:
        keep = [
            "file",
            "off_session_trade_pct",
            "odd_lot_trade_pct",
            "condition_combo_nunique",
            "outside_daily_regular_pct",
            "outside_daily_odd_lot_pct",
            "outside_daily_round_lot_pct",
            "outside_1m_regular_pct",
            "outside_1m_odd_lot_pct",
            "outside_1m_round_lot_pct",
            "acceptance_label",
        ]
        base = base.merge(raw_metrics[keep], on="file", how="left")
    return base.rename(
        columns={
            "m.off_session_trade_pct": "legacy_off_session_trade_pct",
            "m.ohlcv_1m_found": "has_1m_reference",
            "m.ohlcv_daily_found": "has_daily_reference",
        }
    )


def plot_layer3_quality(raw_metrics: pd.DataFrame) -> None:
    if raw_metrics.empty:
        return
    with plt.rc_context(PLOT_RC):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        axes[0].hist(raw_metrics["duplicate_exact_ratio_pct_raw"].dropna(), bins=20, color="#DD8452")
        axes[0].set_title("Duplicados exactos")
        axes[0].set_xlabel("pct")
        axes[1].hist(raw_metrics["max_trades_same_timestamp_raw"].dropna(), bins=20, color="#55A868")
        axes[1].set_title("Burst por timestamp")
        axes[1].set_xlabel("max trades mismo timestamp")
        plt.tight_layout()
        plt.show()


def plot_layer4_consistency(raw_metrics: pd.DataFrame) -> None:
    if raw_metrics.empty:
        return
    with plt.rc_context(PLOT_RC):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        axes[0].scatter(raw_metrics["outside_daily_regular_pct"], raw_metrics["outside_1m_regular_pct"], s=16, alpha=0.7)
        axes[0].set_title("Outside regular | daily vs 1m")
        axes[0].set_xlabel("outside daily regular pct")
        axes[0].set_ylabel("outside 1m regular pct")
        axes[1].hist(raw_metrics["outside_daily_volume_pct"].dropna(), bins=20, color="#C44E52")
        axes[1].set_title("Outside daily por volumen")
        axes[1].set_xlabel("pct volumen fuera")
        plt.tight_layout()
        plt.show()


def plot_layer5_severity(raw_metrics: pd.DataFrame) -> None:
    if raw_metrics.empty:
        return
    with plt.rc_context(PLOT_RC):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        axes[0].hist(raw_metrics["outside_minutes_pct_active"].dropna(), bins=20, color="#8172B2")
        axes[0].set_title("Persistencia temporal del outside")
        axes[0].set_xlabel("pct minutos activos afectados")
        axes[1].hist(raw_metrics["top_outside_minute_trade_share_pct"].dropna(), bins=20, color="#937860")
        axes[1].set_title("Concentración en el minuto dominante")
        axes[1].set_xlabel("pct trades outside en minuto top")
        plt.tight_layout()
        plt.show()


def plot_layer6_policy(policy: pd.DataFrame) -> None:
    if policy.empty:
        return
    with plt.rc_context(PLOT_RC):
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        palette = {
            "good": "#4C72B0",
            "review": "#DD8452",
            "review_microstructure": "#64B5CD",
            "review_1m_reference_alignment": "#55A868",
            "review_no_1m_reference": "#8CCB5E",
            "reference_scale_mismatch": "#8172B2",
            "bad_data": "#C44E52",
        }
        colors = [palette.get(x, "#999999") for x in policy["acceptance_label"]]
        ax.bar(policy["acceptance_label"], policy["files"], color=colors)
        ax.set_title("Capa 6 | Política de aceptación")
        ax.set_ylabel("files en muestra")
        plt.setp(ax.get_xticklabels(), rotation=18, ha="right")
        fig.subplots_adjust(bottom=0.28)
        plt.tight_layout()
        plt.show()


def summary_layer1(summary: pd.DataFrame) -> str:
    total = _metric_value(summary, "files_total")
    passed = _metric_value(summary, "pass_files")
    soft = _metric_value(summary, "soft_fail_files")
    hard = _metric_value(summary, "hard_fail_files")
    dtype = _metric_value(summary, "files_dtype_mismatch")
    negative_price = _metric_value(summary, "files_negative_price")
    negative_size = _metric_value(summary, "files_negative_size")
    ts_out = _metric_value(summary, "files_timestamp_out_of_partition")
    empty = _metric_value(summary, "files_empty_after_parse")
    zero = _metric_value(summary, "files_zero_raw_rows")
    explicit_physical = dtype + negative_price + negative_size + ts_out + empty + zero
    total_safe = max(float(total), 1.0)
    return (
        f"La primera capa separa el resultado agregado del universo y los defectos fisicos explicitos. Sobre {int(total):,} files, "
        f"`pass` representa {int(passed):,} ({100 * float(passed) / total_safe:.2f}%), `soft_fail` {int(soft):,} ({100 * float(soft) / total_safe:.2f}%) "
        f"y `hard_fail` {int(hard):,} ({100 * float(hard) / total_safe:.2f}%). "
        f"Dentro de los fallos fisicos explicitamente observados, el unico bloque no nulo material es `dtype_mismatch={int(dtype):,}` "
        f"({100 * float(dtype) / total_safe:.4f}% del universo), mientras que `negative_price`, `negative_size`, `timestamp_out_of_partition`, "
        f"`empty_after_parse` y `zero_raw_rows` permanecen en cero."
    )



def summary_layer2(summary: pd.DataFrame, sample_index: pd.DataFrame | None = None) -> str:
    reg = _metric_value(summary, "median_regular_trade_pct")
    pre = _metric_value(summary, "median_prepost_trade_pct")
    elig = _metric_value(summary, "median_baseline_eligible_trade_pct")
    parts = [
        f"La segunda capa debe perfilar primero qué prints hay antes de fijar política. En `raw_file_metrics` la mediana de trades en regular sale {reg:.2f}% y la de pre/post {pre:.2f}%. La elegibilidad basal mediana queda en {elig:.2f}%.",
    ]
    if sample_index is not None and not sample_index.empty:
        off_session = pd.to_numeric(sample_index.get("m.off_session_trade_pct"), errors="coerce")
        positive = off_session[off_session > 0]
        parts.append(
            f"Pero `sample_index` marca {int((off_session > 0).sum()):,} de {len(off_session):,} files con `off_session_trade_pct > 0`."
        )
        if not positive.empty:
            parts.append(
                f"La mediana entre esos casos positivos es {positive.median():.2f}%, así que la muestra sí contiene off-session material."
            )
        parts.append(
            "Conclusión: esta capa sirve para observar sesión, conditions y referencias, pero la semántica de sesión en `raw_file_metrics` todavía no basta para cerrar elegibilidad final."
        )
    return "  \n".join(parts)


def summary_layer3(summary: pd.DataFrame) -> str:
    dup = _metric_value(summary, "median_duplicate_exact_ratio_pct_raw")
    p95 = _metric_value(summary, "p95_duplicate_exact_ratio_pct_raw")
    burst = _metric_value(summary, "median_max_trades_same_timestamp_raw")
    return f"La tercera capa mide suciedad mecánica del tape. La mediana de duplicado exacto es {dup:.2f}% y el p95 sube a {p95:.2f}%. El burst mediano por timestamp es {burst:.2f}. Esto separa files limpios de files contaminados por repetición artificial."


def summary_layer4(summary: pd.DataFrame) -> str:
    d = _metric_value(summary, "median_outside_daily_regular_pct")
    m1 = _metric_value(summary, "median_outside_1m_regular_pct")
    vol = _metric_value(summary, "median_outside_daily_volume_pct")
    return f"La cuarta capa ya mide si el flujo elegible rompe de verdad contra referencias. La mediana de outside regular contra daily es {d:.2f}%, contra 1m es {m1:.2f}%, y el outside por volumen mediano es {vol:.2f}%. Aquí deja de importar un solo min/max y empieza a importar la masa real del desvío."


def summary_layer5(summary: pd.DataFrame) -> str:
    active = _metric_value(summary, "median_outside_minutes_pct_active")
    run = _metric_value(summary, "median_longest_outside_run_minutes")
    top = _metric_value(summary, "median_top_outside_minute_trade_share_pct")
    return f"La quinta capa distingue spike puntual frente a problema persistente. La mediana del outside afecta al {active:.2f}% de minutos activos, la racha máxima mediana es {run:.2f} minutos y el minuto dominante concentra {top:.2f}% de los trades outside."


def summary_layer6(policy: pd.DataFrame) -> str:
    if policy.empty:
        return "La sexta capa no tiene muestra todavía."
    parts = [f"{row.acceptance_label}={int(row.files)}" for row in policy.itertuples(index=False)]
    return "La sexta capa convierte métricas en decisión operativa separando `bad_data`, `reference_scale_mismatch` y los bloques de comparabilidad de referencia. El reparto actual de la muestra es: " + ", ".join(parts) + "."

