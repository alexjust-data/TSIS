from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SCRIPT_ROOT = Path(__file__).resolve().parent
STRATEGY_ROOT = SCRIPT_ROOT.parent

DEFAULT_TABLE = (
    STRATEGY_ROOT
    / "runs"
    / "das_scanner_appearance_20260628T114046Z"
    / "state_tables"
    / "das_candidate_state_table_experimental_v0_1.parquet"
)
DEFAULT_OUTPUT = DEFAULT_TABLE.with_name("das_candidate_state_table_experimental_v0_1_stats_report.md")


KEY_NUMERIC_COLUMNS = [
    "scanner__trigger_gap_pct_from_prior_close",
    "scanner__trigger_pct_from_premarket_open",
    "scanner__trigger_volume_today",
    "scanner__trigger_dollar_volume_today",
    "scanner__minutes_after_momentum_trigger",
    "frontside__momentum_trigger_gap_pct_from_prior_close",
    "frontside__momentum_trigger_pct_from_premarket_open",
    "frontside__first_push_pct_from_premarket_open",
    "frontside__first_push_pct_from_prior_close",
    "frontside__first_dip_depth_pct",
    "frontside__rebreak_minutes_after_first_push_high",
    "frontside__max_momentum_pct_from_premarket_open",
    "frontside__max_momentum_pct_from_prior_close",
    "outcome__max_extension_pct_after_scanner",
    "outcome__max_extension_pct_after_momentum_trigger",
]


def _fmt(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(_fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def _value_counts(df: pd.DataFrame, column: str, top: int = 20) -> pd.DataFrame:
    if column not in df.columns:
        return pd.DataFrame(columns=[column, "count", "pct"])
    vc = df[column].fillna("<NA>").value_counts(dropna=False).head(top)
    out = vc.rename_axis(column).reset_index(name="count")
    out["pct"] = out["count"] / len(df) * 100.0
    return out


def _numeric_summary(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            continue
        rows.append(
            {
                "metric": col,
                "count": int(s.count()),
                "mean": s.mean(),
                "p10": s.quantile(0.10),
                "p25": s.quantile(0.25),
                "median": s.median(),
                "p75": s.quantile(0.75),
                "p90": s.quantile(0.90),
                "max": s.max(),
            }
        )
    return pd.DataFrame(rows)


def _bucket_table(
    df: pd.DataFrame,
    column: str,
    bins: list[float],
    labels: list[str],
    bucket_name: str,
) -> pd.DataFrame:
    if column not in df.columns:
        return pd.DataFrame(columns=[bucket_name, "count", "pct"])
    values = pd.to_numeric(df[column], errors="coerce")
    bucket = pd.cut(values, bins=bins, labels=labels, include_lowest=True, right=False)
    out = bucket.value_counts(sort=False, dropna=False).rename_axis(bucket_name).reset_index(name="count")
    out["pct"] = out["count"] / len(df) * 100.0
    return out


def _top_examples(df: pd.DataFrame, sort_col: str, ascending: bool, n: int = 15) -> pd.DataFrame:
    if sort_col not in df.columns:
        return pd.DataFrame()
    cols = [
        "identity__tradingview_symbol",
        "identity__session_date",
        sort_col,
        "scanner__trigger_gap_pct_from_prior_close",
        "scanner__trigger_volume_today",
        "frontside__first_push_pct_from_premarket_open",
        "frontside__first_dip_depth_pct",
        "frontside__rebreak_type",
        "frontside__max_momentum_pct_from_premarket_open",
        "das__variant",
        "quality__state",
    ]
    cols = list(dict.fromkeys(c for c in cols if c in df.columns))
    return df.sort_values(sort_col, ascending=ascending)[cols].head(n)


def build_report(table_path: Path, output_path: Path) -> None:
    df = pd.read_parquet(table_path)
    lines: list[str] = []

    lines.extend(
        [
            "# DAS Experimental Statistics Report v0.1",
            "",
            f"Input table: `{table_path}`",
            f"Rows: `{len(df)}`",
            f"Columns: `{len(df.columns)}`",
            "",
            "## 1. Que datos se han estudiado",
            "",
            "Este reporte analiza la tabla experimental generada desde el run DAS:",
            "",
            "```text",
            str(table_path.parent.parent),
            "```",
            "",
            "La tabla no se ha construido desde el scanner general futuro. Por tanto, las estadisticas son:",
            "",
            "```text",
            "conditional_on_current_das_detector",
            "```",
            "",
            "No son todavia estadisticas poblacionales sobre todos los tickers in-play del mercado.",
            "",
        ]
    )

    unique_tickers = df["identity__ticker"].nunique() if "identity__ticker" in df.columns else None
    date_min = df["identity__session_date"].min() if "identity__session_date" in df.columns else ""
    date_max = df["identity__session_date"].max() if "identity__session_date" in df.columns else ""
    lines.extend(
        [
            "## 2. Cobertura",
            "",
            f"- candidatos: `{len(df)}`",
            f"- tickers unicos: `{unique_tickers}`",
            f"- primera fecha: `{date_min}`",
            f"- ultima fecha: `{date_max}`",
            "",
        ]
    )

    for title, column in [
        ("DAS state", "das__state"),
        ("DAS variant", "das__variant"),
        ("Quality state", "quality__state"),
        ("Rebreak type", "frontside__rebreak_type"),
        ("Exchange", "identity__primary_exchange"),
    ]:
        lines.extend([f"## 3. {title}", "", _markdown_table(_value_counts(df, column)), ""])

    lines.extend(
        [
            "## 4. Resumen numerico",
            "",
            _markdown_table(_numeric_summary(df, KEY_NUMERIC_COLUMNS)),
            "",
        ]
    )

    lines.extend(
        [
            "## 5. Buckets principales",
            "",
            "### 5.1. First push desde apertura premarket",
            "",
            _markdown_table(
                _bucket_table(
                    df,
                    "frontside__first_push_pct_from_premarket_open",
                    [-999, 20, 50, 100, 200, 500, 99999],
                    ["<20%", "20-50%", "50-100%", "100-200%", "200-500%", ">=500%"],
                    "first_push_bucket",
                )
            ),
            "",
            "### 5.2. Max momentum desde apertura premarket",
            "",
            _markdown_table(
                _bucket_table(
                    df,
                    "frontside__max_momentum_pct_from_premarket_open",
                    [-999, 20, 50, 100, 200, 500, 99999],
                    ["<20%", "20-50%", "50-100%", "100-200%", "200-500%", ">=500%"],
                    "max_momentum_bucket",
                )
            ),
            "",
            "### 5.3. Profundidad del primer dip",
            "",
            _markdown_table(
                _bucket_table(
                    df,
                    "frontside__first_dip_depth_pct",
                    [-999, 5, 10, 20, 35, 50, 99999],
                    ["<5%", "5-10%", "10-20%", "20-35%", "35-50%", ">=50%"],
                    "first_dip_depth_bucket",
                )
            ),
            "",
            "### 5.4. Retraso del scanner frente al momentum trigger",
            "",
            _markdown_table(
                _bucket_table(
                    df,
                    "scanner__minutes_after_momentum_trigger",
                    [-999, 0.0001, 5, 15, 30, 60, 120, 99999],
                    ["0m", "0-5m", "5-15m", "15-30m", "30-60m", "60-120m", ">=120m"],
                    "scanner_delay_bucket",
                )
            ),
            "",
        ]
    )

    if {
        "frontside__max_momentum_pct_from_premarket_open",
        "frontside__first_dip_depth_pct",
    }.issubset(df.columns):
        bucketed = df.assign(
            max_momentum_bucket=pd.cut(
                pd.to_numeric(df["frontside__max_momentum_pct_from_premarket_open"], errors="coerce"),
                bins=[-999, 20, 50, 100, 200, 500, 99999],
                labels=["<20%", "20-50%", "50-100%", "100-200%", "200-500%", ">=500%"],
                include_lowest=True,
                right=False,
            ),
            first_dip_bucket=pd.cut(
                pd.to_numeric(df["frontside__first_dip_depth_pct"], errors="coerce"),
                bins=[-999, 5, 10, 20, 35, 50, 99999],
                labels=["<5%", "5-10%", "10-20%", "20-35%", "35-50%", ">=50%"],
                include_lowest=True,
                right=False,
            ),
        )
        dip_count = pd.crosstab(bucketed["max_momentum_bucket"], bucketed["first_dip_bucket"], dropna=False)
        dip_count.index.name = "max_momentum_bucket"
        dip_pct = dip_count.div(dip_count.sum(axis=1).replace(0, pd.NA), axis=0) * 100.0
        dip_pct.index.name = "max_momentum_bucket"
        dip_summary = (
            bucketed.groupby("max_momentum_bucket", observed=False)["frontside__first_dip_depth_pct"]
            .agg(["count", "mean", "median"])
            .reset_index()
        )
        lines.extend(
            [
                "## 6. Profundidad del primer dip por bucket de max momentum",
                "",
                "Esta es la lectura correcta para comparar si los movimientos de `50-100%`, `100-200%` o `>=200%` toleran dips distintos.",
                "",
                "### 6.1. Porcentaje por fila",
                "",
                _markdown_table(dip_pct.reset_index().round(2)),
                "",
                "### 6.2. Conteo absoluto",
                "",
                _markdown_table(dip_count.reset_index()),
                "",
                "### 6.3. Media y mediana del dip",
                "",
                _markdown_table(dip_summary.round(2)),
                "",
            ]
        )

    if "das__variant" in df.columns and "frontside__first_dip_depth_pct" in df.columns:
        cross = (
            df.assign(
                first_dip_bucket=pd.cut(
                    pd.to_numeric(df["frontside__first_dip_depth_pct"], errors="coerce"),
                    bins=[-999, 5, 10, 20, 35, 50, 99999],
                    labels=["<5%", "5-10%", "10-20%", "20-35%", "35-50%", ">=50%"],
                    include_lowest=True,
                    right=False,
                )
            )
            .pivot_table(
                index="das__variant",
                columns="first_dip_bucket",
                values="identity__das_candidate_id",
                aggfunc="count",
                fill_value=0,
                observed=False,
            )
            .reset_index()
        )
        lines.extend(["## 7. Variante x profundidad del primer dip", "", _markdown_table(cross), ""])

    lines.extend(
        [
            "## 8. Top ejemplos por metrica",
            "",
            "### 8.1. Mayor max momentum",
            "",
            _markdown_table(
                _top_examples(df, "frontside__max_momentum_pct_from_premarket_open", False), 15
            ),
            "",
            "### 8.2. Mayor first push",
            "",
            _markdown_table(
                _top_examples(df, "frontside__first_push_pct_from_premarket_open", False), 15
            ),
            "",
            "### 8.3. Eips mas profundos",
            "",
            _markdown_table(_top_examples(df, "frontside__first_dip_depth_pct", False), 15),
            "",
            "### 8.4. Ccanner mas tardio",
            "",
            _markdown_table(_top_examples(df, "scanner__minutes_after_momentum_trigger", False), 15),
            "",
        ]
    )

    lines.extend(
        [
            "## 9. Lectura sobre falsos positivos",
            "",
            "Este run no permite medir una tasa real de falsos positivos del detector DAS.",
            "",
            "Motivo:",
            "",
            "```text",
            "candidate_events.parquet solo contiene candidatos emitidos por el detector actual.",
            "En este run, todos los candidatos emitidos tienen das__state = rebreak_confirmed.",
            "Los casos que no llegaron a rebreak, no rompieron estructura o nunca activaron DAS no estan en la tabla.",
            "```",
            "",
            "Por tanto, con esta tabla podemos medir:",
            "",
            "- variantes dentro de candidatos confirmados;",
            "- distribuciones de first push, max momentum, dip y rebreak;",
            "- posibles buenos/malos si anadimos labels humanos;",
            "- outcomes posteriores de los candidatos emitidos.",
            "",
            "Pero no podemos medir aun:",
            "",
            "- cuantos tickers in-play no generaron DAS;",
            "- cuantos scanner triggers fallaron antes del rebreak;",
            "- cuantos first push no tuvieron dip valido;",
            "- cuantos dips destruyeron estructura;",
            "- tasa poblacional de falsos positivos sobre todo el universo scanner.",
            "",
            "Para medir falsos positivos necesitamos una de estas dos cosas:",
            "",
            "1. `daily_scanner_candidates_table` como denominador general de todos los tickers in-play por timestamp.",
            "2. Un DAS detector mas amplio que emita tambien estados intermedios: scanner_only, first_push_detected, first_dip_detected, no_rebreak, failed_candidate.",
            "",
            "Tus carpetas de imagenes `BUENOS CORREGIDOS`, `MALOS` y `Archive` pueden servir para labels humanos, pero esos labels no sustituyen al denominador completo.",
            "",
            "## 10. Ciguiente paso recomendado",
            "",
            "1. Ingerir labels humanos de carpetas buenas/malas/archive y asociarlos a `candidate_id` cuando sea posible.",
            "2. Crear una version del detector que guarde candidatos antes del rebreak.",
            "3. Comparar estadisticas de confirmados vs rechazados.",
            "4. Cuando exista el scanner general, recalcular estadisticas con denominador poblacional.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build DAS experimental stats report.")
    parser.add_argument("--table", default=str(DEFAULT_TABLE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    build_report(Path(args.table), Path(args.output))
    print(f"wrote={args.output}")


if __name__ == "__main__":
    main()
