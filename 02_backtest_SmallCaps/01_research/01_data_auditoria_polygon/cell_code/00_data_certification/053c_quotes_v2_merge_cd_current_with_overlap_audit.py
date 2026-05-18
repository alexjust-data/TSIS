from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Parquet not found: {path}")
    return pd.read_parquet(path)


def maybe_load_df(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()


def prepare_for_write(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    for col in ["date", "date_inventory", "processed_at_utc", "current_as_of_utc", "mtime_utc"]:
        if col in out.columns:
            out[col] = out[col].map(
                lambda value: (
                    value.isoformat()
                    if hasattr(value, "isoformat")
                    else ("" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value))
                )
            )
    for col in ["issues", "warns", "metrics_json"]:
        if col in out.columns:
            out[col] = out[col].map(
                lambda value: value
                if isinstance(value, str)
                else (
                    ""
                    if value is None or (isinstance(value, float) and pd.isna(value))
                    else json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
                )
            )
    return out


def severity_rank(value: Any) -> int:
    mapping = {"PASS": 0, "SOFT_FAIL": 1, "HARD_FAIL": 2}
    return mapping.get(str(value), 99)


def issue_count(value: Any) -> int:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    if isinstance(value, list):
        return len(value)
    if isinstance(value, str):
        if not value.strip():
            return 0
        try:
            parsed = json.loads(value)
            return len(parsed) if isinstance(parsed, list) else 1
        except Exception:
            return 1
    return 1


def action_rank(value: Any) -> int:
    text = str(value or "").upper()
    mapping = {
        "KEEP_CURRENT": 0,
        "KEEP_EXISTING": 0,
        "PASS": 0,
        "RETRY": 1,
        "REQUEUE": 1,
        "FREEZE": 2,
        "QUARANTINE": 3,
    }
    return mapping.get(text, 9)


def choose_overlap_row(d_row: pd.Series, c_row: pd.Series) -> tuple[str, str]:
    d_sev = severity_rank(d_row.get("severity"))
    c_sev = severity_rank(c_row.get("severity"))
    if d_sev != c_sev:
        return ("D", "lower_severity" if d_sev < c_sev else "C_lower_severity")

    d_issues = issue_count(d_row.get("issues")) + issue_count(d_row.get("warns"))
    c_issues = issue_count(c_row.get("issues")) + issue_count(c_row.get("warns"))
    if d_issues != c_issues:
        return ("D", "fewer_issues_warns" if d_issues < c_issues else "C_fewer_issues_warns")

    d_action = action_rank(d_row.get("action"))
    c_action = action_rank(c_row.get("action"))
    if d_action != c_action:
        return ("D", "better_action_rank" if d_action < c_action else "C_better_action_rank")

    comparable_cols = [
        "rows",
        "severity",
        "issues",
        "warns",
        "action",
        "metrics_json",
        "validator_version",
        "validation_kind",
    ]
    identical = True
    for col in comparable_cols:
        dv = d_row.get(col)
        cv = c_row.get(col)
        if isinstance(dv, float) and pd.isna(dv):
            dv = None
        if isinstance(cv, float) and pd.isna(cv):
            cv = None
        if dv != cv:
            identical = False
            break
    if identical:
        return ("D", "identical_prefer_D")
    return ("D", "tie_prefer_D")


def build_overlap_decisions(d_current: pd.DataFrame, c_current: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    d = d_current.copy()
    c = c_current.copy()
    d["task_key"] = d["task_key"].astype(str)
    c["task_key"] = c["task_key"].astype(str)

    overlap_keys = sorted(set(d["task_key"]) & set(c["task_key"]))
    rows: list[dict[str, Any]] = []
    for key in overlap_keys:
        d_row = d.loc[d["task_key"] == key].iloc[0]
        c_row = c.loc[c["task_key"] == key].iloc[0]
        winner, reason = choose_overlap_row(d_row, c_row)
        rows.append(
            {
                "task_key": key,
                "ticker": d_row.get("ticker") or c_row.get("ticker"),
                "date": str(d_row.get("date") or c_row.get("date")),
                "d_file": d_row.get("file"),
                "c_file": c_row.get("file"),
                "d_severity": d_row.get("severity"),
                "c_severity": c_row.get("severity"),
                "d_action": d_row.get("action"),
                "c_action": c_row.get("action"),
                "winner": winner,
                "decision_reason": reason,
            }
        )
    return pd.DataFrame(rows), overlap_keys


def filter_retry_by_current(retry_df: pd.DataFrame, current_df: pd.DataFrame) -> pd.DataFrame:
    if retry_df.empty or current_df.empty or "task_key" not in retry_df.columns:
        return retry_df.copy()
    keep = set(current_df["task_key"].astype(str))
    out = retry_df.copy()
    out["task_key"] = out["task_key"].astype(str)
    return out[out["task_key"].isin(keep)].copy()


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge quotes D current + C current with overlap audit and deterministic winner selection")
    ap.add_argument("--d-current-dir", required=True)
    ap.add_argument("--c-current-dir", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    d_dir = Path(args.d_current_dir)
    c_dir = Path(args.c_current_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    d_current = load_df(d_dir / "quotes_current.parquet")
    c_current = load_df(c_dir / "quotes_current.parquet")
    d_retry = maybe_load_df(d_dir / "retry_current.parquet")
    c_retry = maybe_load_df(c_dir / "retry_current.parquet")

    overlap_decisions, overlap_keys = build_overlap_decisions(d_current, c_current)
    overlap_key_set = set(overlap_keys)
    winner_map = (
        overlap_decisions.set_index("task_key")["winner"].to_dict() if not overlap_decisions.empty else {}
    )

    d_non_overlap = d_current[~d_current["task_key"].astype(str).isin(overlap_key_set)].copy()
    c_non_overlap = c_current[~c_current["task_key"].astype(str).isin(overlap_key_set)].copy()
    d_overlap = d_current[d_current["task_key"].astype(str).isin(overlap_key_set)].copy()
    c_overlap = c_current[c_current["task_key"].astype(str).isin(overlap_key_set)].copy()

    d_winners = d_overlap[d_overlap["task_key"].astype(str).map(lambda key: winner_map.get(key) == "D")].copy()
    c_winners = c_overlap[c_overlap["task_key"].astype(str).map(lambda key: winner_map.get(key) == "C")].copy()

    merged_current = pd.concat([d_non_overlap, c_non_overlap, d_winners, c_winners], ignore_index=True)
    merged_current["task_key"] = merged_current["task_key"].astype(str)

    d_retry_kept = filter_retry_by_current(d_retry, pd.concat([d_non_overlap, d_winners], ignore_index=True))
    c_retry_kept = filter_retry_by_current(c_retry, pd.concat([c_non_overlap, c_winners], ignore_index=True))
    merged_retry = pd.concat([df for df in [d_retry_kept, c_retry_kept] if not df.empty], ignore_index=True) if (not d_retry_kept.empty or not c_retry_kept.empty) else pd.DataFrame()

    dup_task_keys = int(merged_current["task_key"].duplicated().sum())
    dup_files = int(merged_current["file"].astype(str).duplicated().sum())

    verification = {
        "merged_at_utc": utc_now(),
        "d_current_dir": str(d_dir),
        "c_current_dir": str(c_dir),
        "outdir": str(outdir),
        "d_current_rows": int(len(d_current)),
        "c_current_rows": int(len(c_current)),
        "overlap_task_keys": int(len(overlap_keys)),
        "overlap_rows_d": int(len(d_overlap)),
        "overlap_rows_c": int(len(c_overlap)),
        "overlap_winners_d": int(len(d_winners)),
        "overlap_winners_c": int(len(c_winners)),
        "merged_current_rows": int(len(merged_current)),
        "merged_current_task_keys": int(merged_current["task_key"].nunique()),
        "merged_current_files": int(merged_current["file"].astype(str).nunique()),
        "duplicate_task_key_rows": dup_task_keys,
        "duplicate_file_rows": dup_files,
        "retry_rows": int(len(merged_retry)),
        "verification_passed": bool(
            dup_task_keys == 0
            and dup_files == 0
            and len(merged_current) == merged_current["task_key"].nunique()
            and len(merged_current) == merged_current["file"].astype(str).nunique()
        ),
    }

    overlap_decisions.to_csv(outdir / "quotes_cd_overlap_audit.csv", index=False)
    prepare_for_write(merged_current).to_parquet(outdir / "quotes_current.parquet", index=False)
    prepare_for_write(merged_current).to_csv(outdir / "quotes_current.csv", index=False)
    prepare_for_write(merged_retry).to_parquet(outdir / "retry_current.parquet", index=False)
    prepare_for_write(merged_retry).to_csv(outdir / "retry_current.csv", index=False)
    write_json(outdir / "merge_verification_summary.json", verification)

    if not verification["verification_passed"]:
        raise ValueError(json.dumps(verification, indent=2))

    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
