from __future__ import annotations

import argparse
import math
import json
import random
import runpy
import time
from collections import Counter
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


CURRENT_PARQUET_CD = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
)
DEFAULT_CACHE_DIR = (
    CURRENT_PARQUET_CD.parent / "root_cause_exports" / "notebook_cd_cache"
)


def _utcnow_iso() -> str:
    return pd.Timestamp.now("UTC").isoformat()


def _load_modules(base_dir: Path) -> dict[str, dict]:
    return {
        "mod00": runpy.run_path(str(base_dir / "00_load_trades_run_artifacts.py")),
        "mod40": runpy.run_path(str(base_dir / "40_cd_run_snapshot.py")),
        "mod43": runpy.run_path(str(base_dir / "43_cd_quirurgical_diagnostics.py")),
        "mod45": runpy.run_path(str(base_dir / "45_cd_exec_summary.py")),
        "mod46": runpy.run_path(str(base_dir / "46_cd_break_overview.py")),
        "mod47": runpy.run_path(str(base_dir / "47_cd_break_bands.py")),
        "mod48": runpy.run_path(str(base_dir / "48_cd_taxonomy.py")),
        "mod49": runpy.run_path(str(base_dir / "49_cd_taxonomy_side.py")),
        "mod53": runpy.run_path(str(base_dir / "53_cd_band_cross_analysis.py")),
        "mod51": runpy.run_path(str(base_dir / "51_cd_final_bucket.py")),
        "mod55": runpy.run_path(str(base_dir / "55_cd_taxonomy_side_table.py")),
    }


def _iter_batches(handle, columns: list[str], batch_size: int, max_batches: int | None = None, normalize: bool = False) -> Iterator[pd.DataFrame]:
    for idx, df in enumerate(handle.stream(columns=columns, batch_size=batch_size, normalize=normalize)):
        if max_batches is not None and idx >= max_batches:
            break
        yield df


def _iter_batches_with_progress(
    handle,
    columns: list[str],
    batch_size: int,
    stage_name: str,
    max_batches: int | None = None,
    normalize: bool = False,
) -> Iterator[pd.DataFrame]:
    total_rows = int(handle.row_count())
    total_batches = math.ceil(total_rows / batch_size) if batch_size > 0 else 0
    if max_batches is not None:
        total_batches = min(total_batches, int(max_batches))
        total_rows = min(total_rows, int(total_batches * batch_size))

    stage_start = time.perf_counter()
    processed_rows = 0

    print(
        json.dumps(
            {
                "ts": _utcnow_iso(),
                "stage": stage_name,
                "event": "start",
                "batch_size": batch_size,
                "total_batches": total_batches,
                "total_rows_target": total_rows,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    for idx, df in enumerate(handle.stream(columns=columns, batch_size=batch_size, normalize=normalize), start=1):
        if max_batches is not None and idx > max_batches:
            break
        processed_rows += len(df)
        remaining_rows = max(total_rows - processed_rows, 0)
        elapsed = time.perf_counter() - stage_start
        rate = processed_rows / elapsed if elapsed > 0 else 0.0
        eta_sec = remaining_rows / rate if rate > 0 else None
        print(
            json.dumps(
                {
                    "ts": _utcnow_iso(),
                    "stage": stage_name,
                    "event": "progress",
                    "batch": idx,
                    "total_batches": total_batches,
                    "processed_rows": processed_rows,
                    "remaining_rows": remaining_rows,
                    "pct_rows": round(100.0 * processed_rows / max(total_rows, 1), 3),
                    "elapsed_sec": round(elapsed, 3),
                    "eta_sec": round(eta_sec, 3) if eta_sec is not None else None,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        yield df

    print(
        json.dumps(
            {
                "ts": _utcnow_iso(),
                "stage": stage_name,
                "event": "end",
                "processed_rows": processed_rows,
                "elapsed_sec": round(time.perf_counter() - stage_start, 3),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


def _write_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def _update_reservoir(sample: list[dict], row: dict, seen: int, max_size: int, rng: random.Random) -> None:
    if max_size <= 0:
        return
    if len(sample) < max_size:
        sample.append(row)
        return
    j = rng.randint(0, seen - 1)
    if j < max_size:
        sample[j] = row


def _coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def build_snapshot_artifacts(handle, mod40: dict, current_parquet: Path) -> dict[str, pd.DataFrame]:
    sev_counts_cd, snapshot_cd, batch_mix_cd, batch_rate_roll50_cd = mod40["summarize_cd_snapshot_chunked"](current_parquet)
    return {
        "severity_counts_cd": sev_counts_cd,
        "snapshot_cd": snapshot_cd,
        "batch_mix_cd": batch_mix_cd,
        "batch_rate_roll50_cd": batch_rate_roll50_cd,
    }


def build_root_cause_artifacts(handle, mod00: dict, batch_size: int, sample_size_per_issue: int, top_n_issue_evidence: int, max_batches: int | None = None) -> dict[str, pd.DataFrame]:
    parse_listish = mod00["parse_listish"]
    flatten_tokens = mod00["flatten_tokens"]
    parse_dictish = mod00["parse_dictish"]

    warn_counter: Counter[str] = Counter()
    hard_issue_counter: Counter[str] = Counter()

    for df in _iter_batches_with_progress(handle, ["severity", "issues", "warns"], batch_size=batch_size, max_batches=max_batches, stage_name="root_cause_counts"):
        df["issues_list"] = df["issues"].map(lambda x: flatten_tokens([parse_listish(x)]))
        df["warns_list"] = df["warns"].map(lambda x: flatten_tokens([parse_listish(x)]))
        warn_counter.update(tok for xs in df["warns_list"].tolist() for tok in xs)
        hard_issue_counter.update(
            tok
            for xs in df.loc[df["severity"] == "HARD_FAIL", "issues_list"].tolist()
            for tok in xs
        )

    hard_issue_counts_cd = (
        pd.DataFrame([{"issue": k, "files": v} for k, v in hard_issue_counter.items()])
        .sort_values(["files", "issue"], ascending=[False, True])
        .reset_index(drop=True)
        if hard_issue_counter
        else pd.DataFrame(columns=["issue", "files"])
    )
    warn_counts_cd = (
        pd.DataFrame([{"warn": k, "files": v} for k, v in warn_counter.items()])
        .sort_values(["files", "warn"], ascending=[False, True])
        .reset_index(drop=True)
        if warn_counter
        else pd.DataFrame(columns=["warn", "files"])
    )

    focus_issues = hard_issue_counts_cd.head(top_n_issue_evidence)["issue"].tolist()
    if not focus_issues:
        return {
            "hard_issue_counts_cd": hard_issue_counts_cd,
            "warn_counts_cd": warn_counts_cd,
            "issue_evidence_cd": pd.DataFrame(),
        }

    rng = random.Random(7)
    issue_stats = {
        issue: {
            "files": 0,
            "tickers": set(),
            "dates": set(),
            "has_1m_warn_count": 0,
            "metric_seen": {
                "m.off_session_trade_pct": 0,
                "m.duplicate_excess_ratio_pct": 0,
                "m.trade_volume_vs_daily_ratio": 0,
                "m.trade_volume_vs_1m_ratio": 0,
            },
            "metric_samples": {
                "m.off_session_trade_pct": [],
                "m.duplicate_excess_ratio_pct": [],
                "m.trade_volume_vs_daily_ratio": [],
                "m.trade_volume_vs_1m_ratio": [],
            },
        }
        for issue in focus_issues
    }
    metric_keys = [
        "off_session_trade_pct",
        "duplicate_excess_ratio_pct",
        "trade_volume_vs_daily_ratio",
        "trade_volume_vs_1m_ratio",
    ]
    metric_map = {
        "off_session_trade_pct": "m.off_session_trade_pct",
        "duplicate_excess_ratio_pct": "m.duplicate_excess_ratio_pct",
        "trade_volume_vs_daily_ratio": "m.trade_volume_vs_daily_ratio",
        "trade_volume_vs_1m_ratio": "m.trade_volume_vs_1m_ratio",
    }

    for df in _iter_batches_with_progress(
        handle,
        ["severity", "issues", "warns", "ticker", "date", "metrics_json"],
        batch_size=batch_size,
        max_batches=max_batches,
        stage_name="root_cause_evidence",
    ):
        hard_df = df.loc[df["severity"] == "HARD_FAIL"].copy()
        if hard_df.empty:
            continue
        hard_df["issues_list"] = hard_df["issues"].map(lambda x: flatten_tokens([parse_listish(x)]))
        hard_df["warns_list"] = hard_df["warns"].map(lambda x: flatten_tokens([parse_listish(x)]))
        hard_df["metrics"] = hard_df["metrics_json"].map(parse_dictish)

        for row in hard_df.itertuples(index=False):
            issue_set = set(row.issues_list)
            matched = [issue for issue in focus_issues if issue in issue_set]
            if not matched:
                continue
            warn_set = set(row.warns_list)
            metrics = row.metrics
            for issue in matched:
                stats = issue_stats[issue]
                stats["files"] += 1
                stats["tickers"].add(str(row.ticker))
                stats["dates"].add(str(row.date))
                if "trade_price_outside_1m_range" in warn_set:
                    stats["has_1m_warn_count"] += 1
                for key in metric_keys:
                    full_key = metric_map[key]
                    value = pd.to_numeric(metrics.get(key), errors="coerce")
                    if pd.isna(value):
                        continue
                    stats["metric_seen"][full_key] += 1
                    _update_reservoir(
                        stats["metric_samples"][full_key],
                        {"value": float(value)},
                        stats["metric_seen"][full_key],
                        sample_size_per_issue,
                        rng,
                    )

    rows: list[dict[str, object]] = []
    for issue in focus_issues:
        stats = issue_stats[issue]
        rows.append(
            {
                "issue": issue,
                "files": int(stats["files"]),
                "tickers": int(len(stats["tickers"])),
                "dates": int(len(stats["dates"])),
                "has_1m_warn_pct": 100.0 * stats["has_1m_warn_count"] / max(stats["files"], 1),
                "median_off_session_pct": float(np.median([x["value"] for x in stats["metric_samples"]["m.off_session_trade_pct"]])) if stats["metric_samples"]["m.off_session_trade_pct"] else np.nan,
                "median_dup_pct": float(np.median([x["value"] for x in stats["metric_samples"]["m.duplicate_excess_ratio_pct"]])) if stats["metric_samples"]["m.duplicate_excess_ratio_pct"] else np.nan,
                "median_vol_vs_daily": float(np.median([x["value"] for x in stats["metric_samples"]["m.trade_volume_vs_daily_ratio"]])) if stats["metric_samples"]["m.trade_volume_vs_daily_ratio"] else np.nan,
                "median_vol_vs_1m": float(np.median([x["value"] for x in stats["metric_samples"]["m.trade_volume_vs_1m_ratio"]])) if stats["metric_samples"]["m.trade_volume_vs_1m_ratio"] else np.nan,
            }
        )
    issue_evidence_cd = pd.DataFrame(rows)
    if not issue_evidence_cd.empty:
        issue_evidence_cd = issue_evidence_cd.sort_values(["files", "has_1m_warn_pct"], ascending=[False, False]).reset_index(drop=True)

    return {
        "hard_issue_counts_cd": hard_issue_counts_cd,
        "warn_counts_cd": warn_counts_cd,
        "issue_evidence_cd": issue_evidence_cd,
    }


def build_concentration_artifacts(handle, batch_size: int, top_n: int, max_batches: int | None = None) -> dict[str, pd.DataFrame]:
    month_frames: list[pd.DataFrame] = []
    year_frames: list[pd.DataFrame] = []
    ticker_frames: list[pd.DataFrame] = []

    for df in _iter_batches_with_progress(handle, ["severity", "ticker", "date"], batch_size=batch_size, max_batches=max_batches, stage_name="concentration"):
        if df.empty:
            continue
        date_ts = pd.to_datetime(df["date"], errors="coerce")
        df["month"] = date_ts.dt.to_period("M").astype(str)
        df["year"] = date_ts.dt.year
        month_frames.append(df.groupby(["month", "severity"], dropna=False).size().rename("files").reset_index())
        year_frames.append(df.groupby(["year", "severity"], dropna=False).size().rename("files").reset_index())
        ticker_frames.append(df.groupby(["ticker", "severity"], dropna=False).size().rename("files").reset_index())

    month_mix_full = (
        pd.concat(month_frames, ignore_index=True)
        .groupby(["month", "severity"], dropna=False, as_index=False)["files"].sum()
        if month_frames else pd.DataFrame(columns=["month", "severity", "files"])
    )
    year_mix_full = (
        pd.concat(year_frames, ignore_index=True)
        .groupby(["year", "severity"], dropna=False, as_index=False)["files"].sum()
        if year_frames else pd.DataFrame(columns=["year", "severity", "files"])
    )
    ticker_mix_full = (
        pd.concat(ticker_frames, ignore_index=True)
        .groupby(["ticker", "severity"], dropna=False, as_index=False)["files"].sum()
        if ticker_frames else pd.DataFrame(columns=["ticker", "severity", "files"])
    )

    month_pivot_full = month_mix_full.pivot(index="month", columns="severity", values="files").fillna(0).sort_index()
    month_rate_full = month_pivot_full.div(month_pivot_full.sum(axis=1), axis=0) * 100.0
    year_pivot_full = year_mix_full.pivot(index="year", columns="severity", values="files").fillna(0).sort_index()
    year_rate_full = year_pivot_full.div(year_pivot_full.sum(axis=1), axis=0) * 100.0

    ticker_pivot_full = ticker_mix_full.pivot(index="ticker", columns="severity", values="files").fillna(0)
    ticker_pivot_full["total"] = ticker_pivot_full.sum(axis=1)
    ticker_pivot_full["hard_fail_rate_pct"] = 100.0 * ticker_pivot_full.get("HARD_FAIL", 0) / ticker_pivot_full["total"].clip(lower=1)
    ticker_focus_full = ticker_pivot_full.sort_values(["hard_fail_rate_pct", "total"], ascending=[False, False]).head(top_n).reset_index()

    return {
        "time_concentration_month_cd": month_mix_full,
        "time_concentration_month_rate_cd": month_rate_full.reset_index(),
        "time_concentration_year_cd": year_mix_full,
        "time_concentration_year_rate_cd": year_rate_full.reset_index(),
        "ticker_focus_cd": ticker_focus_full,
    }


def build_diag_artifacts(handle, mod00: dict, mod43: dict, batch_size: int, max_n: int, max_batches: int | None = None) -> dict[str, pd.DataFrame]:
    rng = random.Random(7)
    sample_rows: list[dict] = []
    seen = 0

    for df in _iter_batches_with_progress(handle, ["severity", "warns", "metrics_json", "ticker", "date", "file"], batch_size=batch_size, max_batches=max_batches, stage_name="diag_sample"):
        for row in df.to_dict("records"):
            seen += 1
            _update_reservoir(sample_rows, row, seen, max_n, rng)

    sample_plot_full = mod00["normalize_event_like_df"](pd.DataFrame(sample_rows))
    sample_plot_full = _coerce_numeric(
        sample_plot_full,
        [
            "m.possible_price_scale_factor_vs_daily",
            "m.possible_price_scale_factor_vs_1m",
            "m.duplicate_excess_ratio_pct",
            "m.max_trades_same_timestamp",
        ],
    )
    sample_plot_full, scale_df_full, dup_df_full = mod43["build_sample_plot_full"](sample_plot_full, max_n=max_n, random_state=7)
    dup_outlier_view = mod43["build_dup_outlier_view"](dup_df_full, top_n=25)
    return {
        "diag_sample_cd": sample_plot_full,
        "diag_scale_cd": scale_df_full,
        "diag_dup_cd": dup_df_full,
        "diag_dup_outlier_view_cd": dup_outlier_view,
    }


def build_example_artifacts(handle, mod00: dict, hard_issue_counts_cd: pd.DataFrame, warn_counts_cd: pd.DataFrame, batch_size: int, reservoir_size: int, max_examples: int, max_batches: int | None = None) -> dict[str, pd.DataFrame | str | None]:
    focus_issue = hard_issue_counts_cd.iloc[0]["issue"] if not hard_issue_counts_cd.empty else None
    focus_warn = warn_counts_cd.iloc[0]["warn"] if not warn_counts_cd.empty else None
    rng_issue = random.Random(17)
    rng_warn = random.Random(23)
    issue_rows: list[dict] = []
    warn_rows: list[dict] = []
    issue_seen = 0
    warn_seen = 0

    for df in _iter_batches_with_progress(handle, ["ticker", "date", "severity", "batch_id", "file", "issues", "warns", "metrics_json"], batch_size=batch_size, max_batches=max_batches, stage_name="examples"):
        df = mod00["normalize_event_like_df"](df)
        if focus_issue is not None:
            matched_issue = df.loc[df["issues_list"].map(lambda xs: focus_issue in set(xs)), :].copy()
            for row in matched_issue.to_dict("records"):
                issue_seen += 1
                _update_reservoir(issue_rows, row, issue_seen, reservoir_size, rng_issue)
        if focus_warn is not None:
            matched_warn = df.loc[df["warns_list"].map(lambda xs: focus_warn in set(xs)), :].copy()
            for row in matched_warn.to_dict("records"):
                warn_seen += 1
                _update_reservoir(warn_rows, row, warn_seen, reservoir_size, rng_warn)

    issue_df = pd.DataFrame(issue_rows)
    warn_df = pd.DataFrame(warn_rows)

    issue_examples = pd.DataFrame()
    warn_examples = pd.DataFrame()
    if not issue_df.empty:
        issue_examples = (
            issue_df[
                [
                    "ticker", "date", "severity", "batch_id", "file",
                    "m.price_min", "m.price_max", "m.trade_vwap", "m.vw",
                    "m.ohlcv_1m_low_min", "m.ohlcv_1m_high_max",
                    "m.trade_volume_vs_daily_ratio", "m.trade_volume_vs_1m_ratio",
                    "m.possible_price_scale_factor_vs_daily", "m.possible_price_scale_factor_vs_1m",
                    "issues_list", "warns_list",
                ]
            ]
            .sort_values(["ticker", "date"])
            .head(max_examples)
            .reset_index(drop=True)
        )
    if not warn_df.empty:
        warn_examples = (
            warn_df[
                [
                    "ticker", "date", "severity", "batch_id", "file",
                    "m.duplicate_excess_ratio_pct", "m.max_trades_same_timestamp",
                    "m.off_session_trade_pct", "m.trade_volume_vs_daily_ratio",
                    "m.trade_volume_vs_1m_ratio", "issues_list", "warns_list",
                ]
            ]
            .sort_values(["ticker", "date"])
            .head(max_examples)
            .reset_index(drop=True)
        )

    return {
        "focus_issue": focus_issue,
        "focus_warn": focus_warn,
        "issue_examples_cd": issue_examples,
        "warn_examples_cd": warn_examples,
    }


def build_break_artifacts(handle, mod00: dict, mod46: dict, output_path: Path, batch_size: int, max_batches: int | None = None) -> dict[str, pd.DataFrame]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    top_breaks_accum = pd.DataFrame()
    summary = {
        "files": 0,
        "tickers": set(),
        "dates": set(),
        "below_only": 0,
        "above_only": 0,
        "both": 0,
    }

    try:
        for df in _iter_batches_with_progress(
            handle,
            ["file", "ticker", "date", "severity", "batch_id", "issues", "warns", "metrics_json"],
            batch_size=batch_size,
            max_batches=max_batches,
            stage_name="break_cache",
        ):
            df = mod00["normalize_event_like_df"](df)
            matched = df.loc[df["issues_list"].map(lambda xs: "trade_price_outside_daily_range" in set(xs)), :]
            if matched.empty:
                continue
            break_chunk = mod46["build_break_cache_chunk"](matched)
            summary["files"] += len(break_chunk)
            summary["tickers"].update(break_chunk["ticker"].astype(str).dropna().tolist())
            summary["dates"].update(pd.to_datetime(break_chunk["date"], errors="coerce").astype(str).tolist())
            summary["below_only"] += int((break_chunk["break_side"] == "below_only").sum())
            summary["above_only"] += int((break_chunk["break_side"] == "above_only").sum())
            summary["both"] += int((break_chunk["break_side"] == "both").sum())

            top_breaks_accum = pd.concat(
                [
                    top_breaks_accum,
                    mod46["build_top_breaks"](break_chunk, top_n=200)[0],
                ],
                ignore_index=True,
            )
            top_breaks_accum = top_breaks_accum.sort_values(
                ["break_pct_span_max", "break_abs_max"],
                ascending=[False, False],
            ).head(500).reset_index(drop=True)

            table = pa.Table.from_pandas(break_chunk, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(str(output_path), table.schema)
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()

    break_summary = pd.DataFrame(
        [
            {
                "files": int(summary["files"]),
                "tickers": int(len(summary["tickers"])),
                "dates": int(len(summary["dates"])),
                "below_only": int(summary["below_only"]),
                "above_only": int(summary["above_only"]),
                "both": int(summary["both"]),
            }
        ]
    )
    return {
        "break_summary_cd": break_summary,
        "top_breaks_cd": top_breaks_accum.reset_index(drop=True),
    }


def build_case_index(
    issue_examples_cd: pd.DataFrame,
    warn_examples_cd: pd.DataFrame,
    top_breaks_cd: pd.DataFrame,
    tax_df_cd: pd.DataFrame,
    final_df_cd: pd.DataFrame,
    focus_issue: str | None,
    focus_warn: str | None,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    if not issue_examples_cd.empty:
        issue_idx = issue_examples_cd[["ticker", "date", "file", "severity", "batch_id"]].copy()
        issue_idx["block"] = "root_cause_issue"
        issue_idx["group_key"] = focus_issue
        issue_idx["group_label"] = focus_issue
        issue_idx["focus_issue"] = focus_issue
        issue_idx["focus_warn"] = None
        issue_idx["break_side"] = None
        issue_idx["taxonomy"] = None
        issue_idx["rank_score"] = pd.to_numeric(issue_examples_cd.get("m.trade_volume_vs_1m_ratio"), errors="coerce").fillna(0.0)
        frames.append(issue_idx)

    if not warn_examples_cd.empty:
        warn_idx = warn_examples_cd[["ticker", "date", "file", "severity", "batch_id"]].copy()
        warn_idx["block"] = "root_cause_warn"
        warn_idx["group_key"] = focus_warn
        warn_idx["group_label"] = focus_warn
        warn_idx["focus_issue"] = None
        warn_idx["focus_warn"] = focus_warn
        warn_idx["break_side"] = None
        warn_idx["taxonomy"] = None
        warn_idx["rank_score"] = pd.to_numeric(warn_examples_cd.get("m.duplicate_excess_ratio_pct"), errors="coerce").fillna(0.0)
        frames.append(warn_idx)

    if not top_breaks_cd.empty:
        break_idx = top_breaks_cd[["ticker", "date", "file", "severity", "break_side"]].copy()
        if "batch_id" not in break_idx.columns:
            break_idx["batch_id"] = pd.Series(index=break_idx.index, dtype="object")
        break_idx["block"] = "breaks"
        break_idx["group_key"] = break_idx["break_side"].astype(str)
        break_idx["group_label"] = break_idx["break_side"].astype(str)
        break_idx["focus_issue"] = "trade_price_outside_daily_range"
        break_idx["focus_warn"] = None
        break_idx["taxonomy"] = None
        break_idx["rank_score"] = pd.to_numeric(top_breaks_cd.get("break_pct_span_max"), errors="coerce").fillna(0.0)
        frames.append(break_idx)

    if not tax_df_cd.empty:
        tax_rank = tax_df_cd.copy()
        tax_rank["rank_score"] = (
            0.65 * np.log1p(pd.to_numeric(tax_rank.get("break_pct_span_max"), errors="coerce").fillna(0.0))
            + 0.35 * np.log1p(pd.to_numeric(tax_rank.get("break_abs_max"), errors="coerce").fillna(0.0))
        )
        tax_idx = (
            tax_rank.sort_values(["rank_score", "break_pct_span_max", "break_abs_max"], ascending=[False, False, False])
            [["ticker", "date", "file", "severity", "batch_id", "break_side", "taxonomy", "rank_score"]]
            .head(1000)
            .copy()
        )
        tax_idx["block"] = "taxonomy"
        tax_idx["group_key"] = tax_idx["taxonomy"].astype(str) + "|" + tax_idx["break_side"].astype(str)
        tax_idx["group_label"] = tax_idx["group_key"]
        tax_idx["focus_issue"] = "trade_price_outside_daily_range"
        tax_idx["focus_warn"] = None
        frames.append(tax_idx)

    if not final_df_cd.empty:
        final_rank = final_df_cd.copy()
        final_rank["rank_score"] = (
            0.65 * np.log1p(pd.to_numeric(final_rank.get("break_pct_span_max"), errors="coerce").fillna(0.0))
            + 0.35 * np.log1p(pd.to_numeric(final_rank.get("break_abs_max"), errors="coerce").fillna(0.0))
        )
        final_idx = (
            final_rank.sort_values(["rank_score", "break_pct_span_max", "break_abs_max"], ascending=[False, False, False])
            [["ticker", "date", "file", "severity", "batch_id", "break_side", "taxonomy", "final_bucket", "rank_score"]]
            .head(1000)
            .copy()
        )
        final_idx["block"] = "final_bucket"
        final_idx["group_key"] = final_idx["final_bucket"].astype(str)
        final_idx["group_label"] = final_idx["final_bucket"].astype(str)
        final_idx["focus_issue"] = "trade_price_outside_daily_range"
        final_idx["focus_warn"] = None
        frames.append(final_idx)

    if not frames:
        return pd.DataFrame(
            columns=[
                "block", "group_key", "group_label", "taxonomy", "focus_issue",
                "focus_warn", "break_side", "final_bucket", "severity", "ticker", "date",
                "file", "batch_id", "rank_score", "display_label",
            ]
        )

    case_index = pd.concat(frames, ignore_index=True)
    case_index["display_label"] = (
        case_index["ticker"].astype(str)
        + " | "
        + pd.to_datetime(case_index["date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna(case_index["date"].astype(str))
        + " | "
        + case_index["block"].astype(str)
    )
    return case_index.sort_values(["block", "group_key", "rank_score"], ascending=[True, True, False]).reset_index(drop=True)


def build_taxonomy_artifacts(daily_break_path: Path, mods: dict[str, dict], output_dir: Path) -> dict[str, pd.DataFrame]:
    daily_break_full = pd.read_parquet(daily_break_path)
    band_df = mods["mod47"]["build_band_df"](daily_break_full)
    abs_bucket_counts, pct_bucket_counts = mods["mod47"]["build_band_counts"](band_df)
    cross_abs, cross_pct = mods["mod53"]["build_cross_band_tables"](band_df)
    cross_abs_pct, cross_pct_pct = mods["mod53"]["build_cross_band_pct_tables"](cross_abs, cross_pct)
    tax_df = mods["mod48"]["build_tax_df"](daily_break_full, dup_heavy_threshold=1.0)
    taxonomy_summary = mods["mod48"]["build_taxonomy_summary"](tax_df)
    taxonomy_side = mods["mod49"]["build_taxonomy_side"](tax_df)
    taxonomy_side_view = mods["mod55"]["build_taxonomy_side_view"](taxonomy_side)
    final_df = mods["mod51"]["build_final_df"](tax_df)
    final_summary = mods["mod51"]["build_final_summary"](final_df)
    return {
        "band_df_cd": band_df,
        "abs_bucket_counts_cd": abs_bucket_counts,
        "pct_bucket_counts_cd": pct_bucket_counts,
        "cross_abs_cd": cross_abs,
        "cross_pct_cd": cross_pct,
        "cross_abs_pct_cd": cross_abs_pct,
        "cross_pct_pct_cd": cross_pct_pct,
        "tax_df_cd": tax_df,
        "taxonomy_summary_cd": taxonomy_summary,
        "taxonomy_side_cd": taxonomy_side,
        "taxonomy_side_view_cd": taxonomy_side_view,
        "final_df_cd": final_df,
        "final_summary_cd": final_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build low-memory C+D audit artifacts for trades.")
    parser.add_argument("--current-parquet", type=Path, default=CURRENT_PARQUET_CD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--diag-sample-size", type=int, default=100_000)
    parser.add_argument("--issue-sample-size", type=int, default=20_000)
    parser.add_argument("--top-issue-evidence", type=int, default=15)
    parser.add_argument("--example-reservoir-size", type=int, default=5_000)
    parser.add_argument("--example-head", type=int, default=30)
    parser.add_argument("--max-batches", type=int, default=None)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    mods = _load_modules(base_dir)
    mod00 = mods["mod00"]
    handle = mod00["make_trades_audit_handle"](args.current_parquet)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "builder": "build_trades_cd_audit_artifacts.py",
        "current_parquet": str(args.current_parquet),
        "row_count": int(handle.row_count()),
        "batch_size": int(args.batch_size),
        "diag_sample_size": int(args.diag_sample_size),
        "issue_sample_size": int(args.issue_sample_size),
        "top_issue_evidence": int(args.top_issue_evidence),
        "example_reservoir_size": int(args.example_reservoir_size),
        "example_head": int(args.example_head),
        "max_batches": args.max_batches,
        "generated_at_utc": _utcnow_iso(),
        "artifacts": {},
    }

    start = time.perf_counter()
    print(
        json.dumps(
            {
                "ts": _utcnow_iso(),
                "event": "builder_start",
                "current_parquet": str(args.current_parquet),
                "row_count": manifest["row_count"],
                "batch_size": args.batch_size,
                "max_batches": args.max_batches,
                "output_dir": str(args.output_dir),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    snapshot_artifacts = build_snapshot_artifacts(handle, mods["mod40"], args.current_parquet)
    for name, df in snapshot_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    root_cause_artifacts = build_root_cause_artifacts(
        handle=handle,
        mod00=mod00,
        batch_size=args.batch_size,
        sample_size_per_issue=args.issue_sample_size,
        top_n_issue_evidence=args.top_issue_evidence,
        max_batches=args.max_batches,
    )
    for name, df in root_cause_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    concentration_artifacts = build_concentration_artifacts(
        handle=handle,
        batch_size=args.batch_size,
        top_n=25,
        max_batches=args.max_batches,
    )
    for name, df in concentration_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    diag_artifacts = build_diag_artifacts(
        handle=handle,
        mod00=mod00,
        mod43=mods["mod43"],
        batch_size=args.batch_size,
        max_n=args.diag_sample_size,
        max_batches=args.max_batches,
    )
    for name, df in diag_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    example_artifacts = build_example_artifacts(
        handle=handle,
        mod00=mod00,
        hard_issue_counts_cd=root_cause_artifacts["hard_issue_counts_cd"],
        warn_counts_cd=root_cause_artifacts["warn_counts_cd"],
        batch_size=args.batch_size,
        reservoir_size=args.example_reservoir_size,
        max_examples=args.example_head,
        max_batches=args.max_batches,
    )
    focus_issue = example_artifacts.pop("focus_issue")
    focus_warn = example_artifacts.pop("focus_warn")
    manifest["focus_issue"] = focus_issue
    manifest["focus_warn"] = focus_warn
    for name, df in example_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    exec_summary_full, exec_readout_full_md = mods["mod45"]["build_exec_summary_from_counts"](
        selected_files=manifest["row_count"],
        sev_counts_full=snapshot_artifacts["severity_counts_cd"],
        hard_issue_counts_full=root_cause_artifacts["hard_issue_counts_cd"],
        issue_evidence_full=root_cause_artifacts["issue_evidence_cd"],
    )
    _write_df(exec_summary_full, args.output_dir / "exec_summary_cd.parquet")
    (args.output_dir / "exec_readout_cd.md").write_text(exec_readout_full_md, encoding="utf-8")
    manifest["artifacts"]["exec_summary_cd"] = {"rows": int(len(exec_summary_full))}
    manifest["artifacts"]["exec_readout_cd"] = {"path": "exec_readout_cd.md"}

    break_output_path = args.output_dir / "daily_break_cd.parquet"
    break_artifacts = build_break_artifacts(
        handle=handle,
        mod00=mod00,
        mod46=mods["mod46"],
        output_path=break_output_path,
        batch_size=args.batch_size,
        max_batches=args.max_batches,
    )
    manifest["artifacts"]["daily_break_cd"] = {"path": "daily_break_cd.parquet"}
    for name, df in break_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    taxonomy_artifacts = build_taxonomy_artifacts(
        daily_break_path=break_output_path,
        mods=mods,
        output_dir=args.output_dir,
    )
    for name, df in taxonomy_artifacts.items():
        _write_df(df, args.output_dir / f"{name}.parquet")
        manifest["artifacts"][name] = {"rows": int(len(df))}

    case_index_cd = build_case_index(
        issue_examples_cd=example_artifacts["issue_examples_cd"],
        warn_examples_cd=example_artifacts["warn_examples_cd"],
        top_breaks_cd=break_artifacts["top_breaks_cd"],
        tax_df_cd=taxonomy_artifacts["tax_df_cd"],
        final_df_cd=taxonomy_artifacts["final_df_cd"],
        focus_issue=focus_issue,
        focus_warn=focus_warn,
    )
    _write_df(case_index_cd, args.output_dir / "case_index_cd.parquet")
    manifest["artifacts"]["case_index_cd"] = {"rows": int(len(case_index_cd))}

    manifest["elapsed_sec"] = round(time.perf_counter() - start, 3)
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "ts": _utcnow_iso(),
                "event": "builder_end",
                "output_dir": str(args.output_dir),
                "elapsed_sec": manifest["elapsed_sec"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    print(json.dumps({"status": "ok", "output_dir": str(args.output_dir), "elapsed_sec": manifest["elapsed_sec"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
