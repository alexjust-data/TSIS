from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

matplotlib.use("Agg")


RAW_ROOT = Path(r"D:\ohlcv_1m")
NORM_ROOT = Path(r"E:\TSIS\data\ohlcv_1m_split_normalized")
SPLITS_ROOT = Path(r"C:\TSIS_Data\data\additional\corporate_actions\splits")
MANIFEST_PATH = (
    PROJECT_ROOT
    / "01_foundations"
    / "dataset_registry"
    / "1m"
    / "ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv"
)
OUT_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "1m_split_normalized"
OUT_MD = OUT_DIR / "ohlcv_1m_split_normalized_pilot_readout_v0_1.md"
IMG_DIR = OUT_DIR / "images"


@dataclass(frozen=True)
class CaseMetrics:
    ticker: str
    year: int
    month: int
    role: str
    event_type: str
    event_date: str | None
    rows: int
    split_non1_rows: int
    split_non1_pct: float
    unique_factors: list[float]
    first_non1_date: str | None
    last_non1_date: str | None
    first_one_date: str | None
    last_date: str | None
    anchor_date: str | None


def _load_optional_parquet(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "_empty" in df.columns and len(df) and bool(df["_empty"].iloc[0]) is True:
        return pd.DataFrame()
    return df


def _split_file(ticker: str) -> Path | None:
    p = SPLITS_ROOT / f"ticker={ticker}" / f"splits_{ticker}.parquet"
    return p if p.exists() else None


def _raw_file(ticker: str, year: int, month: int) -> Path:
    return RAW_ROOT / f"ticker={ticker}" / f"year={year}" / f"month={month:02d}" / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"


def _norm_file(ticker: str, year: int, month: int) -> Path:
    return NORM_ROOT / f"ticker={ticker}" / f"year={year}" / f"month={month:02d}" / f"minute_aggs_{ticker}_{year}_{month:02d}_split_normalized.parquet"


def _load_splits(ticker: str) -> pd.DataFrame:
    df = _load_optional_parquet(_split_file(ticker))
    if df.empty:
        return df
    keep = [c for c in ["execution_date", "split_from", "split_to"] if c in df.columns]
    out = df[keep].copy()
    out["execution_date"] = pd.to_datetime(out["execution_date"], errors="coerce")
    out["split_from"] = pd.to_numeric(out["split_from"], errors="coerce")
    out["split_to"] = pd.to_numeric(out["split_to"], errors="coerce")
    out = out.loc[out["execution_date"].notna() & out["split_from"].gt(0) & out["split_to"].gt(0)].copy()
    out["split_ratio"] = out["split_to"] / out["split_from"]
    out = out.sort_values("execution_date").reset_index(drop=True)
    return out


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ts_utc"] = pd.to_datetime(out["ts_utc"], errors="coerce", utc=True)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for c in ["o", "h", "l", "c", "vw", "future_split_factor", "o_split_normalized", "c_split_normalized", "vw_split_normalized"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.sort_values("ts_utc").reset_index(drop=True)
    return out


def _find_anchor_date(norm_df: pd.DataFrame, splits: pd.DataFrame) -> pd.Timestamp | None:
    if norm_df.empty or splits.empty:
        return None
    min_date = pd.Timestamp(norm_df["date"].min()).normalize()
    max_date = pd.Timestamp(norm_df["date"].max()).normalize()
    future = splits.loc[splits["execution_date"].dt.normalize().gt(max_date), "execution_date"]
    if not future.empty:
        return pd.Timestamp(future.iloc[0]).normalize()
    current = splits.loc[
        splits["execution_date"].dt.normalize().ge(min_date) & splits["execution_date"].dt.normalize().le(max_date),
        "execution_date",
    ]
    if not current.empty:
        return pd.Timestamp(current.iloc[0]).normalize()
    return None


def _compute_case_metrics(row: pd.Series, norm_df: pd.DataFrame, splits: pd.DataFrame) -> CaseMetrics:
    factors = pd.to_numeric(norm_df["future_split_factor"], errors="coerce")
    non1_mask = factors.ne(1.0).fillna(False)
    unique_factors = sorted({float(x) for x in factors.dropna().unique().tolist()})
    non1_dates = pd.to_datetime(norm_df.loc[non1_mask, "date"], errors="coerce").dropna().dt.normalize().drop_duplicates().sort_values()
    one_dates = pd.to_datetime(norm_df.loc[~non1_mask, "date"], errors="coerce").dropna().dt.normalize().drop_duplicates().sort_values()
    anchor = _find_anchor_date(norm_df, splits)
    return CaseMetrics(
        ticker=str(row["ticker"]),
        year=int(row["year"]),
        month=int(row["month"]),
        role=str(row["role"]),
        event_type=str(row["event_type"]),
        event_date=None if pd.isna(row.get("event_date")) else str(row.get("event_date")),
        rows=int(len(norm_df)),
        split_non1_rows=int(non1_mask.sum()),
        split_non1_pct=float(100.0 * non1_mask.mean()) if len(norm_df) else 0.0,
        unique_factors=unique_factors,
        first_non1_date=None if non1_dates.empty else str(non1_dates.iloc[0].date()),
        last_non1_date=None if non1_dates.empty else str(non1_dates.iloc[-1].date()),
        first_one_date=None if one_dates.empty else str(one_dates.iloc[0].date()),
        last_date=None if norm_df.empty else str(pd.Timestamp(norm_df["date"].max()).date()),
        anchor_date=None if anchor is None else str(anchor.date()),
    )


def _event_window_dates(df: pd.DataFrame, anchor_date: str | None) -> set[pd.Timestamp]:
    if df.empty:
        return set()
    unique_dates = pd.Series(pd.to_datetime(df["date"], errors="coerce").dropna().dt.normalize().unique()).sort_values().reset_index(drop=True)
    if unique_dates.empty:
        return set()
    if anchor_date is None:
        idx = len(unique_dates) // 2
    else:
        anchor = pd.Timestamp(anchor_date).normalize()
        exact = unique_dates[unique_dates.eq(anchor)]
        if len(exact):
            idx = int(exact.index[0])
        else:
            idx = int((unique_dates - anchor).abs().argmin())
    lo = max(0, idx - 3)
    hi = min(len(unique_dates) - 1, idx + 3)
    return {pd.Timestamp(x).normalize() for x in unique_dates.iloc[lo : hi + 1].tolist()}


def _render_case_figure(row: pd.Series, raw_df: pd.DataFrame, norm_df: pd.DataFrame, metrics: CaseMetrics) -> plt.Figure:
    raw = _prep(raw_df)
    norm = _prep(norm_df)
    anchor = metrics.event_date or metrics.anchor_date
    event_window = _event_window_dates(norm, anchor)

    fig = plt.figure(figsize=(15, 11))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.1, 1.1, 0.7], hspace=0.28, wspace=0.18)

    ax_raw_full = fig.add_subplot(gs[0, 0])
    ax_norm_full = fig.add_subplot(gs[0, 1], sharex=ax_raw_full)
    ax_raw_zoom = fig.add_subplot(gs[1, 0])
    ax_norm_zoom = fig.add_subplot(gs[1, 1], sharex=ax_raw_zoom)
    ax_factor = fig.add_subplot(gs[2, :])

    x = raw["ts_utc"]
    ax_raw_full.plot(x, raw["c"], color="#6b7280", linewidth=0.9, alpha=0.9)
    ax_raw_full.set_title("Raw 1m close | mes completo")
    ax_raw_full.set_ylabel("precio raw")
    ax_raw_full.grid(alpha=0.2)

    ax_norm_full.plot(norm["ts_utc"], norm["c_split_normalized"], color="#2563eb", linewidth=0.9, alpha=0.95)
    ax_norm_full.set_title("Split-normalized 1m close | mes completo")
    ax_norm_full.set_ylabel("precio split_normalized")
    ax_norm_full.grid(alpha=0.2)

    if event_window:
        raw_zoom = raw.loc[pd.to_datetime(raw["date"]).dt.normalize().isin(event_window)].copy()
        norm_zoom = norm.loc[pd.to_datetime(norm["date"]).dt.normalize().isin(event_window)].copy()
    else:
        raw_zoom = raw.copy()
        norm_zoom = norm.copy()

    ax_raw_zoom.plot(raw_zoom["ts_utc"], raw_zoom["c"], color="#6b7280", linewidth=1.0)
    ax_raw_zoom.set_title("Raw 1m close | ventana del evento")
    ax_raw_zoom.set_ylabel("precio raw")
    ax_raw_zoom.grid(alpha=0.2)

    ax_norm_zoom.plot(norm_zoom["ts_utc"], norm_zoom["c_split_normalized"], color="#2563eb", linewidth=1.0)
    ax_norm_zoom.set_title("Split-normalized 1m close | ventana del evento")
    ax_norm_zoom.set_ylabel("precio split_normalized")
    ax_norm_zoom.grid(alpha=0.2)

    factor_by_date = (
        norm[["date", "future_split_factor"]]
        .dropna()
        .assign(date=lambda x: pd.to_datetime(x["date"]).dt.normalize())
        .drop_duplicates()
        .sort_values("date")
    )
    ax_factor.step(factor_by_date["date"], factor_by_date["future_split_factor"], where="post", color="#dc2626", linewidth=1.5)
    ax_factor.set_title("Future split factor por fecha")
    ax_factor.set_ylabel("factor")
    ax_factor.grid(alpha=0.2)

    if anchor is not None:
        anchor_ts = pd.Timestamp(anchor).tz_localize("UTC") if pd.Timestamp(anchor).tzinfo is None else pd.Timestamp(anchor)
        for ax in [ax_raw_full, ax_norm_full, ax_raw_zoom, ax_norm_zoom]:
            ax.axvline(anchor_ts, color="#ef4444", linestyle="--", linewidth=1.2, alpha=0.9)
        ax_factor.axvline(pd.Timestamp(anchor), color="#ef4444", linestyle="--", linewidth=1.2, alpha=0.9)

    for ax in [ax_raw_full, ax_norm_full, ax_raw_zoom, ax_norm_zoom]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        for label in ax.get_xticklabels():
            label.set_rotation(25)
            label.set_horizontalalignment("right")
    ax_factor.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    for label in ax_factor.get_xticklabels():
        label.set_rotation(25)
        label.set_horizontalalignment("right")

    sup = (
        f"{metrics.ticker} | {metrics.year}-{metrics.month:02d} | {metrics.role} | "
        f"event_type={metrics.event_type} | event_date={metrics.event_date or 'none'} | "
        f"split_non1_rows={metrics.split_non1_rows:,}/{metrics.rows:,} ({metrics.split_non1_pct:.2f}%)"
    )
    fig.suptitle(sup, fontsize=14, y=0.98)
    return fig


def _case_slug(row: pd.Series) -> str:
    return f"{row['ticker']}_{int(row['year'])}_{int(row['month']):02d}"


def _image_rel(row: pd.Series) -> str:
    return f"./images/{_case_slug(row)}.png"


def _case_narrative(metrics: CaseMetrics) -> tuple[list[str], list[str], list[str], list[str]]:
    que = [
        "Compara la misma barra `1m` observada en dos vistas: `raw` y `split_normalized`.",
        "Ensena el mes completo, una ventana focalizada alrededor del evento o ancla, y la trayectoria diaria del `future_split_factor`.",
    ]
    responde = [
        "Si la discontinuidad entre sesiones viene de un cambio mecanico de escala o de un movimiento economico real.",
        "Si el factor se aplica justo donde la definicion contractual dice que debe aplicarse.",
    ]
    lectura: list[str] = [
        f"`split_non1_rows = {metrics.split_non1_rows:,}/{metrics.rows:,}` (`{metrics.split_non1_pct:.2f}%`).",
        f"`unique_factors = {metrics.unique_factors}`.",
    ]
    conclusion: list[str] = []

    if metrics.role == "control" and metrics.anchor_date and metrics.split_non1_rows > 0:
        lectura.extend(
            [
                f"El mes es un control sin split interno, pero esta antes del split ancla `{metrics.anchor_date}`.",
                f"Por eso el tramo `{metrics.first_non1_date} -> {metrics.last_non1_date}` aparece reescalado aunque el evento no viva dentro del propio mes.",
            ]
        )
        conclusion.extend(
            [
                "Esto no contradice la semantica; la confirma.",
                "Demuestra que la capa no pregunta si el mes contiene un split, sino si la observacion es anterior a un split futuro relevante.",
            ]
        )
    elif metrics.role == "control" and metrics.split_non1_rows == 0:
        lectura.append("Todo el mes queda con `future_split_factor = 1`, lo que implica que no existe split futuro activo para esta ventana.")
        conclusion.extend(
            [
                "Este es el control neutro puro.",
                "Demuestra que la capa no deja residuos artificiales una vez superado el evento.",
            ]
        )
    elif metrics.split_non1_rows == 0 and metrics.event_date:
        lectura.extend(
            [
                f"El evento cae en `{metrics.event_date}` y dentro del `ticker-month` ya no queda tramo previo a reescalar.",
                "Por eso el resultado correcto es precisamente `0` filas con factor distinto de `1`.",
            ]
        )
        conclusion.extend(
            [
                "Este caso evita una falsa expectativa ingenua.",
                "No todo mes con split debe contener filas reescaladas; depende de donde cae el evento dentro de la ventana materializada.",
            ]
        )
    else:
        if metrics.event_date:
            lectura.extend(
                [
                    f"El tramo reescalado visible va de `{metrics.first_non1_date}` a `{metrics.last_non1_date}`.",
                    f"El primer dia neutro posterior observado es `{metrics.first_one_date}`.",
                ]
            )
        if metrics.split_non1_pct > 80:
            conclusion.append("La masa reescalada es muy alta porque el evento cae muy tarde en el mes o porque casi todo el mes pertenece al tramo previo.")
        elif metrics.split_non1_pct < 20:
            conclusion.append("La masa reescalada es baja porque el evento cae muy pronto y la mayor parte del mes ya vive en la nueva escala.")
        else:
            conclusion.append("La proporcion reescalada es intermedia y coherente con una frontera temporal de split que parte el mes en dos regimenes de escala.")
        conclusion.append("Si el patron visual raw muestra salto y la vista split-normalized lo absorbe sin deformar el tramo posterior, la lectura correcta es que el shock era mecanico y no alpha.")

    return que, responde, lectura, conclusion


def build_readout(manifest: pd.DataFrame) -> str:
    lines = [
        "# Ohlcv 1m Split-Normalized | piloto visual de auditoria",
        "",
        "## Rol",
        "",
        "Este readout no existe para demostrar que el script corre.",
        "",
        "Existe para que un inspector pueda mirar casos concretos y decidir si la capa `1m_split_normalized` esta corrigiendo discontinuidades mecanicas reales sin inventarse una serie ficticia.",
        "",
        "## Formula contractual",
        "",
        "- `px_split_normalized = px_raw * future_split_factor`",
        "- `future_split_factor(date_t) = producto de split_ratio para toda execution_date > date_t`",
        "",
        "## Como leer las imagenes",
        "",
        "- panel superior izquierdo: `1m raw` del mes completo",
        "- panel superior derecho: `1m split_normalized` del mes completo",
        "- panel central izquierdo: `1m raw` en ventana focalizada alrededor del evento o ancla",
        "- panel central derecho: `1m split_normalized` en la misma ventana",
        "- panel inferior: `future_split_factor` por fecha",
        "",
        "La linea roja marca:",
        "",
        "- la fecha del split si el caso contiene evento interno",
        "- o la fecha ancla relevante si el caso es un control pre-evento",
        "",
        "## Que falsaria la hipotesis",
        "",
        "- meses pre-evento con `future_split_factor = 1` de forma sistematica",
        "- meses post-evento con factor `!= 1` sin otro split futuro",
        "- o una vista split-normalized que no absorba la discontinuidad mecanica observada en raw",
        "",
        "## Casos",
        "",
    ]

    for _, row in manifest.iterrows():
        ticker = str(row["ticker"])
        year = int(row["year"])
        month = int(row["month"])
        raw = pd.read_parquet(_raw_file(ticker, year, month))
        norm = pd.read_parquet(_norm_file(ticker, year, month))
        splits = _load_splits(ticker)
        metrics = _compute_case_metrics(row, norm, splits)
        que, responde, lectura, conclusion = _case_narrative(metrics)
        lines.extend(
            [
                f"### {ticker} | {year}-{month:02d} | {row['role']}",
                "",
                f"![{ticker} {year}-{month:02d}]({_image_rel(row)})",
                "",
                "**Que muestra**",
                "",
            ]
        )
        lines.extend([f"- {x}" for x in que])
        lines.extend(["", "**Responde**", ""])
        lines.extend([f"- {x}" for x in responde])
        lines.extend(["", "**Lectura tecnica**", ""])
        lines.extend([f"- {x}" for x in lectura])
        lines.extend(["", "**Conclusion de auditoria**", ""])
        lines.extend([f"- {x}" for x in conclusion])
        lines.extend(["", "---", ""])
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Exporta el readout visual del piloto `1m_split_normalized`.")
    ap.add_argument("--manifest", default=str(MANIFEST_PATH))
    ap.add_argument("--output-md", default=str(OUT_MD))
    ap.add_argument("--output-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    manifest = pd.read_csv(args.manifest)
    out_dir = Path(args.output_dir)
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    for _, row in manifest.iterrows():
        ticker = str(row["ticker"])
        year = int(row["year"])
        month = int(row["month"])
        raw = pd.read_parquet(_raw_file(ticker, year, month))
        norm = pd.read_parquet(_norm_file(ticker, year, month))
        splits = _load_splits(ticker)
        metrics = _compute_case_metrics(row, norm, splits)
        fig = _render_case_figure(row, raw, norm, metrics)
        fig.savefig(img_dir / f"{_case_slug(row)}.png", dpi=140, bbox_inches="tight")
        plt.close(fig)

    md = build_readout(manifest)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(md, encoding="utf-8")
    print(f"wrote {args.output_md}")
    print(f"images {img_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
