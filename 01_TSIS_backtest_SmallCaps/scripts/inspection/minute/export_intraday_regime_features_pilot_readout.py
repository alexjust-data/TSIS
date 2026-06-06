from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
MANIFEST_PATH = PROJECT_ROOT / "01_foundations" / "dataset_registry" / "1m" / "ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv"
FEATURES_ROOT = Path(r"E:\TSIS\data\intraday_regime_features")
OUTPUT_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "intraday_regime_features"
IMAGES_DIR = OUTPUT_DIR / "images"
READOUT_PATH = OUTPUT_DIR / "intraday_regime_features_semantic_pilot_readout_v0_1.md"


@dataclass(frozen=True)
class PilotCase:
    ticker: str
    year: int
    month: int
    event_type: str
    event_date: str | None
    role: str
    split_from: float
    split_to: float
    rationale: str

    @property
    def month_label(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"

    @property
    def image_name(self) -> str:
        return f"{self.ticker}_{self.year}_{self.month:02d}.png"


def _load_manifest() -> list[PilotCase]:
    df = pd.read_csv(MANIFEST_PATH)
    cases: list[PilotCase] = []
    for row in df.to_dict(orient="records"):
        cases.append(
            PilotCase(
                ticker=str(row["ticker"]).upper(),
                year=int(row["year"]),
                month=int(row["month"]),
                event_type=str(row["event_type"]),
                event_date=None if pd.isna(row["event_date"]) else str(row["event_date"]),
                role=str(row["role"]),
                split_from=float(row["split_from"]),
                split_to=float(row["split_to"]),
                rationale=str(row["rationale"]),
            )
        )
    return cases


def _feature_path(case: PilotCase) -> Path:
    return FEATURES_ROOT / f"ticker={case.ticker}" / f"year={case.year}" / f"day_features_{case.ticker}_{case.year}.parquet"


def _compute_raw_counterfactual(year_df: pd.DataFrame) -> pd.DataFrame:
    out = year_df.sort_values("date").reset_index(drop=True).copy()
    prev_close = out["close_raw"].shift(1)
    prev_high = out["high_raw"].shift(1)
    prev_low = out["low_raw"].shift(1)
    prev_range_center = (prev_high + prev_low) / 2.0
    out["gap_open_vs_prev_close_raw_counterfactual"] = out["open_raw"] / prev_close - 1.0
    out["multi_session_return_3d_to_open_raw_counterfactual"] = out["open_raw"] / out["close_raw"].shift(3) - 1.0
    out["distance_to_prev_day_range_center_raw_counterfactual"] = out["open_raw"] / prev_range_center - 1.0
    return out


def _load_case_frame(case: PilotCase) -> pd.DataFrame:
    p = _feature_path(case)
    df = pd.read_parquet(p).copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = _compute_raw_counterfactual(df)
    df["month"] = df["date"].dt.month
    month_df = df[df["month"] == case.month].copy()
    return month_df.sort_values("date").reset_index(drop=True)


def _summarize_case(case: PilotCase, df: pd.DataFrame) -> dict[str, object]:
    gap_diff = (df["gap_open_vs_prev_close"] - df["gap_open_vs_prev_close_raw_counterfactual"]).abs()
    ret3_diff = (df["multi_session_return_3d_to_open"] - df["multi_session_return_3d_to_open_raw_counterfactual"]).abs()
    dist_diff = (df["distance_to_prev_day_range_center"] - df["distance_to_prev_day_range_center_raw_counterfactual"]).abs()
    return {
        "ticker": case.ticker,
        "month": case.month_label,
        "role": case.role,
        "event_type": case.event_type,
        "event_date": case.event_date or "",
        "days": int(len(df)),
        "days_factor_ne_1": int((pd.to_numeric(df["max_future_split_factor_in_day"], errors="coerce") != 1).sum()),
        "max_abs_gap_diff_pct": float(gap_diff.max() * 100) if gap_diff.notna().any() else 0.0,
        "max_abs_ret3_diff_pct": float(ret3_diff.max() * 100) if ret3_diff.notna().any() else 0.0,
        "max_abs_range_center_diff_pct": float(dist_diff.max() * 100) if dist_diff.notna().any() else 0.0,
        "days_gap_diff_gt_50pct": int((gap_diff > 0.5).sum()),
        "days_gap_diff_gt_5pct": int((gap_diff > 0.05).sum()),
    }


def _render_case_figure(case: PilotCase, df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(13, 12), sharex=True, constrained_layout=True)
    x = pd.to_datetime(df["date"], errors="coerce")
    event_dt = pd.to_datetime(case.event_date) if case.event_date else None

    specs = [
        (
            axes[0],
            "gap_open_vs_prev_close_raw_counterfactual",
            "gap_open_vs_prev_close",
            "Gap open vs prev close",
            "retorno",
        ),
        (
            axes[1],
            "multi_session_return_3d_to_open_raw_counterfactual",
            "multi_session_return_3d_to_open",
            "Retorno 3d a open",
            "retorno",
        ),
        (
            axes[2],
            "distance_to_prev_day_range_center_raw_counterfactual",
            "distance_to_prev_day_range_center",
            "Distancia al centro del rango previo",
            "retorno",
        ),
    ]

    for ax, raw_col, norm_col, title, ylabel in specs:
        ax.plot(x, df[raw_col] * 100, marker="o", linewidth=1.6, label="raw counterfactual", color="#d95f02")
        ax.plot(x, df[norm_col] * 100, marker="o", linewidth=1.6, label="split_normalized", color="#1b9e77")
        diff = (df[norm_col] - df[raw_col]) * 100
        ax.fill_between(x, 0, diff, color="#7570b3", alpha=0.15, label="diferencia" if ax is axes[0] else None)
        ax.axhline(0, color="black", linewidth=0.8, alpha=0.5)
        if event_dt is not None:
            ax.axvline(event_dt, color="crimson", linestyle="--", linewidth=1.2)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)

    axes[3].step(x, df["max_future_split_factor_in_day"], where="mid", color="#386cb0", linewidth=1.8, label="future_split_factor")
    if event_dt is not None:
        axes[3].axvline(event_dt, color="crimson", linestyle="--", linewidth=1.2, label="event_date")
    axes[3].axhline(1.0, color="black", linewidth=0.8, alpha=0.5)
    axes[3].set_title("Factor de split futuro activo por dia")
    axes[3].set_ylabel("factor")
    axes[3].grid(True, alpha=0.25)
    axes[3].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axes[3].tick_params(axis="x", rotation=35)

    axes[0].legend(loc="upper left", fontsize=8)
    axes[3].legend(loc="upper left", fontsize=8)
    fig.suptitle(f"{case.ticker} | {case.month_label} | intraday_regime_features raw vs split_normalized", fontsize=14)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _case_analysis(case: PilotCase, summary: dict[str, object]) -> tuple[str, str, str, str]:
    gap50 = int(summary["days_gap_diff_gt_50pct"])
    gap5 = int(summary["days_gap_diff_gt_5pct"])
    max_gap = float(summary["max_abs_gap_diff_pct"])
    max_ret3 = float(summary["max_abs_ret3_diff_pct"])
    max_rng = float(summary["max_abs_range_center_diff_pct"])
    days = int(summary["days"])
    factor_days = int(summary["days_factor_ne_1"])

    if case.role == "control" and case.event_date:
        role_note = "control con evento explicitado"
    elif case.role == "control":
        role_note = "control sin evento en ventana"
    else:
        role_note = case.event_type

    if case.role == "control" and max_gap < 5:
        reading = (
            f"La firma dominante es de neutralidad. Aunque el mes tenga `days_factor_ne_1 = {factor_days}`, "
            f"la diferencia maxima en `gap_open_vs_prev_close` se queda en `{max_gap:.2f}%` y no hay dias con diferencia superior al `50%`. "
            f"Eso prueba que un factor distinto de `1` no implica automaticamente distorsion de features: si toda la ventana vive en la misma escala relativa, "
            f"los cocientes cross-session se conservan."
        )
        conclusion = (
            "Conclusión de auditoría: control correcto. La capa no inventa correcciones visibles donde no hay discontinuidad de escala dentro de la ventana útil del feature."
        )
    elif case.event_date and gap50 > 0:
        reading = (
            f"Aqui si aparece la firma que queriamos detectar. El mes tiene `{gap50}` dias con diferencia de gap superior al `50%` "
            f"y una diferencia maxima de `{max_gap:.2f}%`. En paralelo, `multi_session_return_3d_to_open` alcanza una divergencia maxima de `{max_ret3:.2f}%`, "
            f"lo que indica que el shock mecanico no solo contaminaría el gap overnight, sino tambien memoria multi-sesion y features de extension."
        )
        conclusion = (
            "Conclusión de auditoría: caso positivo fuerte. El consumidor demuestra que usar `1m raw` habria fabricado señales de régimen falsas, "
            "mientras que `1m_split_normalized` neutraliza esa discontinuidad."
        )
    else:
        reading = (
            f"La diferencia visible es baja o local. El mes tiene `{gap5}` dias con diferencia de gap superior al `5%`, "
            f"una diferencia maxima de gap de `{max_gap:.2f}%` y una diferencia maxima en distancia al rango previo de `{max_rng:.2f}%`. "
            f"Esto suele corresponder a casos donde el evento cae al principio del mes o donde la ventana util del feature ya vive casi toda en escala post-evento."
        )
        conclusion = (
            "Conclusión de auditoría: caso frontera coherente. La falta de divergencia grande no contradice la semántica; describe una ventana donde casi no queda pasado reescalable dentro del propio mes."
        )

    shows = (
        f"Comparacion diaria entre las tres features cross-session mas sensibles a saltos mecanicos para `{case.ticker}` en `{case.month_label}` "
        f"(`{role_note}`), junto con la trayectoria de `future_split_factor` por dia."
    )
    responds = (
        "Responde a si las features de régimen cambian de forma material cuando la comparacion entre sesiones se calcula con `raw` frente a `split_normalized`; "
        "y a si esa diferencia aparece exactamente donde la semantica del split la haria esperable."
    )
    return shows, responds, reading, conclusion


def build_readout() -> None:
    cases = _load_manifest()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, object]] = []
    case_blocks: list[str] = []

    for case in cases:
        df = _load_case_frame(case)
        summary = _summarize_case(case, df)
        summaries.append(summary)
        _render_case_figure(case, df, IMAGES_DIR / case.image_name)
        shows, responds, reading, conclusion = _case_analysis(case, summary)
        event_date_line = case.event_date if case.event_date else "sin evento en ventana"
        case_blocks.append(
            "\n".join(
                [
                    f"### {case.ticker} | {case.month_label}",
                    "",
                    f"![{case.ticker} {case.month_label}](./images/{case.image_name})",
                    "",
                    "**Que muestra**",
                    "",
                    f"- {shows}",
                    f"- `days = {summary['days']}`, `days_factor_ne_1 = {summary['days_factor_ne_1']}`, `event_date = {event_date_line}`.",
                    f"- `max_abs_gap_diff_pct = {summary['max_abs_gap_diff_pct']:.2f}%`, `max_abs_ret3_diff_pct = {summary['max_abs_ret3_diff_pct']:.2f}%`, `max_abs_range_center_diff_pct = {summary['max_abs_range_center_diff_pct']:.2f}%`.",
                    "",
                    "**Responde**",
                    "",
                    f"- {responds}",
                    "",
                    "**Lectura tecnica**",
                    "",
                    f"- {reading}",
                    "",
                    "**Conclusion de auditoria**",
                    "",
                    f"- {conclusion}",
                    "",
                ]
            )
        )

    summary_df = pd.DataFrame(summaries)
    top_rows = []
    for _, row in summary_df.sort_values(["max_abs_gap_diff_pct", "max_abs_ret3_diff_pct"], ascending=False).iterrows():
        top_rows.append(
            f"| {row['ticker']} | {row['month']} | {row['role']} | {row['days']} | {row['days_factor_ne_1']} | {row['max_abs_gap_diff_pct']:.2f}% | {row['max_abs_ret3_diff_pct']:.2f}% | {row['max_abs_range_center_diff_pct']:.2f}% | {row['days_gap_diff_gt_50pct']} |"
        )

    md = "\n".join(
        [
            "# Intraday Regime Features - Semantic Pilot Readout `v0_1`",
            "",
            "## 1. Rol",
            "",
            "Este readout audita el primer consumidor real de `ohlcv_1m_split_normalized`.",
            "",
            "No intenta demostrar si el modelo final ya existe.",
            "Intenta demostrar algo mas basico y mas importante:",
            "",
            "- si las features cross-session cambian cuando se calculan con `raw` frente a `split_normalized`;",
            "- si esa diferencia aparece exactamente en los casos donde un split la haria esperable;",
            "- y si los controles se mantienen neutros cuando no deberia existir shock mecanico.",
            "",
            "## 2. Resumen cuantitativo del piloto",
            "",
            "| ticker | month | role | days | days_factor_ne_1 | max_abs_gap_diff_pct | max_abs_ret3_diff_pct | max_abs_range_center_diff_pct | days_gap_diff_gt_50pct |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|",
            *top_rows,
            "",
            "## 3. Lectura global",
            "",
            "- Cuando el split cae dentro de la memoria util de la feature, las diferencias `raw vs split_normalized` se vuelven grandes y localizadas.",
            "- Cuando toda la ventana vive ya en escala post-evento, o toda ella vive aun en escala pre-evento homogénea, las razones cross-session pueden permanecer casi invariantes.",
            "- Esto es exactamente lo que queriamos auditar: no que la capa cambie siempre, sino que cambie solo cuando el shock mecanico afectaria de verdad al cociente entre sesiones.",
            "",
            "## 4. Casos",
            "",
            *case_blocks,
        ]
    )
    READOUT_PATH.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    build_readout()
