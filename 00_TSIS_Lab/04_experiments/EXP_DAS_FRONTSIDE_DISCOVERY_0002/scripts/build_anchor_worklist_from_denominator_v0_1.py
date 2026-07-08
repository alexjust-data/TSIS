"""Build anchor worklist from scanner denominator for EXP_DAS_FRONTSIDE_DISCOVERY_0002.

The worklist is the controlled handoff from scanner denominator to anchor
builders. It does not detect DAS structure yet; it freezes which ticker/session
cases must be inspected and which 1m source file each case uses.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_anchor_worklist_from_denominator_v0_1"
DEFAULT_RUN_ROOT = Path(
    r"C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_worklist(run_root: Path, output_dir: Path | None) -> dict:
    outputs = run_root / "outputs"
    denominator_path = outputs / "scanner_2026_qg_full_universe_denominator_v0_2.parquet"
    if not denominator_path.exists():
        raise FileNotFoundError(f"Missing denominator parquet: {denominator_path}")

    output_dir = output_dir or (run_root / "anchor_worklist")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(denominator_path).copy()
    required = [
        "ticker",
        "session_date",
        "scanner_gate_ts_utc",
        "scanner_gate_ts_et",
        "scanner_gate_price",
        "scanner_gate_prior_close_pct",
        "scanner_gate_accumulated_volume",
        "source_input_1m_file",
        "source_input_1m_dataset",
        "source_input_1m_root",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Denominator missing required columns: {missing}")

    df = df.sort_values(["session_date", "ticker", "scanner_gate_ts_utc"]).reset_index(drop=True)
    df.insert(0, "anchor_worklist_id", [f"DASFRONT2026_{i:04d}" for i in range(1, len(df) + 1)])
    df["anchor_builder_status"] = "pending_anchor_detection"
    df["visual_audit_required"] = True
    df["scanner_candidate_is_denominator"] = True
    df["scanner_candidate_is_das_good_case"] = False
    df["scanner_candidate_is_inplay"] = False
    df["anchor_detection_input_state"] = "ready_from_scanner_denominator"
    df["created_utc"] = utc_now()

    df["source_input_1m_file_exists"] = df["source_input_1m_file"].map(lambda p: Path(str(p)).exists())
    df["source_input_1m_file_missing_reason"] = df["source_input_1m_file_exists"].map(
        lambda ok: None if ok else "missing_source_input_1m_file"
    )

    parquet_path = output_dir / "anchor_worklist_from_denominator_v0_1.parquet"
    csv_path = output_dir / "anchor_worklist_from_denominator_v0_1.csv"
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)

    summary = {
        "builder_id": BUILDER_ID,
        "experiment_id": EXPERIMENT_ID,
        "created_utc": utc_now(),
        "run_root": str(run_root),
        "denominator_path": str(denominator_path),
        "output_dir": str(output_dir),
        "rows": int(len(df)),
        "unique_tickers": int(df["ticker"].nunique()),
        "unique_sessions": int(df["session_date"].nunique()),
        "source_input_1m_files_missing": int((~df["source_input_1m_file_exists"]).sum()),
        "market_cap_source_state_counts": df.get("market_cap_source_state", pd.Series(dtype=str)).fillna("__NA__").astype(str).value_counts().to_dict(),
        "next_step": "detect anchors: first_push_high, first_dip_low, rebreak/fake/no_rebreak, then visual audit",
    }
    (output_dir / "anchor_worklist_summary_v0_1.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Anchor Worklist From Denominator v0.1",
        "",
        f"created_utc: `{summary['created_utc']}`",
        f"builder_id: `{BUILDER_ID}`",
        "",
        "## Lectura Correcta",
        "",
        "Esta worklist no detecta DAS todavia. Solo congela los casos que deben pasar a deteccion de anchors.",
        "",
        "```text",
        "scanner denominator row -> anchor worklist row -> anchor builder -> visual audit -> outcomes",
        "```",
        "",
        "## Counts",
        "",
        f"- rows: `{summary['rows']}`",
        f"- unique_tickers: `{summary['unique_tickers']}`",
        f"- unique_sessions: `{summary['unique_sessions']}`",
        f"- source_input_1m_files_missing: `{summary['source_input_1m_files_missing']}`",
        "",
        "## Next",
        "",
        "Construir anchors para cada caso:",
        "",
        "```text",
        "scanner_gate",
        "first_push_high",
        "first_dip_low",
        "rebreak_confirmed / fake_rebreak / no_rebreak",
        "```",
    ]
    (output_dir / "anchor_worklist_summary_v0_1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    summary = build_worklist(args.run_root, args.output_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
