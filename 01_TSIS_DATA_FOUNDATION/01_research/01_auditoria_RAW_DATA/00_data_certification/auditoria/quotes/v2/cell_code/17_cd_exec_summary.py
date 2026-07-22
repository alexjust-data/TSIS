from __future__ import annotations

import pandas as pd


def build_exec_summary_cd(df: pd.DataFrame, hard_issue_counts: pd.DataFrame, warn_counts: pd.DataFrame, taxonomy_summary: pd.DataFrame):
    top_hard = hard_issue_counts.iloc[0]["issue"] if not hard_issue_counts.empty else None
    top_warn = warn_counts.iloc[0]["warn"] if not warn_counts.empty else None
    top_tax = taxonomy_summary.iloc[0]["taxonomy"] if not taxonomy_summary.empty else None

    if len(df) == 1 and "rows_total" in df.columns:
        base = df.iloc[0]
        out = {
            "rows_total": int(base.get("rows_total", 0)),
            "hard_fail_files": int(base.get("hard_fail_files", 0)),
            "soft_fail_files": int(base.get("soft_fail_files", 0)),
            "pass_files": int(base.get("pass_files", 0)),
            "top_hard_issue": top_hard,
            "top_warn": top_warn,
            "top_taxonomy": top_tax,
            "hard_fail_rate_pct": float(base.get("hard_fail_rate_pct", 0.0)),
            "soft_fail_rate_pct": float(base.get("soft_fail_rate_pct", 0.0)),
            "timestamp_shift_rate_pct": float(base.get("timestamp_shift_rate_pct", 0.0)),
            "crossed_ratio_p99_pct": float(base.get("crossed_ratio_p99_pct", 0.0)),
        }
    else:
        out = {
            "rows_total": int(len(df)),
            "hard_fail_files": int(df["severity"].eq("HARD_FAIL").sum()),
            "soft_fail_files": int(df["severity"].eq("SOFT_FAIL").sum()),
            "pass_files": int(df["severity"].eq("PASS").sum()),
            "top_hard_issue": top_hard,
            "top_warn": top_warn,
            "top_taxonomy": top_tax,
            "hard_fail_rate_pct": float(df["severity"].eq("HARD_FAIL").mean() * 100.0),
            "soft_fail_rate_pct": float(df["severity"].eq("SOFT_FAIL").mean() * 100.0),
            "timestamp_shift_rate_pct": float(df["m.timestamp_out_of_partition_day"].fillna(False).mean() * 100.0),
            "crossed_ratio_p99_pct": float(df["m.crossed_ratio_pct"].fillna(0).quantile(0.99)),
        }

    summary = pd.DataFrame([out])

    md = f"""
### Lectura ejecutiva

- El `current` final `quotes C + D` contiene `{out["rows_total"]:,}` files con `HARD_FAIL` `{out["hard_fail_rate_pct"]:.2f}%` y `SOFT_FAIL` `{out["soft_fail_rate_pct"]:.2f}%`.
- El issue duro dominante es `{top_hard}` y el warning dominante es `{top_warn}`.
- La taxonomía principal queda en `{top_tax}`, lo que indica que el residuo no está repartido al azar sino concentrado en familias operativas repetibles.
- `timestamp_out_of_partition_day` aparece en `{out["timestamp_shift_rate_pct"]:.2f}%` del universo y pesa mucho más en `SOFT_FAIL` que en `HARD_FAIL`.
- El `p99` de `crossed_ratio_pct` está en `{out["crossed_ratio_p99_pct"]:.2f}%`, así que además del ruido micro hay una cola dura de files claramente deteriorados.
"""
    return summary, md
