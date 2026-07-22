"""Audit scanner denominator outputs for EXP_DAS_FRONTSIDE_DISCOVERY_0002.

This audit freezes the interpretation of a scanner denominator run:
scanner candidates are not DAS-good cases and not strategy outcomes. They are
the operational population captured by a declared scanner configuration.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
AUDIT_ID = "audit_scanner_denominator_v0_1"
DEFAULT_RUN_ROOT = Path(
    r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def value_counts(df: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in df.columns:
        return {"__missing_column__": 0}
    out = df[column].fillna("__NA__").astype(str).value_counts(dropna=False).to_dict()
    return {str(k): int(v) for k, v in out.items()}


def numeric_summary(df: pd.DataFrame, column: str) -> dict[str, float | None]:
    if column not in df.columns:
        return {"min": None, "p25": None, "median": None, "p75": None, "max": None}
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    if s.empty:
        return {"min": None, "p25": None, "median": None, "p75": None, "max": None}
    q = s.quantile([0, 0.25, 0.5, 0.75, 1.0]).to_dict()
    return {
        "min": float(q[0.0]),
        "p25": float(q[0.25]),
        "median": float(q[0.5]),
        "p75": float(q[0.75]),
        "max": float(q[1.0]),
    }


def skipped_reason_summary(manifest: dict) -> dict[str, int]:
    skipped = manifest.get("skipped_files") or []
    reasons: Counter[str] = Counter()
    for item in skipped:
        text = str(item)
        if ": " in text:
            reason = text.rsplit(": ", 1)[-1]
        else:
            reason = "unknown"
        reasons[reason] += 1
    return dict(sorted(reasons.items()))


def write_table(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def build_audit(run_root: Path, output_dir: Path | None) -> dict:
    outputs = run_root / "outputs"
    denominator_path = outputs / "scanner_2026_qg_full_universe_denominator_v0_2.parquet"
    manifest_path = outputs / "scanner_2026_qg_full_universe_run_manifest_v0_2.json"
    progress_path = outputs / "scanner_2026_qg_full_universe_progress_v0_2.json"

    if not denominator_path.exists():
        raise FileNotFoundError(f"Missing denominator parquet: {denominator_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing run manifest: {manifest_path}")

    output_dir = output_dir or (run_root / "audit")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(denominator_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    progress = json.loads(progress_path.read_text(encoding="utf-8-sig")) if progress_path.exists() else {}

    key_cols = [c for c in ["ticker", "session_date"] if c in df.columns]
    duplicate_rows = pd.DataFrame()
    duplicate_key_count = 0
    if len(key_cols) == 2 and not df.empty:
        dup_mask = df.duplicated(key_cols, keep=False)
        duplicate_rows = df.loc[dup_mask].sort_values(key_cols)
        duplicate_key_count = int(df.duplicated(key_cols).sum())
        duplicate_rows.to_csv(output_dir / "denominator_duplicate_ticker_session_rows_v0_1.csv", index=False)

    count_tables = {
        "market_cap_source_state": value_counts(df, "market_cap_source_state"),
        "market_cap_gate_state": value_counts(df, "market_cap_gate_state"),
        "price_gate_state": value_counts(df, "price_gate_state"),
        "volume_gate_state": value_counts(df, "volume_gate_state"),
        "threshold_gate_state": value_counts(df, "threshold_gate_state"),
        "quote_guarded_repair_applied_at_gate": value_counts(df, "quote_guarded_repair_applied_at_gate"),
        "repair_state_at_gate": value_counts(df, "repair_state_at_gate"),
    }

    count_rows = []
    for column, counts in count_tables.items():
        for value, count in counts.items():
            count_rows.append({"column": column, "value": value, "count": count})
    write_table(output_dir / "denominator_gate_and_state_counts_v0_1.csv", count_rows)

    sample_cols = [
        "ticker",
        "session_date",
        "scanner_gate_ts_et",
        "scanner_gate_price",
        "scanner_gate_prior_close_pct",
        "scanner_gate_accumulated_volume",
        "market_cap",
        "market_cap_source_state",
        "market_cap_gate_state",
        "quote_guarded_repair_applied_at_gate",
    ]
    sample_cols = [c for c in sample_cols if c in df.columns]
    df[sample_cols].head(50).to_csv(output_dir / "denominator_first_50_candidates_v0_1.csv", index=False)

    audit = {
        "audit_id": AUDIT_ID,
        "created_utc": utc_now(),
        "experiment_id": EXPERIMENT_ID,
        "run_root": str(run_root),
        "denominator_path": str(denominator_path),
        "manifest_path": str(manifest_path),
        "progress_path": str(progress_path) if progress_path.exists() else None,
        "interpretation": {
            "scanner_candidates_are_denominator": True,
            "scanner_candidates_are_das_good_cases": False,
            "scanner_candidates_are_strategy_outcomes": False,
            "valid_conclusion_scope": "behavior conditioned on this declared scanner configuration",
        },
        "row_counts": {
            "denominator_rows": int(len(df)),
            "unique_tickers": int(df["ticker"].nunique()) if "ticker" in df.columns else None,
            "unique_sessions": int(df["session_date"].nunique()) if "session_date" in df.columns else None,
            "duplicate_ticker_session_extra_rows": duplicate_key_count,
        },
        "run_counts": {
            "qg_files_seen": int(manifest.get("qg_files_seen", 0)),
            "qg_files_read": int(manifest.get("qg_files_read", 0)),
            "skipped_files": len(manifest.get("skipped_files") or []),
            "repair_applied_rows_seen": int(manifest.get("repair_applied_rows_seen", 0)),
            "candidates_emitted": int(manifest.get("candidates_emitted", 0)),
            "progress_status": progress.get("status"),
        },
        "config": manifest.get("config", {}),
        "state_counts": count_tables,
        "numeric_summary": {
            "scanner_gate_prior_close_pct": numeric_summary(df, "scanner_gate_prior_close_pct"),
            "scanner_gate_accumulated_volume": numeric_summary(df, "scanner_gate_accumulated_volume"),
            "scanner_gate_price": numeric_summary(df, "scanner_gate_price"),
            "market_cap": numeric_summary(df, "market_cap"),
        },
        "skipped_reason_summary": skipped_reason_summary(manifest),
        "next_step": "build anchors for every denominator row: scanner_gate, first_push_high, first_dip_low, rebreak/fake/no_rebreak",
    }

    (output_dir / "denominator_audit_v0_1.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [
        "# Denominator Audit v0.1",
        "",
        f"created_utc: `{audit['created_utc']}`",
        f"experiment_id: `{EXPERIMENT_ID}`",
        "",
        "## Lectura Correcta",
        "",
        "Estos candidatos son el denominador operativo que el scanner habria cazado bajo una configuracion declarada.",
        "No son casos buenos DAS, no son entradas validas y no son outcomes de estrategia.",
        "",
        "La conclusion permitida queda condicionada a este scanner:",
        "",
        "```text",
        "universo 1m quote-guarded 2026",
        "-> scanner +50% vs prior_close + volumen + precio + market cap",
        "-> candidatos capturados",
        "-> despues se estudia si hay estructura DAS / in-play / continuation / failure",
        "```",
        "",
        "## Counts",
        "",
        f"- denominator_rows: `{audit['row_counts']['denominator_rows']}`",
        f"- unique_tickers: `{audit['row_counts']['unique_tickers']}`",
        f"- unique_sessions: `{audit['row_counts']['unique_sessions']}`",
        f"- duplicate_ticker_session_extra_rows: `{audit['row_counts']['duplicate_ticker_session_extra_rows']}`",
        f"- qg_files_seen: `{audit['run_counts']['qg_files_seen']}`",
        f"- qg_files_read: `{audit['run_counts']['qg_files_read']}`",
        f"- skipped_files: `{audit['run_counts']['skipped_files']}`",
        f"- repair_applied_rows_seen: `{audit['run_counts']['repair_applied_rows_seen']}`",
        "",
        "## Configuracion Del Scanner",
        "",
        "```json",
        json.dumps(audit["config"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Market Cap / Gates / Repair State",
        "",
        "Ver `denominator_gate_and_state_counts_v0_1.csv` para el desglose columna-valor.",
        "",
        "## Distribuciones Basicas",
        "",
        "```json",
        json.dumps(audit["numeric_summary"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Skipped Files",
        "",
        "```json",
        json.dumps(audit["skipped_reason_summary"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Siguiente Paso",
        "",
        "Construir anchors para cada fila del denominador y generar paquete visual de inspeccion.",
        "",
        "```text",
        "scanner_gate -> first_push_high -> first_dip_low -> rebreak/fake/no_rebreak",
        "```",
    ]
    (output_dir / "denominator_audit_v0_1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    audit = build_audit(args.run_root, args.output_dir)
    print(json.dumps({"audit_id": audit["audit_id"], "rows": audit["row_counts"]["denominator_rows"], "output_dir": str(Path(audit["run_root"]) / "audit")}, indent=2))
