from __future__ import annotations

from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.price_views import apply_split_normalized_view


DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "1m_split_normalized"
AUDIT_ROOT = DOSSIER_DIR / "evidence_assets" / "full_universe_split_audit"
POP_ROOT = DOSSIER_DIR / "population_visual_overview"
CASE_ROOT = DOSSIER_DIR / "event_case_evidence_packs"
CASE_IMG_ROOT = CASE_ROOT / "images"
READOUT_PATH = CASE_ROOT / "ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md"
CASE_MANIFEST_PATH = CASE_ROOT / "ohlcv_1m_split_normalized_visual_case_manifest_v0_1.csv"
POP_MANIFEST_PATH = POP_ROOT / "ohlcv_1m_split_normalized_population_visual_manifest_v0_1.csv"

MINUTE_ROOT = Path(r"D:\ohlcv_1m")
SPLITS_ROOT = Path(r"C:\TSIS_Data\data\additional\corporate_actions\splits")


def load_assets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cases = pd.read_parquet(AUDIT_ROOT / "full_universe_split_event_cases.parquet")
    meta = pd.read_csv(AUDIT_ROOT / "full_universe_split_event_audit_meta.csv")
    status = pd.read_csv(AUDIT_ROOT / "full_universe_split_event_status_summary.csv")
    cases["event_date"] = pd.to_datetime(cases["event_date"], errors="coerce")
    cases["split_direction"] = np.where(
        pd.to_numeric(cases["split_ratio"], errors="coerce").lt(1.0),
        "reverse_split",
        np.where(pd.to_numeric(cases["split_ratio"], errors="coerce").gt(1.0), "forward_split", "neutral"),
    )
    return cases, meta, status


def savefig(fig: plt.Figure, root: Path, name: str, title: str, question: str) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return {"image": name, "title": title, "question": question, "image_path": str(path)}


def bar_labels(ax, orient: str = "v") -> None:
    if orient == "v":
        for p in ax.patches:
            h = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2, h, f"{int(h):,}", ha="center", va="bottom", fontsize=8)
    else:
        for p in ax.patches:
            w = p.get_width()
            ax.text(w, p.get_y() + p.get_height() / 2, f" {int(w):,}", ha="left", va="center", fontsize=8)


def export_population_visuals(cases: pd.DataFrame, meta: pd.DataFrame, status: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, str]] = []

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)
    ordered = status.sort_values("n_cases", ascending=False)
    axes[0].bar(ordered["status"], ordered["n_cases"], color=["#4c78a8", "#f58518", "#e45756", "#72b7b2"][: len(ordered)])
    axes[0].set_title("Full-universe split event audit status", loc="left", weight="bold")
    axes[0].set_ylabel("event cases")
    axes[0].tick_params(axis="x", rotation=20)
    axes[0].grid(True, axis="y", alpha=0.25)
    bar_labels(axes[0])
    pass_cases = int(meta["pass_cases"].iloc[0])
    fail_cases = int(meta["fail_cases"].iloc[0])
    non_pass = int(meta["total_event_cases"].iloc[0]) - pass_cases - fail_cases
    axes[1].pie(
        [pass_cases, non_pass, fail_cases],
        labels=["PASS", "coverage-limited", "FAIL"],
        autopct="%1.1f%%",
        colors=["#59a14f", "#bab0ab", "#e15759"],
        startangle=90,
    )
    axes[1].set_title("Auditable result vs coverage limits", loc="left", weight="bold")
    records.append(savefig(fig, POP_ROOT, "00_population_status_overview.png", "Population Status Overview", "How the full split-event audit resolves into PASS, FAIL and coverage-limited states."))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), constrained_layout=True)
    direction = cases.groupby(["status", "split_direction"]).size().unstack(fill_value=0)
    direction.plot(kind="bar", stacked=True, ax=axes[0], color=["#4c78a8", "#f58518", "#72b7b2"])
    axes[0].set_title("Status by split direction", loc="left", weight="bold")
    axes[0].set_ylabel("event cases")
    axes[0].tick_params(axis="x", rotation=20)
    axes[0].grid(True, axis="y", alpha=0.25)
    pass_df = cases.loc[cases["status"].eq("PASS")].copy()
    bins = [0, 0.02, 0.05, 0.1, 0.25, 0.5, 1, 2, 10, np.inf]
    labels = ["<0.02", "0.02-0.05", "0.05-0.10", "0.10-0.25", "0.25-0.50", "0.50-1", "1-2", "2-10", ">10"]
    pass_df["ratio_bucket"] = pd.cut(pass_df["split_ratio"], bins=bins, labels=labels, include_lowest=True)
    rb = pass_df["ratio_bucket"].value_counts().reindex(labels).fillna(0)
    axes[1].bar(rb.index.astype(str), rb.values, color="#59a14f")
    axes[1].set_title("PASS cases by split ratio bucket", loc="left", weight="bold")
    axes[1].set_ylabel("PASS cases")
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].grid(True, axis="y", alpha=0.25)
    records.append(savefig(fig, POP_ROOT, "01_population_direction_and_ratio.png", "Direction And Ratio", "Whether the audit covers both reverse and forward split mechanics across ratio severities."))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), constrained_layout=True)
    yearly = cases.groupby([cases["event_date"].dt.year, "status"]).size().unstack(fill_value=0)
    yearly.plot(kind="area", stacked=True, ax=axes[0], color=["#e15759", "#bab0ab", "#f58518", "#4c78a8"])
    axes[0].set_title("Event status by year", loc="left", weight="bold")
    axes[0].set_xlabel("event year")
    axes[0].set_ylabel("event cases")
    axes[0].grid(True, alpha=0.25)
    coverage = cases.assign(has_coverage=cases["status"].ne("NO_1M_COVERAGE"))
    cov_year = coverage.groupby(coverage["event_date"].dt.year)["has_coverage"].mean() * 100.0
    axes[1].plot(cov_year.index, cov_year.values, marker="o", color="#4c78a8")
    axes[1].set_title("Share with any 1m coverage by year", loc="left", weight="bold")
    axes[1].set_ylabel("% cases with coverage")
    axes[1].grid(True, alpha=0.25)
    records.append(savefig(fig, POP_ROOT, "02_population_temporal_coverage.png", "Temporal Coverage", "How coverage limitations distribute through event years."))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), constrained_layout=True)
    pass_rows = cases.loc[cases["status"].eq("PASS")].copy()
    axes[0].hist(pass_rows["rows_total"], bins=40, color="#4c78a8", alpha=0.9)
    axes[0].set_title("PASS rows_total distribution", loc="left", weight="bold")
    axes[0].set_xlabel("rows in three-month event window")
    axes[0].set_ylabel("event cases")
    axes[0].grid(True, alpha=0.25)
    axes[1].hist(pass_rows["max_abs_multiplier_error"].fillna(0), bins=30, color="#59a14f", alpha=0.9)
    axes[1].set_title("PASS max_abs_multiplier_error", loc="left", weight="bold")
    axes[1].set_xlabel("absolute multiplier error")
    axes[1].set_ylabel("event cases")
    axes[1].grid(True, alpha=0.25)
    records.append(savefig(fig, POP_ROOT, "03_population_pass_invariant_strength.png", "PASS Invariant Strength", "Whether PASS cases have enough rows and whether multiplier errors are materially nonzero."))

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    missing = cases.loc[cases["status"].ne("PASS")].copy()
    miss = missing.groupby(["status", "split_direction"]).size().unstack(fill_value=0).sort_index()
    miss.plot(kind="barh", stacked=True, ax=ax, color=["#4c78a8", "#f58518", "#72b7b2"])
    ax.set_title("Coverage-limited cases by status and direction", loc="left", weight="bold")
    ax.set_xlabel("event cases")
    ax.grid(True, axis="x", alpha=0.25)
    records.append(savefig(fig, POP_ROOT, "04_population_coverage_limited_anatomy.png", "Coverage-Limited Anatomy", "Which non-PASS cases are real limits of available 1m history rather than semantic failures."))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), constrained_layout=True)
    top_tickers = cases.groupby("ticker").size().sort_values(ascending=False).head(20).sort_values()
    axes[0].barh(top_tickers.index, top_tickers.values, color="#4c78a8")
    axes[0].set_title("Top tickers by split-event cases", loc="left", weight="bold")
    axes[0].set_xlabel("event cases")
    bar_labels(axes[0], "h")
    top_missing = cases.loc[cases["status"].ne("PASS")].groupby("ticker").size().sort_values(ascending=False).head(20).sort_values()
    axes[1].barh(top_missing.index, top_missing.values, color="#f58518")
    axes[1].set_title("Top tickers by coverage-limited cases", loc="left", weight="bold")
    axes[1].set_xlabel("event cases")
    bar_labels(axes[1], "h")
    records.append(savefig(fig, POP_ROOT, "05_population_ticker_concentration.png", "Ticker Concentration", "Whether audit mass or coverage limitations are concentrated in a few tickers."))

    out = pd.DataFrame(records)
    out.to_csv(POP_MANIFEST_PATH, index=False)
    return out


def month_path(ticker: str, year: int, month: int) -> Path:
    return MINUTE_ROOT / f"ticker={ticker}" / f"year={year}" / f"month={month:02d}" / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"


def split_file(ticker: str) -> Path:
    return SPLITS_ROOT / f"ticker={ticker}" / f"splits_{ticker}.parquet"


def neighbor_months(event_date: pd.Timestamp) -> list[tuple[int, int]]:
    current = pd.Timestamp(event_date).normalize().replace(day=1)
    prev = (current - pd.offsets.MonthBegin(1)).normalize()
    nxt = (current + pd.offsets.MonthBegin(1)).normalize()
    return [(prev.year, prev.month), (current.year, current.month), (nxt.year, nxt.month)]


def load_raw_window(row: pd.Series) -> pd.DataFrame:
    frames = []
    for year, month in neighbor_months(pd.Timestamp(row["event_date"])):
        p = month_path(str(row["ticker"]), year, month)
        if p.exists():
            frames.append(pd.read_parquet(p))
    if not frames:
        return pd.DataFrame()
    raw = pd.concat(frames, ignore_index=True)
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw["ts_utc"] = pd.to_datetime(raw["ts_utc"], errors="coerce", utc=True)
    return raw.sort_values("ts_utc").reset_index(drop=True)


def load_splits(ticker: str) -> pd.DataFrame:
    p = split_file(ticker)
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    if "_empty" in df.columns and len(df) and bool(df["_empty"].iloc[0]) is True:
        return pd.DataFrame()
    return df


def event_daily_frame(row: pd.Series) -> pd.DataFrame:
    raw = load_raw_window(row)
    if raw.empty:
        return pd.DataFrame()
    norm, _ = apply_split_normalized_view(raw, splits=load_splits(str(row["ticker"])), date_col="date", price_cols=("o", "h", "l", "c", "vw"))
    for col in ["c", "c_split_normalized", "future_split_factor"]:
        norm[col] = pd.to_numeric(norm[col], errors="coerce")
    daily = (
        norm.groupby("date", as_index=False)
        .agg(
            close_raw=("c", "last"),
            close_split_normalized=("c_split_normalized", "last"),
            high_raw=("h", "max"),
            low_raw=("l", "min"),
            high_split_normalized=("h_split_normalized", "max"),
            low_split_normalized=("l_split_normalized", "min"),
            future_split_factor=("future_split_factor", "max"),
            minute_rows=("c", "size"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    return daily


def render_event_case(row: pd.Series, image_path: Path) -> None:
    status = str(row["status"])
    if status == "NO_1M_COVERAGE":
        fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0.02, 0.08), 0.96, 0.84, fill=False, linewidth=1.2, edgecolor="#6b7280"))
        ax.text(0.04, 0.86, "Coverage-limited split event", fontsize=18, weight="bold", ha="left")
        ax.text(0.04, 0.78, "NO_1M_COVERAGE", fontsize=15, weight="bold", color="#b45309", ha="left")
        fields = [
            ("ticker", str(row["ticker"])),
            ("event_date", pd.Timestamp(row["event_date"]).date().isoformat()),
            ("split", f"{row['split_from']} -> {row['split_to']}"),
            ("split_ratio", f"{float(row['split_ratio']):.8g}"),
            ("rows_total", str(int(row["rows_total"]))),
            ("audit_status", status),
        ]
        y = 0.66
        for label, value in fields:
            ax.text(0.06, y, f"{label}:", fontsize=11, weight="bold", color="#374151", ha="left")
            ax.text(0.24, y, value, fontsize=11, color="#111827", ha="left")
            y -= 0.075
        notes = [
            "Existe split en fuentes maestras.",
            "No hay historia 1m cargable en la ventana de evento.",
            "Esto limita la auditoria empirica.",
            "No es una violacion semantica observada.",
        ]
        ax.text(0.06, 0.22, "Lectura:", fontsize=11, weight="bold", color="#374151", ha="left")
        ax.text(0.18, 0.22, "\n".join(f"- {n}" for n in notes), fontsize=11, color="#111827", ha="left", va="top")
        fig.savefig(image_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return

    daily = event_daily_frame(row)
    if daily.empty:
        fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
        ax.axis("off")
        ax.text(0.03, 0.92, f"{row['ticker']} | {row['event_date']} | sin daily frame cargable", va="top", ha="left", fontsize=13)
        fig.savefig(image_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return

    event_date = pd.Timestamp(row["event_date"])
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True, constrained_layout=True)
    axes[0].plot(daily["date"], daily["close_raw"], marker="o", linewidth=1.4, color="#6b7280", label="close raw")
    axes[0].fill_between(daily["date"], daily["low_raw"], daily["high_raw"], color="#9ca3af", alpha=0.18, label="raw low-high")
    axes[0].axvline(event_date, color="#ef4444", linestyle="--", linewidth=1.2)
    axes[0].set_title("Daily aggregate from 1m raw around split event", loc="left", weight="bold")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(loc="upper left", fontsize=8)

    axes[1].plot(daily["date"], daily["close_split_normalized"], marker="o", linewidth=1.4, color="#2563eb", label="close split_normalized")
    axes[1].fill_between(daily["date"], daily["low_split_normalized"], daily["high_split_normalized"], color="#60a5fa", alpha=0.18, label="split-normalized low-high")
    axes[1].axvline(event_date, color="#ef4444", linestyle="--", linewidth=1.2)
    axes[1].set_title("Daily aggregate from 1m split-normalized around split event", loc="left", weight="bold")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(loc="upper left", fontsize=8)

    axes[2].step(daily["date"], daily["future_split_factor"], where="post", color="#dc2626", linewidth=1.8, label="future_split_factor")
    axes[2].axhline(1.0, color="black", linewidth=0.8, alpha=0.5)
    axes[2].axvline(event_date, color="#ef4444", linestyle="--", linewidth=1.2)
    axes[2].set_title("Future split factor", loc="left", weight="bold")
    axes[2].grid(True, alpha=0.25)
    axes[2].legend(loc="upper left", fontsize=8)

    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        for label in ax.get_xticklabels():
            label.set_rotation(25)
            label.set_horizontalalignment("right")

    fig.suptitle(
        f"{row['ticker']} | {pd.Timestamp(row['event_date']).date()} | {row['split_direction']} | status={status} | ratio={float(row['split_ratio']):.6g}",
        fontsize=14,
    )
    fig.savefig(image_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def select_cases(cases: pd.DataFrame) -> pd.DataFrame:
    picks = []
    pass_cases = cases.loc[cases["status"].eq("PASS")].copy()
    pass_cases["ratio_distance"] = (np.log(pd.to_numeric(pass_cases["split_ratio"], errors="coerce")).abs()).fillna(0)
    picks.append(pass_cases.loc[pass_cases["split_direction"].eq("reverse_split")].sort_values(["ratio_distance", "rows_total"], ascending=False).head(8))
    picks.append(pass_cases.loc[pass_cases["split_direction"].eq("forward_split")].sort_values(["ratio_distance", "rows_total"], ascending=False).head(6))
    for status, n in [("NO_PRE_COVERAGE", 4), ("NO_POST_COVERAGE", 4), ("NO_1M_COVERAGE", 6)]:
        picks.append(cases.loc[cases["status"].eq(status)].sort_values(["rows_total", "ticker"], ascending=[False, True]).head(n))
    out = pd.concat(picks, ignore_index=True)
    out = out.drop_duplicates(["ticker", "event_date", "split_from", "split_to"]).reset_index(drop=True)
    out["visual_rank"] = np.arange(1, len(out) + 1)
    out["visual_family"] = np.select(
        [
            out["status"].eq("PASS") & out["split_direction"].eq("reverse_split"),
            out["status"].eq("PASS") & out["split_direction"].eq("forward_split"),
            out["status"].eq("NO_PRE_COVERAGE"),
            out["status"].eq("NO_POST_COVERAGE"),
            out["status"].eq("NO_1M_COVERAGE"),
        ],
        ["pass_reverse_split", "pass_forward_split", "coverage_no_pre", "coverage_no_post", "coverage_no_1m"],
        default="other",
    )
    return out


def export_case_visuals(cases: pd.DataFrame) -> pd.DataFrame:
    CASE_IMG_ROOT.mkdir(parents=True, exist_ok=True)
    selected = select_cases(cases)
    rows = []
    for _, row in selected.iterrows():
        event_date = pd.Timestamp(row["event_date"]).date().isoformat()
        name = f"{int(row['visual_rank']):02d}_{row['visual_family']}_{row['ticker']}_{event_date}.png".replace(":", "-")
        render_event_case(row, CASE_IMG_ROOT / name)
        rec = row.to_dict()
        rec["image"] = f"images/{name}"
        rows.append(rec)
    out = pd.DataFrame(rows)
    out.to_csv(CASE_MANIFEST_PATH, index=False)
    return out


POP_READINGS = {
    "00_population_status_overview.png": (
        "Muestra el resultado agregado de la auditoria full-universe de eventos split: `PASS`, estados limitados por cobertura y `FAIL`.",
        "Responde si hay fallos semanticos observados en casos auditables y separa error real de falta de cobertura empirica.",
        "No responde si la capa fisica esta materializada para todo ticker-month del universo; responde al universo de eventos split auditables.",
        "La conclusion fuerte es `FAIL = 0`; los casos no PASS deben leerse como limites de cobertura, no como evidencia de transformacion incorrecta.",
    ),
    "01_population_direction_and_ratio.png": (
        "Muestra que la auditoria cubre reverse splits, forward splits y severidades distintas de ratio.",
        "Responde si el PASS se concentra solo en un tipo facil de evento o si atraviesa familias mecanicas diferentes.",
        "No responde si cada ticker tiene historia intradia suficiente; esa pregunta vive en cobertura.",
        "El inspector puede confiar en que el piloto visual no era solo un ejemplo bonito: el barrido incluye direcciones y ratios variados.",
    ),
    "02_population_temporal_coverage.png": (
        "Muestra la distribucion temporal de eventos y la proporcion con alguna cobertura `1m` por ano.",
        "Responde si los limites de auditoria vienen de la disponibilidad temporal de `1m`, especialmente en anos menos cubiertos.",
        "No responde si un ano debe ponderar igual en backtest; solo ensena disponibilidad empirica para auditar splits.",
        "Cualquier claim full-universe debe distinguir universo de eventos de universo fisicamente materializado.",
    ),
    "03_population_pass_invariant_strength.png": (
        "Muestra filas disponibles en casos PASS y distribucion de `max_abs_multiplier_error`.",
        "Responde si PASS esta sostenido por ventanas con datos y errores de multiplicador materialmente nulos.",
        "No responde a calidad general de OHLCV raw; solo a invariantes de escala split-normalized.",
        "La auditoria de semantica split queda fuerte, pero no sustituye la auditoria raw de `minute`.",
    ),
    "04_population_coverage_limited_anatomy.png": (
        "Muestra la anatomia de `NO_PRE_COVERAGE`, `NO_POST_COVERAGE` y `NO_1M_COVERAGE` por direccion de split.",
        "Responde que los no PASS son familias de cobertura insuficiente, no fallos del algoritmo.",
        "No responde que esos eventos esten resueltos visualmente; declara que no se pueden falsar plenamente con la historia disponible.",
        "Los consumidores deben conservar estos estados como caveats de coverage si usan eventos fuera del perimetro auditable.",
    ),
    "05_population_ticker_concentration.png": (
        "Muestra concentracion de eventos y de limites de cobertura por ticker.",
        "Responde si la carga de auditoria se reparte o queda concentrada en nombres con muchos eventos.",
        "No responde a causalidad economica de cada ticker; solo ubica concentraciones operativas.",
        "Ayuda a priorizar ampliaciones futuras de cobertura o inspeccion si se decide materializar mas casos.",
    ),
}


def population_reading(image: str) -> tuple[str, str, str, str]:
    return POP_READINGS[image]


def case_reading(row: pd.Series) -> tuple[str, str, str, str]:
    status = str(row["status"])
    direction = str(row["split_direction"])
    ticker = str(row["ticker"])
    event_date = pd.Timestamp(row["event_date"]).date().isoformat()
    ratio = float(row["split_ratio"])
    if status == "PASS":
        qm = (
            f"La imagen muestra el evento `{ticker} {event_date}` con cobertura antes y despues del split. "
            f"El panel raw y el split-normalized permiten ver la transformacion de escala, y el factor cambia segun la regla contractual. Ratio auditado: `{ratio:.6g}`."
        )
        resp = "Responde que este caso concreto pasa los invariantes: tramo pre-evento reescalado, tramo post-evento neutro y error multiplicador nulo dentro de tolerancia."
        no = "No responde que todo OHLCV intradia del ticker sea limpio ni que la capa sea adjusted economica; solo valida semantica de split para este evento."
        cons = "Puede usarse como evidencia forense positiva de `1m_split_normalized` para comparabilidad cross-session alrededor de splits."
    elif status == "NO_PRE_COVERAGE":
        qm = (
            f"La imagen muestra `{ticker} {event_date}` con historia posterior disponible pero sin tramo previo suficiente en la ventana auditada."
        )
        resp = "Responde que no se puede falsar la mitad pre-evento del invariante con la cobertura existente."
        no = "No responde que la transformacion este mal; la ausencia de pre-cobertura no es un FAIL semantico."
        cons = "Debe quedar como limite de coverage. No debe promocionarse a PASS, pero tampoco contarse como fallo."
    elif status == "NO_POST_COVERAGE":
        qm = (
            f"La imagen muestra `{ticker} {event_date}` con historia previa disponible pero sin tramo posterior suficiente en la ventana auditada."
        )
        resp = "Responde que no se puede falsar la mitad post-evento del invariante con la cobertura existente."
        no = "No responde que la capa arrastre factor incorrecto despues del evento; no hay base empirica suficiente para esa afirmacion."
        cons = "Debe conservarse como caveat de coverage si un consumidor necesita prueba bilateral completa."
    elif status == "NO_1M_COVERAGE":
        qm = (
            f"La tarjeta muestra `{ticker} {event_date}` como evento existente en splits maestros, pero sin historia `1m` cargable para auditar."
        )
        resp = "Responde que el evento pertenece al universo de referencia de splits pero queda fuera del universo empiricamente auditable con `1m`."
        no = "No responde nada sobre correccion visual de precio porque no hay barras que inspeccionar."
        cons = "Debe excluirse de claims de PASS y reportarse como limite de cobertura, no como error de la transformacion."
    else:
        qm = f"La imagen muestra un caso `{status}`."
        resp = "Responde al estado local de auditoria."
        no = "No responde a una promocion global."
        cons = "Requiere revision especifica."
    return qm, resp, no, cons


def build_readout(pop: pd.DataFrame, cases: pd.DataFrame) -> str:
    lines = [
        "# Ohlcv 1m Split-Normalized Visual Inspector Pack v0.1",
        "",
        "Fecha de referencia: 2026-06-07.",
        "",
        "Este dossier aplica el modelo inspector general-a-particular a `ohlcv_1m_split_normalized`.",
        "",
        "## Alcance",
        "",
        "- dataset: `ohlcv_1m_split_normalized_v0_1`",
        "- pregunta: semantica de escala split-normalized en eventos de split/reverse split",
        "- unidad poblacional auditada: `ticker + execution_date`",
        "- casos de evento auditados: `3335`",
        "- casos PASS: `2280`",
        "- casos FAIL: `0`",
        "- visuales poblacionales: `6`",
        f"- visuales de caso: `{len(cases)}`",
        f"- total de imagenes incrustadas: `{len(pop) + len(cases)}`",
        "",
        "## Regla De Lectura",
        "",
        "La auditoria no demuestra que todo `1m` raw sea limpio ni que exista una materializacion fisica full-universe para todos los ticker-month.",
        "",
        "Demuestra algo mas preciso:",
        "",
        "- la regla `future_split_factor(date_t)` esta bien definida;",
        "- los eventos con cobertura bilateral suficiente no muestran fallos semanticos;",
        "- los no PASS son limites de cobertura, no fallos observados;",
        "- y el uso correcto es comparabilidad cross-session, no verdad local de ejecucion.",
        "",
        "## Menu",
        "",
        "- [Mapa Poblacional Visual](#mapa-poblacional-visual)",
        "- [Casepacks Visuales](#casepacks-visuales)",
        "",
        "## Mapa Poblacional Visual",
        "",
    ]
    for _, row in pop.iterrows():
        qm, resp, no, cons = population_reading(str(row["image"]))
        lines.extend(
            [
                f"### {row['title']}",
                "",
                f"Pregunta: {row['question']}",
                "",
                f"![{row['title']}](../population_visual_overview/{row['image']})",
                "",
                "**Que muestra**",
                "",
                f"- {qm}",
                "",
                "**Responde**",
                "",
                f"- {resp}",
                "",
                "**No responde**",
                "",
                f"- {no}",
                "",
                "**Consecuencia**",
                "",
                f"- {cons}",
                "",
            ]
        )

    lines.extend(["## Casepacks Visuales", ""])
    family_titles = {
        "pass_reverse_split": "PASS / Reverse Split",
        "pass_forward_split": "PASS / Forward Split",
        "coverage_no_pre": "Coverage Limited / No Pre Coverage",
        "coverage_no_post": "Coverage Limited / No Post Coverage",
        "coverage_no_1m": "Coverage Limited / No 1m Coverage",
    }
    for family, group in cases.groupby("visual_family", sort=False):
        lines.extend([f"### {family_titles.get(family, family)}", ""])
        for _, row in group.iterrows():
            qm, resp, no, cons = case_reading(row)
            event_date = pd.Timestamp(row["event_date"]).date().isoformat()
            lines.extend(
                [
                    f"#### {int(row['visual_rank']):02d}. {row['ticker']} {event_date}",
                    "",
                    f"status: `{row['status']}`  ",
                    f"split_direction: `{row['split_direction']}`  ",
                    f"split_ratio: `{float(row['split_ratio']):.8g}`  ",
                    f"rows_total: `{int(row['rows_total']):,}`  ",
                    f"rows_pre: `{int(row['rows_pre']):,}`  ",
                    f"rows_post: `{int(row['rows_post']):,}`  ",
                    f"max_abs_multiplier_error: `{row['max_abs_multiplier_error']}`",
                    "",
                    f"![{row['ticker']} {event_date}](./{row['image']})",
                    "",
                    "**Que muestra**",
                    "",
                    f"- {qm}",
                    "",
                    "**Responde**",
                    "",
                    f"- {resp}",
                    "",
                    "**No responde**",
                    "",
                    f"- {no}",
                    "",
                    "**Consecuencia**",
                    "",
                    f"- {cons}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    cases, meta, status = load_assets()
    pop = export_population_visuals(cases, meta, status)
    selected = export_case_visuals(cases)
    READOUT_PATH.write_text(build_readout(pop, selected), encoding="utf-8", newline="\n")
    print(READOUT_PATH)
    print(f"population_visuals={len(pop)}")
    print(f"case_visuals={len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
