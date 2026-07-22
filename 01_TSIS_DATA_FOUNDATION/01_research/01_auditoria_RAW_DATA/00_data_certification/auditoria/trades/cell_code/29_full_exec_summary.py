from __future__ import annotations

import numpy as np
import pandas as pd


def build_exec_summary_full(full_current: pd.DataFrame, hard_issue_counts_full: pd.DataFrame, issue_evidence_full: pd.DataFrame):
    hard_total_full = int((full_current["severity"] == "HARD_FAIL").sum())
    top_issue_files_full = int(hard_issue_counts_full.iloc[0]["files"]) if not hard_issue_counts_full.empty else 0
    top_issue_name_full = hard_issue_counts_full.iloc[0]["issue"] if not hard_issue_counts_full.empty else None
    top_issue_row_full = issue_evidence_full.iloc[0].to_dict() if not issue_evidence_full.empty else {}

    exec_summary_full = pd.DataFrame([
        {
            "selected_files": int(len(full_current)),
            "pass_rate_pct": round(100.0 * (full_current["severity"] == "PASS").mean(), 3),
            "soft_fail_rate_pct": round(100.0 * (full_current["severity"] == "SOFT_FAIL").mean(), 3),
            "hard_fail_rate_pct": round(100.0 * (full_current["severity"] == "HARD_FAIL").mean(), 3),
            "top_hard_issue": top_issue_name_full,
            "top_hard_issue_files": top_issue_files_full,
            "top_hard_issue_pct_of_hard": round(100.0 * top_issue_files_full / max(hard_total_full, 1), 3),
            "top_hard_issue_tickers": int(top_issue_row_full.get("tickers", 0)),
            "top_hard_issue_dates": int(top_issue_row_full.get("dates", 0)),
            "top_hard_issue_has_1m_warn_pct": round(float(top_issue_row_full.get("has_1m_warn_pct", np.nan)), 3),
            "top_hard_issue_median_vol_vs_daily": round(float(top_issue_row_full.get("median_vol_vs_daily", np.nan)), 3),
            "top_hard_issue_median_vol_vs_1m": round(float(top_issue_row_full.get("median_vol_vs_1m", np.nan)), 3),
        }
    ])

    readout_md = (
        "**Lectura rapida**\n\n"
        f"- El full tiene `PASS` residual y esta dominado por `SOFT_FAIL` + `HARD_FAIL`.\n"
        f"- El `HARD_FAIL` dominante es `{top_issue_name_full}` y explica la mayor parte del residuo duro.\n"
        "- Ese issue no esta concentrado en pocos outliers: aparece en cientos de tickers y miles de fechas.\n"
        "- La confirmacion por `1m` y los ratios de volumen sugieren que el residuo dominante es un problema real de referencia/escala, no ruido aislado."
    )
    return exec_summary_full, readout_md
