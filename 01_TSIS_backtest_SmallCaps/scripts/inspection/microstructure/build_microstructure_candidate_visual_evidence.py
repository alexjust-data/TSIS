from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = MODULE_ROOT.parent
DEFAULT_TEST_RUN = (
    REPO_ROOT
    / "tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1"
)
DEFAULT_CANDIDATE_DIR = (
    DEFAULT_TEST_RUN
    / "artifacts/microstructure_features_table_v0_2_candidate_output/microstructure_features_table_v0_2_candidate"
)
DEFAULT_WINDOW_MANIFEST = (
    DEFAULT_TEST_RUN
    / "artifacts/microstructure_candidate_materializer_manifest/"
    "microstructure_features_table_v0_2_candidate_window_manifest_v0_1.csv"
)
DEFAULT_OUTPUT_ROOT = MODULE_ROOT / "01_foundations/inspection_dossiers/microstructure_features"
DEFAULT_PACK_DIR = DEFAULT_OUTPUT_ROOT / "visual_evidence_v0_1"


def _json_default(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return str(value)


def _read_candidate(candidate_dir: Path) -> pd.DataFrame:
    glob = str(candidate_dir / "**" / "*.parquet").replace("\\", "/")
    frame = duckdb.sql(f"select * from read_parquet('{glob}', hive_partitioning=true)").fetchdf()
    frame["window_start_utc"] = pd.to_datetime(frame["window_start_utc"], utc=True)
    frame["window_end_utc"] = pd.to_datetime(frame["window_end_utc"], utc=True)
    if "window_role" not in frame.columns and "window_label" in frame.columns:
        frame["window_role"] = frame["window_label"]
    return frame.sort_values(["session_date", "ticker", "window_role", "event_window_id"]).reset_index(drop=True)


def _read_window_manifest(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame["event_time_utc"] = pd.to_datetime(frame["event_time_utc"], utc=True, errors="coerce")
    frame["window_start_utc"] = pd.to_datetime(frame["window_start_utc"], utc=True, errors="coerce")
    frame["window_end_utc"] = pd.to_datetime(frame["window_end_utc"], utc=True, errors="coerce")
    return frame


def _load_quotes(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    frame["ts_utc"] = pd.to_datetime(frame["timestamp"], unit="ns", utc=True, errors="coerce")
    frame = frame[(frame["ts_utc"] >= start) & (frame["ts_utc"] < end)].copy()
    for column in ["bid_price", "ask_price", "bid_size", "ask_size"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["mid"] = (frame["bid_price"] + frame["ask_price"]) / 2.0
    valid = frame["bid_price"].gt(0) & frame["ask_price"].gt(frame["bid_price"]) & frame["mid"].gt(0)
    frame["spread_bps"] = ((frame["ask_price"] - frame["bid_price"]) / frame["mid"] * 10_000.0).where(valid)
    frame["top_depth"] = (frame["bid_size"] + frame["ask_size"]).where(
        frame["bid_price"].gt(0) & frame["ask_price"].gt(0)
    )
    return frame


def _load_trades(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    frame["ts_utc"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    frame = frame[(frame["ts_utc"] >= start) & (frame["ts_utc"] < end)].copy()
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    frame["size"] = pd.to_numeric(frame["size"], errors="coerce")
    frame["dollar"] = (frame["price"] * frame["size"]).where(frame["price"].gt(0) & frame["size"].gt(0))
    return frame


def _downsample(frame: pd.DataFrame, limit: int) -> pd.DataFrame:
    if len(frame) <= limit:
        return frame
    step = max(len(frame) // limit, 1)
    return frame.iloc[::step].copy()


def _fmt_float(value: Any, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{float(value):,.{digits}f}"


def _fmt_int(value: Any) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{int(value):,}"


def _case_filename(index: int, row: pd.Series) -> str:
    ticker = str(row["ticker"]).lower()
    session = str(row["session_date"])[:10].replace("-", "_")
    role = str(row["window_role"]).lower()
    short_id = str(row["event_window_id"])[:10]
    return f"{index:02d}_{ticker}_{session}_{role}_{short_id}.png"


def _classify_case(row: pd.Series) -> tuple[str, str]:
    if not bool(row["source_quotes_file_present"]) or not bool(row["source_trades_file_present"]):
        return "review_missing_source", "missing quotes or trades source prevents strong interpretation."
    if str(row["window_role"]) == "pre_event_30m":
        return "pre_event_feature_candidate", "pre-event window is leakage-safe for feature review."
    return "same_session_context_candidate", "same-session window is useful context, not an ML pre-event feature."


def _render_case(
    *,
    index: int,
    row: pd.Series,
    window_row: pd.Series | None,
    images_dir: Path,
) -> dict[str, Any]:
    start = pd.Timestamp(row["window_start_utc"])
    end = pd.Timestamp(row["window_end_utc"])
    quotes_file = Path(str(row["source_quotes_file"]))
    trades_file = Path(str(row["source_trades_file"]))
    quotes = _load_quotes(quotes_file, start, end)
    trades = _load_trades(trades_file, start, end)
    event_time = None
    if window_row is not None and pd.notna(window_row.get("event_time_utc")):
        event_time = pd.Timestamp(window_row["event_time_utc"])

    image_name = _case_filename(index, row)
    image_path = images_dir / image_name
    case_bucket, case_reason = _classify_case(row)

    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True, constrained_layout=True)
    fig.suptitle(
        f"{row['ticker']} | {str(row['session_date'])[:10]} | {row['window_role']} | "
        f"quotes={_fmt_int(row['quotes_rows'])} trades={_fmt_int(row['trades_rows'])}",
        fontsize=13,
    )

    q_plot = _downsample(quotes, 5000)
    axes[0].plot(q_plot["ts_utc"], q_plot["bid_price"], color="#1f77b4", linewidth=0.75, label="bid")
    axes[0].plot(q_plot["ts_utc"], q_plot["ask_price"], color="#d62728", linewidth=0.75, label="ask")
    axes[0].set_ylabel("Quote price")
    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].grid(True, alpha=0.25)

    t_plot = _downsample(trades, 7000)
    size = t_plot["size"].fillna(0).clip(lower=1)
    size = (size / size.quantile(0.95) * 20).clip(lower=4, upper=28) if len(size) else size
    axes[1].scatter(t_plot["ts_utc"], t_plot["price"], s=size, alpha=0.35, color="#2ca02c", edgecolors="none")
    axes[1].set_ylabel("Trade price")
    axes[1].grid(True, alpha=0.25)

    spread = quotes[["ts_utc", "spread_bps"]].dropna()
    axes[2].plot(_downsample(spread, 5000)["ts_utc"], _downsample(spread, 5000)["spread_bps"], color="#7f3c8d", linewidth=0.8)
    if not trades.empty:
        bars = trades.set_index("ts_utc")["size"].resample("1min").sum().dropna()
        if not bars.empty:
            ax2 = axes[2].twinx()
            ax2.bar(bars.index, bars.values, width=0.00045, alpha=0.18, color="#ff7f0e", label="trade volume/min")
            ax2.set_ylabel("Volume/min")
    axes[2].set_ylabel("Spread bps")
    axes[2].grid(True, alpha=0.25)

    for ax in axes:
        ax.axvline(start, color="black", linewidth=0.8, linestyle="--", alpha=0.7)
        ax.axvline(end, color="black", linewidth=0.8, linestyle="--", alpha=0.7)
        if event_time is not None and start <= event_time <= end:
            ax.axvline(event_time, color="#e41a1c", linewidth=1.1, linestyle="-", alpha=0.8)
        ax.margins(x=0.01)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[-1].set_xlabel("UTC time")

    image_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(image_path, dpi=160)
    plt.close(fig)

    summary = {
        "case_index": index,
        "event_window_id": row["event_window_id"],
        "ticker": row["ticker"],
        "session_date": str(row["session_date"])[:10],
        "window_role": row["window_role"],
        "window_start_utc": start.isoformat(),
        "window_end_utc": end.isoformat(),
        "event_time_utc": event_time.isoformat() if event_time is not None else None,
        "image_path": str(image_path),
        "image_name": image_name,
        "case_bucket": case_bucket,
        "case_reason": case_reason,
        "quotes_rows": int(row["quotes_rows"]),
        "trades_rows": int(row["trades_rows"]),
        "quotes_crossed_rows": int(row["quotes_crossed_rows"]),
        "quotes_crossed_ratio_pct_all_rows": float(row["quotes_crossed_ratio_pct_all_rows"]),
        "quotes_spread_bps_median": float(row["quotes_spread_bps_median"]),
        "quotes_spread_bps_p90": float(row["quotes_spread_bps_p90"]),
        "trades_odd_lot_ratio_pct": float(row["trades_odd_lot_ratio_pct"]),
        "trades_duplicate_exact_ratio_pct": float(row["trades_duplicate_exact_ratio_pct"]),
        "trades_off_regular_session_ratio_pct": float(row["trades_off_regular_session_ratio_pct"]),
        "trades_total_volume": float(row["trades_total_volume"]),
        "trades_dollar_volume": float(row["trades_dollar_volume"]),
        "execution_sim_candidate": bool(row["execution_sim_candidate"]),
        "backtest_core_microstructure_candidate": bool(row["backtest_core_microstructure_candidate"]),
        "full_universe_claim": bool(row["full_universe_claim"]),
    }
    return summary


def _case_markdown(case: dict[str, Any], relative_image: str) -> str:
    role = case["window_role"]
    ml_text = (
        "La ventana `pre_event_30m` termina en el evento y es candidata a feature pre-evento."
        if role == "pre_event_30m"
        else "La ventana `same_session_regular` contiene contexto de sesion y puede incluir informacion posterior; no debe usarse como feature ML pre-evento."
    )
    crossed_text = (
        "No se observan crossed quotes en esta ventana."
        if case["quotes_crossed_rows"] == 0
        else f"Se observan {case['quotes_crossed_rows']} crossed quotes; deben mantenerse visibles como textura de review, aunque no rompen este candidato."
    )
    return f"""### Case {case['case_index']:02d} - `{case['ticker']}` `{case['session_date']}` `{role}`

![Case {case['case_index']:02d}]({relative_image})

**Lectura tecnica de la imagen.** El panel superior muestra best bid/best ask
durante la ventana candidata. El panel central muestra prints de trades con el
tamano relativo del punto escalado por `size`. El panel inferior combina spread
en bps y volumen negociado por minuto. Las lineas negras discontinuas marcan el
inicio y fin de la ventana; si la linea roja aparece dentro del panel, marca el
timestamp de evento.

**Interpretacion para el inspector.** {ml_text} En esta imagen hay
`{case['quotes_rows']:,}` quotes y `{case['trades_rows']:,}` trades. La mediana
del spread es `{_fmt_float(case['quotes_spread_bps_median'])}` bps y el p90 es
`{_fmt_float(case['quotes_spread_bps_p90'])}` bps. {crossed_text} En trades, el
odd-lot ratio es `{_fmt_float(case['trades_odd_lot_ratio_pct'])}%`, el duplicate
exact ratio es `{_fmt_float(case['trades_duplicate_exact_ratio_pct'])}%` y el
off-regular-session ratio es `{_fmt_float(case['trades_off_regular_session_ratio_pct'])}%`.

**Decision de consumo.** `execution_sim_candidate={case['execution_sim_candidate']}`,
`backtest_core_microstructure_candidate={case['backtest_core_microstructure_candidate']}`,
`full_universe_claim={case['full_universe_claim']}`. Esta evidencia sirve para
validar lectura forense del candidato, no para promocion institucional ni para
ML/RL primario.
"""


def build_visual_evidence(
    *,
    candidate_dir: Path,
    window_manifest: Path,
    output_root: Path,
    pack_dir: Path,
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    pack_dir.mkdir(parents=True, exist_ok=True)
    images_dir = pack_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    candidate = _read_candidate(candidate_dir)
    windows = _read_window_manifest(window_manifest)
    windows_by_id = {row["event_window_id"]: row for _, row in windows.iterrows()}

    cases = []
    for index, (_, row) in enumerate(candidate.iterrows(), start=1):
        cases.append(
            _render_case(
                index=index,
                row=row,
                window_row=windows_by_id.get(row["event_window_id"]),
                images_dir=images_dir,
            )
        )

    manifest = {
        "pack_id": "microstructure_candidate_visual_evidence_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_dir": str(candidate_dir),
        "window_manifest": str(window_manifest),
        "output_root": str(output_root),
        "pack_dir": str(pack_dir),
        "case_count": len(cases),
        "cases": cases,
        "status": "visual_forensic_candidate_evidence_only",
        "official_dataset_created": False,
        "full_universe_claim": False,
    }

    manifest_path = pack_dir / "microstructure_candidate_visual_manifest_v0_1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")

    lines = [
        "# Microstructure Candidate Visual Readout v0.1",
        "",
        "## Scope",
        "",
        "This readout is visual/forensic evidence for the 6-row `microstructure_features_table_v0_2_candidate` smoke artifact.",
        "",
        "It does not promote a new official dataset and it does not claim full-universe microstructure coverage.",
        "",
        "```text",
        f"candidate_dir = {candidate_dir}",
        f"window_manifest = {window_manifest}",
        f"case_count = {len(cases)}",
        "official_dataset_created = false",
        "full_universe_claim = false",
        "```",
        "",
        "## How To Read These Images",
        "",
        "Each image has three panels: bid/ask quote path, trade prints, and spread/volume texture. The purpose is to help a human inspector decide whether the candidate windows are understandable as microstructure state components.",
        "",
        "Important limitation: `D:/quotes` lineage is still provisional until the E-root quotes parity/authority work is complete.",
        "",
        "## Cases",
        "",
    ]

    for case in cases:
        relative = Path("visual_evidence_v0_1/images") / case["image_name"]
        lines.append(_case_markdown(case, relative.as_posix()))

    readout_path = output_root / "microstructure_candidate_visual_readout_v0_1.md"
    body = "\n".join(lines).replace("\n\n\n", "\n\n").rstrip() + "\n"
    readout_path.write_text(body, encoding="utf-8")

    readme_path = output_root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            "# Microstructure Features Inspection Dossier\n\n"
            "This folder stores visual/forensic inspection evidence for microstructure feature candidates.\n\n"
            "Current readout:\n\n"
            "- `microstructure_candidate_visual_readout_v0_1.md`\n",
            encoding="utf-8",
        )

    manifest["readout_path"] = str(readout_path)
    manifest["manifest_path"] = str(manifest_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build visual forensic evidence for microstructure candidate windows.")
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--window-manifest", type=Path, default=DEFAULT_WINDOW_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK_DIR)
    args = parser.parse_args()

    manifest = build_visual_evidence(
        candidate_dir=args.candidate_dir,
        window_manifest=args.window_manifest,
        output_root=args.output_root,
        pack_dir=args.pack_dir,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "case_count": manifest["case_count"],
                "readout_path": manifest["readout_path"],
                "manifest_path": manifest["manifest_path"],
                "pack_dir": manifest["pack_dir"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
