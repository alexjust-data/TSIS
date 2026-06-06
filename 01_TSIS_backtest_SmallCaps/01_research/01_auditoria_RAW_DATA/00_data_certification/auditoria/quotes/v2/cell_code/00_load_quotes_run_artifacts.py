from __future__ import annotations

import ast
import gc
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from IPython.display import Markdown, display


CURRENT_PARQUET_CD = Path(
    globals().get(
        "CURRENT_PARQUET_CD",
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet",
    )
)

CURRENT_PARQUET_D = Path(
    globals().get(
        "CURRENT_PARQUET_D",
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_full_sharded_merged\quotes_current.parquet",
    )
)

CURRENT_PARQUET_C = Path(
    globals().get(
        "CURRENT_PARQUET_C",
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_c_full_sharded_merged\quotes_current.parquet",
    )
)

CACHE_DIR = Path(
    globals().get(
        "QUOTES_NOTEBOOK_CACHE_DIR",
        r"C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache_v2",
    )
)

TARGET_LT1B_PATH = Path(
    globals().get(
        "TARGET_LT1B_PATH",
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    )
)

PAT_SINGLE_QUOTED = re.compile(r"'([^']+)'")
PAT_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')


def _parse_token_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    text = str(value).strip()
    if not text or text == "[]" or text.lower() == "nan":
        return []
    hits = PAT_SINGLE_QUOTED.findall(text)
    if hits:
        return [token.strip() for token in hits if token.strip()]
    hits = PAT_DOUBLE_QUOTED.findall(text)
    if hits:
        return [token.strip() for token in hits if token.strip()]
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple, set, np.ndarray)):
            return [str(x) for x in parsed if str(x).strip()]
        return [str(parsed)]
    except Exception:
        cleaned = text.strip("[]")
        cleaned = cleaned.replace("\n", " ")
        return [chunk.strip(" '\"") for chunk in cleaned.split(",") if chunk.strip(" '\"")]


def _parse_metrics(value: Any) -> dict[str, Any]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return {}
    if isinstance(value, dict):
        return value
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _slug(parts: Iterable[Any]) -> str:
    text = "|".join(str(x) for x in parts)
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def _first_token(series: pd.Series) -> pd.Series:
    return series.map(lambda values: values[0] if values else None)


def _update_counter_from_series(counter: Counter[str], series: pd.Series) -> None:
    for values in series:
        for token in values:
            counter[str(token)] += 1


def _merge_top_n(
    existing: pd.DataFrame | None,
    incoming: pd.DataFrame | None,
    sort_by: list[str],
    ascending: list[bool],
    top_n: int,
) -> pd.DataFrame:
    frames = []
    if existing is not None and not existing.empty:
        frames.append(existing)
    if incoming is not None and not incoming.empty:
        frames.append(incoming)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values(sort_by, ascending=ascending).head(top_n).reset_index(drop=True)
    return out


def _safe_numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(dtype="float64")


def _compute_cross_gap_metrics_from_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    out: dict[str, Any] = {
        "raw_rows": 0,
        "valid_rows": 0,
        "crossed_rows_raw": 0,
        "crossed_rows_ask_zero": 0,
        "crossed_rows_ask_positive": 0,
        "crossed_ask_zero_share_pct": np.nan,
        "crossed_ask_positive_share_pct": np.nan,
        "cross_abs_median": np.nan,
        "cross_abs_p90": np.nan,
        "cross_abs_max": np.nan,
        "cross_rel_bps_median": np.nan,
        "cross_rel_bps_p90": np.nan,
        "cross_rel_bps_max": np.nan,
        "cross_abs_median_ask_positive": np.nan,
        "cross_abs_p90_ask_positive": np.nan,
        "cross_rel_bps_median_ask_positive": np.nan,
        "cross_rel_bps_p90_ask_positive": np.nan,
        "near_zero_share_pct_ask_positive": np.nan,
        "mild_share_pct_ask_positive": np.nan,
        "moderate_share_pct_ask_positive": np.nan,
        "severe_share_pct_ask_positive": np.nan,
        "crossed_area_abs": np.nan,
        "near_zero_share_pct": np.nan,
        "mild_share_pct": np.nan,
        "moderate_share_pct": np.nan,
        "severe_share_pct": np.nan,
    }
    if not path.exists():
        return out

    try:
        df = pd.read_parquet(path, columns=["bid_price", "ask_price"])
    except Exception:
        try:
            table = pq.ParquetFile(path).read(columns=["bid_price", "ask_price"])
            df = table.to_pandas()
        except Exception:
            return out

    out["raw_rows"] = int(len(df))
    bid = _safe_numeric_series(df, "bid_price")
    ask = _safe_numeric_series(df, "ask_price")
    valid = pd.DataFrame({"bid_price": bid, "ask_price": ask}).dropna().copy()
    out["valid_rows"] = int(len(valid))
    if valid.empty:
        return out

    crossed = valid.loc[valid["bid_price"] > valid["ask_price"]].copy()
    out["crossed_rows_raw"] = int(len(crossed))
    if crossed.empty:
        return out

    ask_zero_mask = crossed["ask_price"].eq(0)
    crossed_ask_zero = crossed.loc[ask_zero_mask].copy()
    crossed_ask_positive = crossed.loc[~ask_zero_mask & crossed["ask_price"].gt(0)].copy()
    out["crossed_rows_ask_zero"] = int(len(crossed_ask_zero))
    out["crossed_rows_ask_positive"] = int(len(crossed_ask_positive))
    denom_crossed = max(len(crossed), 1)
    out["crossed_ask_zero_share_pct"] = float(len(crossed_ask_zero) / denom_crossed * 100.0)
    out["crossed_ask_positive_share_pct"] = float(len(crossed_ask_positive) / denom_crossed * 100.0)

    crossed["cross_abs"] = crossed["bid_price"] - crossed["ask_price"]
    crossed["mid_price"] = (crossed["bid_price"] + crossed["ask_price"]) / 2.0
    crossed["cross_rel_bps"] = np.where(
        crossed["mid_price"] > 0,
        crossed["cross_abs"] / crossed["mid_price"] * 10000.0,
        np.nan,
    )
    rel = pd.to_numeric(crossed["cross_rel_bps"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    abs_gap = pd.to_numeric(crossed["cross_abs"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()

    if not abs_gap.empty:
        out["cross_abs_median"] = float(abs_gap.median())
        out["cross_abs_p90"] = float(abs_gap.quantile(0.9))
        out["cross_abs_max"] = float(abs_gap.max())
        out["crossed_area_abs"] = float(abs_gap.sum())
    if not rel.empty:
        out["cross_rel_bps_median"] = float(rel.median())
        out["cross_rel_bps_p90"] = float(rel.quantile(0.9))
        out["cross_rel_bps_max"] = float(rel.max())
        denom = max(len(rel), 1)
        out["near_zero_share_pct"] = float(rel.le(1.0).sum() / denom * 100.0)
        out["mild_share_pct"] = float((rel.gt(1.0) & rel.le(5.0)).sum() / denom * 100.0)
        out["moderate_share_pct"] = float((rel.gt(5.0) & rel.le(25.0)).sum() / denom * 100.0)
        out["severe_share_pct"] = float(rel.gt(25.0).sum() / denom * 100.0)

    if not crossed_ask_positive.empty:
        crossed_ask_positive["cross_abs"] = crossed_ask_positive["bid_price"] - crossed_ask_positive["ask_price"]
        crossed_ask_positive["mid_price"] = (crossed_ask_positive["bid_price"] + crossed_ask_positive["ask_price"]) / 2.0
        crossed_ask_positive["cross_rel_bps"] = np.where(
            crossed_ask_positive["mid_price"] > 0,
            crossed_ask_positive["cross_abs"] / crossed_ask_positive["mid_price"] * 10000.0,
            np.nan,
        )
        rel_pos = pd.to_numeric(crossed_ask_positive["cross_rel_bps"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        abs_pos = pd.to_numeric(crossed_ask_positive["cross_abs"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if not abs_pos.empty:
            out["cross_abs_median_ask_positive"] = float(abs_pos.median())
            out["cross_abs_p90_ask_positive"] = float(abs_pos.quantile(0.9))
        if not rel_pos.empty:
            out["cross_rel_bps_median_ask_positive"] = float(rel_pos.median())
            out["cross_rel_bps_p90_ask_positive"] = float(rel_pos.quantile(0.9))
            denom_pos = max(len(rel_pos), 1)
            out["near_zero_share_pct_ask_positive"] = float(rel_pos.le(1.0).sum() / denom_pos * 100.0)
            out["mild_share_pct_ask_positive"] = float((rel_pos.gt(1.0) & rel_pos.le(5.0)).sum() / denom_pos * 100.0)
            out["moderate_share_pct_ask_positive"] = float((rel_pos.gt(5.0) & rel_pos.le(25.0)).sum() / denom_pos * 100.0)
            out["severe_share_pct_ask_positive"] = float(rel_pos.gt(25.0).sum() / denom_pos * 100.0)
    return out


def _classify_quotes_taxonomy_v21(work: pd.DataFrame) -> pd.Series:
    def _metric_series(name: str, default: float = 0.0) -> pd.Series:
        value = work.get(name)
        if isinstance(value, pd.Series):
            return pd.to_numeric(value, errors="coerce").fillna(default)
        return pd.Series(default, index=work.index, dtype="float64")

    crossed = _metric_series("m.crossed_ratio_pct")
    crossed_rows = _metric_series("m.crossed_rows")
    ask_integer = _metric_series("m.ask_integer_pct")
    ask_eq_round_bid = _metric_series("m.ask_eq_round_bid_pct")
    rows = _metric_series("rows")
    severity = work.get("severity", pd.Series("", index=work.index)).astype(str)
    ts_shift = work.get("m.timestamp_out_of_partition_day", pd.Series(False, index=work.index)).fillna(False).astype(bool)

    conditions = [
        severity.eq("HARD_FAIL") & crossed.ge(90) & ask_integer.ge(90),
        severity.eq("HARD_FAIL") & crossed.ge(20) & ask_integer.ge(80),
        severity.eq("HARD_FAIL") & crossed.ge(20) & ts_shift,
        severity.eq("HARD_FAIL") & crossed.ge(20),
        severity.eq("HARD_FAIL") & crossed.ge(10) & crossed.lt(20),
        severity.eq("HARD_FAIL") & crossed.ge(5),
        severity.eq("HARD_FAIL") & crossed.gt(0) & crossed.lt(5) & rows.le(100),
        severity.eq("HARD_FAIL") & crossed.gt(0) & crossed.lt(5) & rows.gt(100) & rows.le(1000) & crossed_rows.le(5),
        severity.eq("HARD_FAIL") & crossed.gt(0) & crossed.lt(5) & rows.gt(100) & rows.le(1000),
        severity.eq("HARD_FAIL") & crossed.gt(0) & crossed.lt(5) & rows.gt(1000) & crossed_rows.lt(50),
        severity.eq("HARD_FAIL") & crossed.gt(0) & crossed.lt(5) & rows.gt(1000),
        severity.eq("SOFT_FAIL") & ts_shift & crossed.le(0.1),
        severity.eq("SOFT_FAIL") & ts_shift & crossed.gt(0.1),
        severity.eq("SOFT_FAIL") & crossed.le(0.1),
        severity.eq("SOFT_FAIL") & crossed.gt(0.1) & crossed.le(0.3),
        severity.eq("SOFT_FAIL") & crossed.gt(0.3) & rows.lt(10_000),
        severity.eq("SOFT_FAIL") & crossed.gt(0.3),
        severity.eq("PASS") & ask_eq_round_bid.ge(80),
    ]
    choices = [
        "extreme_integerized_100pct_crossed",
        "extreme_hard_crossed_gt20_integerized",
        "extreme_hard_crossed_gt20_non_integerized_with_utc_rollover",
        "extreme_hard_crossed_gt20_non_integerized",
        "high_hard_crossed_10_to_20",
        "high_hard_crossed_5_to_20",
        "small_file_threshold_edge_hard",
        "medium_file_threshold_edge_hard_few_crosses",
        "medium_file_threshold_edge_hard_many_crosses",
        "large_file_threshold_edge_hard_few_crosses",
        "large_file_threshold_edge_hard_many_crosses",
        "utc_rollover_large_day_clean",
        "utc_rollover_large_day_with_soft_crossed",
        "soft_crossed_micro_noise",
        "persistent_soft_crossed_low",
        "persistent_soft_crossed_mid_thin_scale",
        "persistent_soft_crossed_mid_large_scale",
        "rounded_ask_pattern_without_cross_hard",
    ]
    return pd.Series(np.select(conditions, choices, default="clean_pass_or_other"), index=work.index, dtype="string")


def _reservoir_extend(
    reservoir: list[float],
    incoming: Iterable[float],
    seen: int,
    max_size: int,
    rng: np.random.Generator,
) -> int:
    for value in incoming:
        seen += 1
        if len(reservoir) < max_size:
            reservoir.append(float(value))
        else:
            j = int(rng.integers(0, seen))
            if j < max_size:
                reservoir[j] = float(value)
    return seen


@dataclass(frozen=True)
class QuotesAuditHandle:
    path: Path
    label: str
    cache_dir: Path
    target_tickers: frozenset[str] | None = None
    target_path: Path | None = None

    def parquet(self) -> pq.ParquetFile:
        return pq.ParquetFile(self.path)

    def row_count(self) -> int:
        return int(self.parquet().metadata.num_rows)

    def file_size_mb(self) -> float:
        return round(self.path.stat().st_size / 1024 / 1024, 2)

    def iter_batches(
        self,
        columns: list[str],
        batch_size: int = 200_000,
        stage_name: str | None = None,
        report_every: int | None = None,
    ):
        pf = self.parquet()
        read_columns = list(columns)
        needs_ticker_filter = self.target_tickers is not None
        if needs_ticker_filter and "ticker" not in read_columns:
            read_columns.append("ticker")
        batch_idx = 0
        source_rows_seen = 0
        filtered_rows_seen = 0
        total_source_rows = self.row_count()
        for batch in pf.iter_batches(columns=read_columns, batch_size=batch_size):
            batch_idx += 1
            source_rows_seen += batch.num_rows
            df = batch.to_pandas()
            if needs_ticker_filter:
                ticker_series = df["ticker"].astype("string")
                df = df.loc[ticker_series.isin(self.target_tickers)].copy()
                if df.empty:
                    if stage_name and report_every and batch_idx % report_every == 0:
                        print(
                            json.dumps(
                                {
                                    "stage": stage_name,
                                    "batch_idx": batch_idx,
                                    "source_rows_seen": int(source_rows_seen),
                                    "source_rows_total": int(total_source_rows),
                                    "filtered_rows_seen": int(filtered_rows_seen),
                                }
                            )
                        )
                    continue
            filtered_rows_seen += len(df)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            if stage_name and report_every and batch_idx % report_every == 0:
                print(
                    json.dumps(
                        {
                            "stage": stage_name,
                            "batch_idx": batch_idx,
                            "source_rows_seen": int(source_rows_seen),
                            "source_rows_total": int(total_source_rows),
                            "filtered_rows_seen": int(filtered_rows_seen),
                        }
                    )
                )
            yield df
        if stage_name:
            print(
                json.dumps(
                    {
                        "stage": stage_name,
                        "status": "completed",
                        "batches_total": batch_idx,
                        "source_rows_seen": int(source_rows_seen),
                        "source_rows_total": int(total_source_rows),
                        "filtered_rows_seen": int(filtered_rows_seen),
                    }
                )
            )

    def cache_path(self, stem: str, suffix: str = ".parquet") -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir / f"{stem}_{self.label}{suffix}"


def load_target_lt1b_tickers(target_path: Path = TARGET_LT1B_PATH) -> frozenset[str]:
    df = pd.read_parquet(target_path, columns=["ticker"])
    tickers = df["ticker"].dropna().astype(str).str.strip()
    tickers = tickers[tickers != ""]
    return frozenset(tickers.tolist())


def load_quotes_artifacts() -> dict[str, Any]:
    target_tickers = load_target_lt1b_tickers(TARGET_LT1B_PATH)
    handle_cd = QuotesAuditHandle(
        CURRENT_PARQUET_CD,
        "cd_lt1b",
        CACHE_DIR,
        target_tickers=target_tickers,
        target_path=TARGET_LT1B_PATH,
    )
    handle_d = QuotesAuditHandle(CURRENT_PARQUET_D, "d", CACHE_DIR)
    handle_c = QuotesAuditHandle(CURRENT_PARQUET_C, "c", CACHE_DIR)
    return {
        "current_parquet_cd": CURRENT_PARQUET_CD,
        "current_parquet_d": CURRENT_PARQUET_D,
        "current_parquet_c": CURRENT_PARQUET_C,
        "target_lt1b_path": TARGET_LT1B_PATH,
        "target_lt1b_tickers": target_tickers,
        "cache_dir": CACHE_DIR,
        "quotes_handle_cd": handle_cd,
        "quotes_handle_d": handle_d,
        "quotes_handle_c": handle_c,
    }


def show_load_summary(payload: dict[str, Any]) -> None:
    cd = payload["quotes_handle_cd"]
    d = payload["quotes_handle_d"]
    c = payload["quotes_handle_c"]
    md = f"""
### Loader quotes C+D `<1B>`

- current final `C + D`: `{cd.path}`
- current D: `{d.path}`
- current C: `{c.path}`
- target `<1B>` path: `{payload["target_lt1b_path"]}`
- target tickers `<1B>`: `{len(payload["target_lt1b_tickers"]):,}`
- source rows C+D full: `{cd.row_count():,}` | parquet `{cd.file_size_mb():,.2f} MB`
- rows D: `{d.row_count():,}` | parquet `{d.file_size_mb():,.2f} MB`
- rows C: `{c.row_count():,}` | parquet `{c.file_size_mb():,.2f} MB`
- filtro aplicado en analitica: `ticker in target_lt1b_tickers`
- modo de trabajo: `lazy/chunked`
- cache notebook: `{payload["cache_dir"]}`
"""
    display(Markdown(md))


def build_snapshot_inputs_cached(handle: QuotesAuditHandle, refresh: bool = False) -> pd.DataFrame:
    cache_path = handle.cache_path("snapshot_inputs")
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    parts: list[pd.DataFrame] = []
    columns = ["ticker", "date", "rows", "severity", "root", "metrics_json"]
    for df in handle.iter_batches(columns):
        metrics = df["metrics_json"].map(_parse_metrics)
        out = pd.DataFrame(
            {
                "ticker": df["ticker"].astype("string"),
                "date": df["date"],
                "rows": pd.to_numeric(df["rows"], errors="coerce"),
                "severity": df["severity"].astype("string"),
                "root": df["root"].astype("string"),
                "m.crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "m.timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
            }
        )
        parts.append(out)
    snapshot_df = pd.concat(parts, ignore_index=True)
    snapshot_df.to_parquet(cache_path, index=False)
    return snapshot_df


def build_snapshot_artifacts_cached(handle: QuotesAuditHandle, refresh: bool = False) -> dict[str, pd.DataFrame]:
    cache_snapshot = handle.cache_path("snapshot")
    cache_severity = handle.cache_path("severity_counts")
    cache_root = handle.cache_path("root_mix")
    if all(path.exists() for path in [cache_snapshot, cache_severity, cache_root]) and not refresh:
        return {
            "snapshot": pd.read_parquet(cache_snapshot),
            "severity_counts": pd.read_parquet(cache_severity),
            "root_mix": pd.read_parquet(cache_root),
        }

    severity_counter: Counter[str] = Counter()
    root_severity_counter: Counter[tuple[str, str]] = Counter()
    ticker_seen: set[str] = set()
    date_min = None
    date_max = None
    ts_partition_rows = 0
    rng = np.random.default_rng(7)
    rows_sample: list[float] = []
    rows_seen = 0
    crossed_sample: list[float] = []
    crossed_seen = 0
    total_rows = 0

    cols = ["ticker", "date", "rows", "severity", "root", "metrics_json"]
    for df in handle.iter_batches(cols, batch_size=50_000, stage_name="snapshot_scan_lt1b", report_every=10):
        total_rows += len(df)
        severity_counter.update(df["severity"].astype(str).value_counts(dropna=False).to_dict())
        root_counts = df.groupby(["root", "severity"], dropna=False).size()
        for key, value in root_counts.items():
            root_severity_counter[(str(key[0]), str(key[1]))] += int(value)

        ticker_seen.update(df["ticker"].dropna().astype(str).tolist())
        if "date" in df.columns and not df["date"].dropna().empty:
            batch_min = df["date"].min()
            batch_max = df["date"].max()
            date_min = batch_min if date_min is None or batch_min < date_min else date_min
            date_max = batch_max if date_max is None or batch_max > date_max else date_max

        metrics = df["metrics_json"].map(_parse_metrics)
        ts_partition_rows += int(metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))).sum())

        rows_seen = _reservoir_extend(rows_sample, pd.to_numeric(df["rows"], errors="coerce").dropna().astype(float).tolist(), rows_seen, 500_000, rng)
        crossed_seen = _reservoir_extend(
            crossed_sample,
            pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce").dropna().astype(float).tolist(),
            crossed_seen,
            500_000,
            rng,
        )

        del df, metrics
        gc.collect()

    sev_counts = pd.DataFrame(severity_counter.items(), columns=["severity", "files"])
    sev_counts["pct"] = sev_counts["files"] / max(total_rows, 1) * 100.0
    sev_counts["severity"] = pd.Categorical(sev_counts["severity"], categories=["PASS", "SOFT_FAIL", "HARD_FAIL"], ordered=True)
    sev_counts = sev_counts.sort_values("severity").reset_index(drop=True)

    root_mix = pd.DataFrame(
        [{"root": root, "severity": sev, "files": files} for (root, sev), files in root_severity_counter.items()]
    )
    if not root_mix.empty:
        root_mix = root_mix.pivot(index="root", columns="severity", values="files").fillna(0).reindex(columns=["PASS", "SOFT_FAIL", "HARD_FAIL"], fill_value=0)
        root_mix["total"] = root_mix.sum(axis=1)
        for sev in ["PASS", "SOFT_FAIL", "HARD_FAIL"]:
            root_mix[f"{sev.lower()}_pct"] = root_mix[sev] / root_mix["total"].replace(0, pd.NA) * 100.0
        root_mix = root_mix.reset_index()

    rows_series = pd.Series(rows_sample, dtype=float)
    crossed_series = pd.Series(crossed_sample, dtype=float)
    snapshot = pd.DataFrame(
        [
            {
                "current_parquet": str(handle.path),
                "rows_total": int(total_rows),
                "ticker_n": int(len(ticker_seen)),
                "date_min": str(date_min.date()) if date_min is not None else None,
                "date_max": str(date_max.date()) if date_max is not None else None,
                "root_c_rows": int(sum(files for (root, _sev), files in root_severity_counter.items() if root == "C")),
                "root_d_rows": int(sum(files for (root, _sev), files in root_severity_counter.items() if root == "D")),
                "rows_median": float(rows_series.median()) if not rows_series.empty else np.nan,
                "rows_p90": float(rows_series.quantile(0.90)) if not rows_series.empty else np.nan,
                "rows_p99": float(rows_series.quantile(0.99)) if not rows_series.empty else np.nan,
                "crossed_ratio_median_pct": float(crossed_series.median()) if not crossed_series.empty else np.nan,
                "crossed_ratio_p99_pct": float(crossed_series.quantile(0.99)) if not crossed_series.empty else np.nan,
                "timestamp_out_of_partition_rows": int(ts_partition_rows),
            }
        ]
    )

    snapshot.to_parquet(cache_snapshot, index=False)
    sev_counts.to_parquet(cache_severity, index=False)
    root_mix.to_parquet(cache_root, index=False)
    return {"snapshot": snapshot, "severity_counts": sev_counts, "root_mix": root_mix}


def build_root_cause_outputs_cached(handle: QuotesAuditHandle, refresh: bool = False) -> dict[str, pd.DataFrame]:
    cache_hard = handle.cache_path("hard_issue_counts")
    cache_warn = handle.cache_path("warn_counts")
    cache_issue_root = handle.cache_path("issue_root_view")
    cache_warn_sev = handle.cache_path("warn_severity_view")
    if all(path.exists() for path in [cache_hard, cache_warn, cache_issue_root, cache_warn_sev]) and not refresh:
        return {
            "hard_issue_counts": pd.read_parquet(cache_hard),
            "warn_counts": pd.read_parquet(cache_warn),
            "issue_root_view": pd.read_parquet(cache_issue_root),
            "warn_severity_view": pd.read_parquet(cache_warn_sev),
        }

    hard_counter: Counter[str] = Counter()
    warn_counter: Counter[str] = Counter()
    issue_root_counter: Counter[tuple[str, str]] = Counter()
    warn_severity_counter: Counter[tuple[str, str]] = Counter()

    for df in handle.iter_batches(["severity", "root", "issues", "warns"], stage_name="root_cause_scan_lt1b", report_every=10):
        df["issues_list"] = df["issues"].map(_parse_token_list)
        df["warns_list"] = df["warns"].map(_parse_token_list)

        hard = df.loc[df["severity"].eq("HARD_FAIL"), ["root", "issues_list"]]
        _update_counter_from_series(hard_counter, hard["issues_list"])
        _update_counter_from_series(warn_counter, df["warns_list"])

        for _, row in hard.iterrows():
            for issue in row["issues_list"]:
                issue_root_counter[(str(issue), str(row["root"]))] += 1
        for _, row in df.loc[df["warns_list"].map(bool), ["severity", "warns_list"]].iterrows():
            for warn in row["warns_list"]:
                warn_severity_counter[(str(warn), str(row["severity"]))] += 1

        del df, hard
        gc.collect()

    hard_issue_counts = pd.DataFrame(hard_counter.items(), columns=["issue", "files"]).sort_values("files", ascending=False).reset_index(drop=True)
    if not hard_issue_counts.empty:
        hard_issue_counts["pct"] = hard_issue_counts["files"] / hard_issue_counts["files"].sum() * 100.0

    warn_counts = pd.DataFrame(warn_counter.items(), columns=["warn", "files"]).sort_values("files", ascending=False).reset_index(drop=True)
    if not warn_counts.empty:
        warn_counts["pct"] = warn_counts["files"] / warn_counts["files"].sum() * 100.0

    issue_root_view = pd.DataFrame(
        [{"issue": issue, "root": root, "files": files} for (issue, root), files in issue_root_counter.items()]
    ).sort_values(["files", "issue"], ascending=[False, True]).reset_index(drop=True)
    warn_severity_view = pd.DataFrame(
        [{"warn": warn, "severity": severity, "files": files} for (warn, severity), files in warn_severity_counter.items()]
    ).sort_values(["files", "warn"], ascending=[False, True]).reset_index(drop=True)

    hard_issue_counts.to_parquet(cache_hard, index=False)
    warn_counts.to_parquet(cache_warn, index=False)
    issue_root_view.to_parquet(cache_issue_root, index=False)
    warn_severity_view.to_parquet(cache_warn_sev, index=False)
    return {
        "hard_issue_counts": hard_issue_counts,
        "warn_counts": warn_counts,
        "issue_root_view": issue_root_view,
        "warn_severity_view": warn_severity_view,
    }


def build_concentration_inputs_cached(handle: QuotesAuditHandle, refresh: bool = False) -> pd.DataFrame:
    cache_path = handle.cache_path("concentration_inputs")
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    parts: list[pd.DataFrame] = []
    for df in handle.iter_batches(["ticker", "date", "severity"]):
        out = pd.DataFrame(
            {
                "ticker": df["ticker"].astype("string"),
                "date": df["date"],
                "severity": df["severity"].astype("string"),
            }
        )
        out["year"] = out["date"].dt.year
        out["month"] = out["date"].dt.to_period("M").astype(str)
        parts.append(out)
    conc_df = pd.concat(parts, ignore_index=True)
    conc_df.to_parquet(cache_path, index=False)
    return conc_df


def build_concentration_artifacts_cached(handle: QuotesAuditHandle, top_n: int = 30, refresh: bool = False) -> dict[str, pd.DataFrame]:
    cache_month_rate = handle.cache_path("month_rate")
    cache_year_rate = handle.cache_path("year_rate")
    cache_ticker_focus = handle.cache_path(f"ticker_focus_top{top_n}")
    if all(path.exists() for path in [cache_month_rate, cache_year_rate, cache_ticker_focus]) and not refresh:
        return {
            "month_rate": pd.read_parquet(cache_month_rate),
            "year_rate": pd.read_parquet(cache_year_rate),
            "ticker_focus": pd.read_parquet(cache_ticker_focus),
        }

    month_counter: Counter[tuple[str, str]] = Counter()
    year_counter: Counter[tuple[str, str]] = Counter()
    ticker_counter: Counter[tuple[str, str]] = Counter()
    severity_order = ["PASS", "SOFT_FAIL", "HARD_FAIL"]

    for df in handle.iter_batches(["ticker", "date", "severity"], batch_size=100_000, stage_name="concentration_scan_lt1b", report_every=10):
        month = df["date"].dt.to_period("M").astype(str)
        year = df["date"].dt.year.astype("Int64").astype(str)
        for key, value in df.assign(month=month).groupby(["month", "severity"], dropna=False).size().items():
            month_counter[(str(key[0]), str(key[1]))] += int(value)
        for key, value in df.assign(year=year).groupby(["year", "severity"], dropna=False).size().items():
            year_counter[(str(key[0]), str(key[1]))] += int(value)
        for key, value in df.groupby(["ticker", "severity"], dropna=False).size().items():
            ticker_counter[(str(key[0]), str(key[1]))] += int(value)
        del df
        gc.collect()

    month_mix = pd.DataFrame([{"month": month, "severity": sev, "files": files} for (month, sev), files in month_counter.items()])
    month_pivot = month_mix.pivot(index="month", columns="severity", values="files").fillna(0).reindex(columns=severity_order, fill_value=0)
    month_pivot["total"] = month_pivot.sum(axis=1)
    month_rate = month_pivot.assign(
        hard_fail_rate_pct=month_pivot["HARD_FAIL"] / month_pivot["total"].replace(0, pd.NA) * 100.0,
        soft_fail_rate_pct=month_pivot["SOFT_FAIL"] / month_pivot["total"].replace(0, pd.NA) * 100.0,
    ).reset_index()

    year_mix = pd.DataFrame([{"year": year, "severity": sev, "files": files} for (year, sev), files in year_counter.items()])
    year_mix["year_num"] = pd.to_numeric(year_mix["year"], errors="coerce")
    year_pivot = year_mix.pivot(index="year_num", columns="severity", values="files").fillna(0).reindex(columns=severity_order, fill_value=0)
    year_pivot["total"] = year_pivot.sum(axis=1)
    year_rate = year_pivot.assign(
        hard_fail_rate_pct=year_pivot["HARD_FAIL"] / year_pivot["total"].replace(0, pd.NA) * 100.0,
        soft_fail_rate_pct=year_pivot["SOFT_FAIL"] / year_pivot["total"].replace(0, pd.NA) * 100.0,
    ).reset_index().rename(columns={"year_num": "year"})

    ticker_mix = pd.DataFrame([{"ticker": ticker, "severity": sev, "files": files} for (ticker, sev), files in ticker_counter.items()])
    ticker_pivot = ticker_mix.pivot(index="ticker", columns="severity", values="files").fillna(0).reindex(columns=severity_order, fill_value=0)
    ticker_pivot["total"] = ticker_pivot.sum(axis=1)
    ticker_pivot["hard_fail_rate_pct"] = ticker_pivot["HARD_FAIL"] / ticker_pivot["total"].replace(0, pd.NA) * 100.0
    ticker_pivot["soft_fail_rate_pct"] = ticker_pivot["SOFT_FAIL"] / ticker_pivot["total"].replace(0, pd.NA) * 100.0
    ticker_focus = ticker_pivot.sort_values(["HARD_FAIL", "SOFT_FAIL", "total"], ascending=False).head(top_n).reset_index()

    month_rate.to_parquet(cache_month_rate, index=False)
    year_rate.to_parquet(cache_year_rate, index=False)
    ticker_focus.to_parquet(cache_ticker_focus, index=False)
    return {"month_rate": month_rate, "year_rate": year_rate, "ticker_focus": ticker_focus}


def build_microstructure_outputs_cached(
    handle: QuotesAuditHandle,
    refresh: bool = False,
    sample_max_n: int = 250_000,
    top_n: int = 25,
    random_state: int = 7,
) -> dict[str, pd.DataFrame]:
    cache_sample = handle.cache_path("micro_sample")
    cache_crossed = handle.cache_path("crossed_band")
    cache_integer = handle.cache_path("integer_anomaly")
    cache_timestamp = handle.cache_path("timestamp_view")
    if all(path.exists() for path in [cache_sample, cache_crossed, cache_integer, cache_timestamp]) and not refresh:
        return {
            "sample_df": pd.read_parquet(cache_sample),
            "crossed_band": pd.read_parquet(cache_crossed),
            "integer_anomaly_view": pd.read_parquet(cache_integer),
            "timestamp_view": pd.read_parquet(cache_timestamp),
        }

    rng = np.random.default_rng(random_state)
    seen = 0
    sample_parts: list[pd.DataFrame] = []
    band_counter: Counter[tuple[str, str]] = Counter()
    integer_top = pd.DataFrame()
    timestamp_top = pd.DataFrame()

    cols = ["ticker", "date", "root", "severity", "rows", "file", "issues", "warns", "metrics_json"]
    for df in handle.iter_batches(cols, stage_name="microstructure_scan_lt1b", report_every=10):
        metrics = df["metrics_json"].map(_parse_metrics)
        out = pd.DataFrame(
            {
                "ticker": df["ticker"].astype("string"),
                "date": df["date"],
                "root": df["root"].astype("string"),
                "severity": df["severity"].astype("string"),
                "rows": pd.to_numeric(df["rows"], errors="coerce"),
                "file": df["file"].astype("string"),
                "m.crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "m.crossed_rows": pd.to_numeric(metrics.map(lambda x: x.get("crossed_rows")), errors="coerce"),
                "m.ask_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_integer_pct")), errors="coerce"),
                "m.bid_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("bid_integer_pct")), errors="coerce"),
                "m.ask_eq_round_bid_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_eq_round_bid_pct")), errors="coerce"),
                "m.timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
                "m.ts_min_utc": metrics.map(lambda x: x.get("ts_min_utc")),
                "m.ts_max_utc": metrics.map(lambda x: x.get("ts_max_utc")),
                "m.actual_timestamp_dates_utc": metrics.map(lambda x: json.dumps(x.get("actual_timestamp_dates_utc", []))),
            }
        )
        out["issues_list"] = df["issues"].map(_parse_token_list)
        out["warns_list"] = df["warns"].map(_parse_token_list)
        out["issues_primary"] = _first_token(out["issues_list"]).astype("string")
        out["warns_primary"] = _first_token(out["warns_list"]).astype("string")
        out["crossed_bucket"] = pd.cut(
            out["m.crossed_ratio_pct"],
            bins=[-np.inf, 0, 0.01, 0.1, 1, 5, 20, 100, np.inf],
            labels=["0", "(0,0.01]", "(0.01,0.1]", "(0.1,1]", "(1,5]", "(5,20]", "(20,100]", ">100"],
        ).astype("string")

        band_counts = out.groupby(["severity", "crossed_bucket"], dropna=False).size()
        for key, value in band_counts.items():
            band_counter[(str(key[0]), str(key[1]))] += int(value)

        integer_mask = out["m.ask_integer_pct"].fillna(0).ge(80) | out["m.ask_eq_round_bid_pct"].fillna(0).ge(80)
        integer_chunk = (
            out.loc[
                integer_mask,
                [
                    "ticker",
                    "date",
                    "root",
                    "severity",
                    "rows",
                    "m.crossed_ratio_pct",
                    "m.crossed_rows",
                    "m.ask_integer_pct",
                    "m.bid_integer_pct",
                    "m.ask_eq_round_bid_pct",
                    "issues_primary",
                    "warns_primary",
                ],
            ]
        )
        integer_top = _merge_top_n(
            integer_top,
            integer_chunk,
            ["m.ask_integer_pct", "m.ask_eq_round_bid_pct", "m.crossed_ratio_pct"],
            [False, False, False],
            top_n,
        )

        ts_mask = out["m.timestamp_out_of_partition_day"].fillna(False)
        timestamp_chunk = (
            out.loc[
                ts_mask,
                [
                    "ticker",
                    "date",
                    "root",
                    "severity",
                    "rows",
                    "m.ts_min_utc",
                    "m.ts_max_utc",
                    "m.actual_timestamp_dates_utc",
                    "warns_primary",
                ],
            ]
        )
        timestamp_top = _merge_top_n(
            timestamp_top,
            timestamp_chunk,
            ["rows", "ticker", "date"],
            [False, True, True],
            top_n,
        )

        batch_n = len(out)
        if batch_n > 0:
            if seen < sample_max_n:
                take = min(sample_max_n - seen, batch_n)
                sample_parts.append(out.sample(n=take, random_state=int(rng.integers(0, 2**31 - 1))).copy())
                seen += take
            else:
                prob = sample_max_n / max(sample_max_n + batch_n, 1)
                take = int(batch_n * prob)
                if take > 0:
                    sample_parts.append(out.sample(n=min(take, batch_n), random_state=int(rng.integers(0, 2**31 - 1))).copy())

        del df, metrics, out
        gc.collect()

    sample_df = pd.concat(sample_parts, ignore_index=True) if sample_parts else pd.DataFrame()
    if len(sample_df) > sample_max_n:
        sample_df = sample_df.sample(sample_max_n, random_state=random_state).reset_index(drop=True)

    crossed_band = pd.DataFrame(
        [{"severity": sev, "crossed_bucket": bucket, "files": files} for (sev, bucket), files in band_counter.items()]
    )
    integer_anomaly_view = integer_top.reset_index(drop=True)
    timestamp_view = timestamp_top.reset_index(drop=True)
    sample_df.to_parquet(cache_sample, index=False)
    crossed_band.to_parquet(cache_crossed, index=False)
    integer_anomaly_view.to_parquet(cache_integer, index=False)
    timestamp_view.to_parquet(cache_timestamp, index=False)
    return {
        "sample_df": sample_df,
        "crossed_band": crossed_band,
        "integer_anomaly_view": integer_anomaly_view,
        "timestamp_view": timestamp_view,
    }


def build_focus_examples_cached(
    handle: QuotesAuditHandle,
    hard_issue_counts: pd.DataFrame,
    warn_counts: pd.DataFrame,
    top_n: int = 20,
    refresh: bool = False,
):
    focus_issue = hard_issue_counts.iloc[0]["issue"] if not hard_issue_counts.empty else None
    focus_warn = warn_counts.iloc[0]["warn"] if not warn_counts.empty else None
    cache_path = handle.cache_path(f"focus_examples_{_slug([focus_issue, focus_warn, top_n])}")
    if cache_path.exists() and not refresh:
        cached = pd.read_parquet(cache_path)
        issue_examples = cached.loc[cached["example_kind"].eq("issue")].drop(columns=["example_kind"]).reset_index(drop=True)
        warn_examples = cached.loc[cached["example_kind"].eq("warn")].drop(columns=["example_kind"]).reset_index(drop=True)
        return focus_issue, focus_warn, issue_examples, warn_examples

    issue_parts: list[pd.DataFrame] = []
    warn_parts: list[pd.DataFrame] = []
    cols = ["ticker", "date", "root", "severity", "rows", "file", "issues", "warns", "metrics_json"]
    for df in handle.iter_batches(cols, stage_name="focus_examples_scan_lt1b", report_every=10):
        metrics = df["metrics_json"].map(_parse_metrics)
        out = pd.DataFrame(
            {
                "ticker": df["ticker"].astype("string"),
                "date": df["date"],
                "root": df["root"].astype("string"),
                "severity": df["severity"].astype("string"),
                "rows": pd.to_numeric(df["rows"], errors="coerce"),
                "file": df["file"].astype("string"),
                "m.crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "m.crossed_rows": pd.to_numeric(metrics.map(lambda x: x.get("crossed_rows")), errors="coerce"),
                "m.ask_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_integer_pct")), errors="coerce"),
                "m.ask_eq_round_bid_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_eq_round_bid_pct")), errors="coerce"),
                "m.timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
            }
        )
        out["issues_primary"] = df["issues"].map(lambda x: (_parse_token_list(x) or [None])[0]).astype("string")
        out["warns_primary"] = df["warns"].map(lambda x: (_parse_token_list(x) or [None])[0]).astype("string")

        if focus_issue is not None:
            issue_parts.append(out.loc[out["issues_primary"].eq(focus_issue)])
        if focus_warn is not None:
            warn_parts.append(out.loc[out["warns_primary"].eq(focus_warn)])

        del df, metrics, out
        gc.collect()

    issue_examples = pd.DataFrame()
    for part in issue_parts:
        issue_examples = _merge_top_n(issue_examples, part, ["m.crossed_ratio_pct", "rows"], [False, False], top_n)
    warn_examples = pd.DataFrame()
    for part in warn_parts:
        warn_examples = _merge_top_n(warn_examples, part, ["m.crossed_ratio_pct", "rows"], [False, False], top_n)

    to_cache = pd.concat(
        [
            issue_examples.assign(example_kind="issue"),
            warn_examples.assign(example_kind="warn"),
        ],
        ignore_index=True,
    )
    to_cache.to_parquet(cache_path, index=False)
    return focus_issue, focus_warn, issue_examples, warn_examples


def build_forensic_candidates_cached(
    handle: QuotesAuditHandle,
    initial_focus: str = "HARD_FAIL",
    top_n: int = 20,
    refresh: bool = False,
) -> pd.DataFrame:
    cache_path = handle.cache_path(f"forensic_candidates_{_slug([initial_focus, top_n])}")
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    ranked = pd.DataFrame()
    cols = ["ticker", "date", "root", "severity", "rows", "file", "metrics_json"]
    for df in handle.iter_batches(cols, stage_name="forensic_scan_lt1b", report_every=10):
        metrics = df["metrics_json"].map(_parse_metrics)
        out = pd.DataFrame(
            {
                "ticker": df["ticker"].astype("string"),
                "date": df["date"],
                "root": df["root"].astype("string"),
                "severity": df["severity"].astype("string"),
                "rows": pd.to_numeric(df["rows"], errors="coerce"),
                "file": df["file"].astype("string"),
                "m.crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "m.crossed_rows": pd.to_numeric(metrics.map(lambda x: x.get("crossed_rows")), errors="coerce"),
                "m.ask_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_integer_pct")), errors="coerce"),
                "m.ask_eq_round_bid_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_eq_round_bid_pct")), errors="coerce"),
                "m.timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
            }
        )

        if initial_focus == "HARD_FAIL":
            out = out.loc[out["severity"].eq("HARD_FAIL")]
        elif initial_focus == "TIMESTAMP":
            out = out.loc[out["m.timestamp_out_of_partition_day"].fillna(False)]

        if not out.empty:
            ranked = _merge_top_n(
                ranked,
                out,
                ["m.crossed_ratio_pct", "rows"],
                [False, False],
                top_n,
            )

        del df, metrics, out
        gc.collect()

    ranked = ranked.reset_index(drop=True)
    ranked.to_parquet(cache_path, index=False)
    return ranked


def build_taxonomy_summary_cached(handle: QuotesAuditHandle, refresh: bool = False) -> pd.DataFrame:
    cache_path = handle.cache_path("taxonomy_summary")
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    counter: Counter[str] = Counter()
    ticker_sets: dict[str, set[str]] = {}
    date_sets: dict[str, set[pd.Timestamp]] = {}
    hard_counter: Counter[str] = Counter()
    soft_counter: Counter[str] = Counter()
    crossed_values: dict[str, list[float]] = {}
    crossed_seen: dict[str, int] = {}
    rng = np.random.default_rng(11)

    for df in handle.iter_batches(
        ["ticker", "date", "severity", "rows", "issues", "warns", "metrics_json"],
        stage_name="taxonomy_scan_lt1b",
        report_every=10,
    ):
        metrics = df["metrics_json"].map(_parse_metrics)
        work = pd.DataFrame(
            {
                "ticker": df["ticker"].astype(str),
                "date": df["date"],
                "severity": df["severity"].astype(str),
                "rows": pd.to_numeric(df["rows"], errors="coerce"),
                "m.crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "m.crossed_rows": pd.to_numeric(metrics.map(lambda x: x.get("crossed_rows")), errors="coerce"),
                "m.ask_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_integer_pct")), errors="coerce"),
                "m.ask_eq_round_bid_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_eq_round_bid_pct")), errors="coerce"),
                "m.timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
            }
        )
        work["taxonomy"] = _classify_quotes_taxonomy_v21(work)

        for taxonomy, sub in work.groupby("taxonomy", dropna=False):
            taxonomy = str(taxonomy)
            counter[taxonomy] += len(sub)
            ticker_sets.setdefault(taxonomy, set()).update(sub["ticker"].dropna().astype(str).tolist())
            date_sets.setdefault(taxonomy, set()).update(sub["date"].dropna().tolist())
            hard_counter[taxonomy] += int(sub["severity"].eq("HARD_FAIL").sum())
            soft_counter[taxonomy] += int(sub["severity"].eq("SOFT_FAIL").sum())
            crossed_values.setdefault(taxonomy, [])
            crossed_seen.setdefault(taxonomy, 0)
            crossed_seen[taxonomy] = _reservoir_extend(
                crossed_values[taxonomy],
                sub["m.crossed_ratio_pct"].dropna().astype(float).tolist(),
                crossed_seen[taxonomy],
                100_000,
                rng,
            )

        del df, metrics, work
        gc.collect()

    rows = []
    total = sum(counter.values())
    for taxonomy, files in counter.most_common():
        crossed = pd.Series(crossed_values.get(taxonomy, []), dtype=float)
        rows.append(
            {
                "taxonomy": taxonomy,
                "files": int(files),
                "tickers": int(len(ticker_sets.get(taxonomy, set()))),
                "dates": int(len(date_sets.get(taxonomy, set()))),
                "hard_fail_files": int(hard_counter.get(taxonomy, 0)),
                "soft_fail_files": int(soft_counter.get(taxonomy, 0)),
                "crossed_ratio_median_pct": float(crossed.median()) if not crossed.empty else np.nan,
                "crossed_ratio_p90_pct": float(crossed.quantile(0.9)) if not crossed.empty else np.nan,
                "pct": float(files / max(total, 1) * 100.0),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_parquet(cache_path, index=False)
    return summary


def build_case_index_cached(
    handle: QuotesAuditHandle,
    hard_issue_counts: pd.DataFrame,
    warn_counts: pd.DataFrame,
    top_n_per_block: int = 50,
    refresh: bool = False,
) -> pd.DataFrame:
    cache_path = handle.cache_path(f"case_index_top{top_n_per_block}")
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    focus_issue, focus_warn, issue_examples, warn_examples = build_focus_examples_cached(
        handle,
        hard_issue_counts,
        warn_counts,
        top_n=top_n_per_block,
        refresh=refresh,
    )
    forensic = build_forensic_candidates_cached(
        handle,
        initial_focus="HARD_FAIL",
        top_n=top_n_per_block,
        refresh=refresh,
    )

    issue_index = issue_examples.assign(
        block="issue_examples",
        group_key=focus_issue,
        group_label=focus_issue,
        focus_issue=focus_issue,
        focus_warn=None,
        taxonomy=_classify_quotes_taxonomy_v21(issue_examples),
        rank_score=pd.to_numeric(issue_examples.get("m.crossed_ratio_pct"), errors="coerce").fillna(0),
        display_label=issue_examples["ticker"].astype(str) + " | " + issue_examples["date"].astype(str) + " | issue",
        source_population="focus_issue",
    )
    warn_index = warn_examples.assign(
        block="warn_examples",
        group_key=focus_warn,
        group_label=focus_warn,
        focus_issue=None,
        focus_warn=focus_warn,
        taxonomy=_classify_quotes_taxonomy_v21(warn_examples),
        rank_score=pd.to_numeric(warn_examples.get("m.crossed_ratio_pct"), errors="coerce").fillna(0),
        display_label=warn_examples["ticker"].astype(str) + " | " + warn_examples["date"].astype(str) + " | warn",
        source_population="focus_warn",
    )
    forensic_index = forensic.assign(
        block="forensic",
        group_key=forensic["severity"].astype(str),
        group_label=forensic["severity"].astype(str),
        focus_issue=None,
        focus_warn=None,
        taxonomy=_classify_quotes_taxonomy_v21(forensic),
        rank_score=pd.to_numeric(forensic.get("m.crossed_ratio_pct"), errors="coerce").fillna(0),
        display_label=forensic["ticker"].astype(str) + " | " + forensic["date"].astype(str) + " | forensic",
        source_population="hard_fail_candidates",
    )

    keep_cols = [
        "block",
        "group_key",
        "group_label",
        "taxonomy",
        "focus_issue",
        "focus_warn",
        "severity",
        "root",
        "ticker",
        "date",
        "file",
        "rows",
        "m.crossed_ratio_pct",
        "m.crossed_rows",
        "m.timestamp_out_of_partition_day",
        "m.ask_integer_pct",
        "m.ask_eq_round_bid_pct",
        "rank_score",
        "display_label",
        "source_population",
    ]
    case_index = pd.concat([issue_index, warn_index, forensic_index], ignore_index=True, sort=False)
    for col in keep_cols:
        if col not in case_index.columns:
            case_index[col] = pd.NA
    case_index = case_index.loc[:, keep_cols].sort_values(["block", "rank_score"], ascending=[True, False]).reset_index(drop=True)
    case_index.to_parquet(cache_path, index=False)
    return case_index


def build_crossed_gap_severity_cached(
    handle: QuotesAuditHandle,
    sample_per_taxonomy: int = 40,
    random_state: int = 17,
    refresh: bool = False,
) -> dict[str, pd.DataFrame]:
    cache_summary = handle.cache_path("crossed_gap_severity_summary")
    cache_cases = handle.cache_path("crossed_gap_severity_cases")
    if cache_summary.exists() and cache_cases.exists() and not refresh:
        return {
            "crossed_gap_severity_summary": pd.read_parquet(cache_summary),
            "crossed_gap_severity_cases": pd.read_parquet(cache_cases),
        }

    sample_df = build_microstructure_outputs_cached(handle, refresh=False)["sample_df"].copy()
    if sample_df.empty:
        empty = pd.DataFrame()
        empty.to_parquet(cache_summary, index=False)
        empty.to_parquet(cache_cases, index=False)
        return {
            "crossed_gap_severity_summary": empty,
            "crossed_gap_severity_cases": empty,
        }

    sample_df["taxonomy"] = _classify_quotes_taxonomy_v21(sample_df)
    sample_df = sample_df.loc[pd.to_numeric(sample_df["m.crossed_rows"], errors="coerce").fillna(0).gt(0)].copy()
    if sample_df.empty:
        empty = pd.DataFrame()
        empty.to_parquet(cache_summary, index=False)
        empty.to_parquet(cache_cases, index=False)
        return {
            "crossed_gap_severity_summary": empty,
            "crossed_gap_severity_cases": empty,
        }

    rng = np.random.default_rng(random_state)
    picked_parts: list[pd.DataFrame] = []
    for taxonomy, sub in sample_df.groupby("taxonomy", dropna=False):
        sub = sub.copy()
        take_n = min(sample_per_taxonomy, len(sub))
        if take_n <= 0:
            continue
        picked_parts.append(sub.sample(n=take_n, random_state=int(rng.integers(0, 2**31 - 1))).copy())
    picked = pd.concat(picked_parts, ignore_index=True) if picked_parts else pd.DataFrame()
    if picked.empty:
        empty = pd.DataFrame()
        empty.to_parquet(cache_summary, index=False)
        empty.to_parquet(cache_cases, index=False)
        return {
            "crossed_gap_severity_summary": empty,
            "crossed_gap_severity_cases": empty,
        }

    case_rows: list[dict[str, Any]] = []
    total = len(picked)
    for idx, row in picked.reset_index(drop=True).iterrows():
        if (idx + 1) % 25 == 0 or (idx + 1) == total:
            print(json.dumps({"stage": "crossed_gap_severity_scan_lt1b", "sample_files_done": int(idx + 1), "sample_files_total": int(total)}))
        metrics = _compute_cross_gap_metrics_from_file(row["file"])
        case_rows.append(
            {
                "taxonomy": row["taxonomy"],
                "ticker": row["ticker"],
                "date": row["date"],
                "root": row["root"],
                "severity": row["severity"],
                "rows": row["rows"],
                "file": row["file"],
                "m.crossed_ratio_pct": row["m.crossed_ratio_pct"],
                "m.crossed_rows": row["m.crossed_rows"],
                "m.ask_integer_pct": row["m.ask_integer_pct"],
                **metrics,
            }
        )
    cases = pd.DataFrame(case_rows)

    if cases.empty:
        summary = pd.DataFrame()
    else:
        summary = (
            cases.groupby("taxonomy", dropna=False)
            .agg(
                sample_files=("file", "count"),
                sample_tickers=("ticker", "nunique"),
                crossed_ratio_pct_median=("m.crossed_ratio_pct", "median"),
                crossed_ratio_pct_p90=("m.crossed_ratio_pct", lambda s: float(pd.Series(s).quantile(0.9))),
                cross_abs_median=("cross_abs_median", "median"),
                cross_abs_p90=("cross_abs_p90", lambda s: float(pd.Series(s).quantile(0.9))),
                cross_rel_bps_median=("cross_rel_bps_median", "median"),
                cross_rel_bps_p90=("cross_rel_bps_p90", lambda s: float(pd.Series(s).quantile(0.9))),
                crossed_ask_zero_share_pct_median=("crossed_ask_zero_share_pct", "median"),
                crossed_ask_positive_share_pct_median=("crossed_ask_positive_share_pct", "median"),
                cross_abs_median_ask_positive=("cross_abs_median_ask_positive", "median"),
                cross_abs_p90_ask_positive=("cross_abs_p90_ask_positive", lambda s: float(pd.Series(s).quantile(0.9))),
                cross_rel_bps_median_ask_positive=("cross_rel_bps_median_ask_positive", "median"),
                cross_rel_bps_p90_ask_positive=("cross_rel_bps_p90_ask_positive", lambda s: float(pd.Series(s).quantile(0.9))),
                near_zero_share_pct_median=("near_zero_share_pct", "median"),
                mild_share_pct_median=("mild_share_pct", "median"),
                moderate_share_pct_median=("moderate_share_pct", "median"),
                severe_share_pct_median=("severe_share_pct", "median"),
                near_zero_share_pct_ask_positive_median=("near_zero_share_pct_ask_positive", "median"),
                mild_share_pct_ask_positive_median=("mild_share_pct_ask_positive", "median"),
                moderate_share_pct_ask_positive_median=("moderate_share_pct_ask_positive", "median"),
                severe_share_pct_ask_positive_median=("severe_share_pct_ask_positive", "median"),
                crossed_rows_raw_total=("crossed_rows_raw", "sum"),
                crossed_rows_ask_zero_total=("crossed_rows_ask_zero", "sum"),
                crossed_rows_ask_positive_total=("crossed_rows_ask_positive", "sum"),
                crossed_area_abs_total=("crossed_area_abs", "sum"),
            )
            .reset_index()
            .sort_values(["sample_files", "crossed_ratio_pct_median"], ascending=[False, False])
            .reset_index(drop=True)
        )

    cases.to_parquet(cache_cases, index=False)
    summary.to_parquet(cache_summary, index=False)
    return {
        "crossed_gap_severity_summary": summary,
        "crossed_gap_severity_cases": cases,
    }


def build_positive_cross_review_cached(
    handle: QuotesAuditHandle,
    refresh: bool = False,
) -> dict[str, pd.DataFrame]:
    cache_summary = handle.cache_path("positive_cross_review_summary")
    cache_cases = handle.cache_path("positive_cross_review_cases")
    if cache_summary.exists() and cache_cases.exists() and not refresh:
        return {
            "positive_cross_review_summary": pd.read_parquet(cache_summary),
            "positive_cross_review_cases": pd.read_parquet(cache_cases),
        }

    cases = build_crossed_gap_severity_cached(handle, refresh=False)["crossed_gap_severity_cases"].copy()
    if cases.empty:
        empty = pd.DataFrame()
        empty.to_parquet(cache_summary, index=False)
        empty.to_parquet(cache_cases, index=False)
        return {
            "positive_cross_review_summary": empty,
            "positive_cross_review_cases": empty,
        }

    focus_taxonomies = {
        "large_file_threshold_edge_hard_many_crosses",
        "persistent_soft_crossed_mid_large_scale",
        "high_hard_crossed_10_to_20",
        "medium_file_threshold_edge_hard_many_crosses",
    }
    work = cases.loc[cases["taxonomy"].astype(str).isin(focus_taxonomies)].copy()
    work = work.loc[pd.to_numeric(work["crossed_rows_ask_positive"], errors="coerce").fillna(0).gt(0)].copy()
    if work.empty:
        empty = pd.DataFrame()
        empty.to_parquet(cache_summary, index=False)
        empty.to_parquet(cache_cases, index=False)
        return {
            "positive_cross_review_summary": empty,
            "positive_cross_review_cases": empty,
        }

    bps = pd.to_numeric(work["cross_rel_bps_median_ask_positive"], errors="coerce")
    conditions = [
        bps.lt(5),
        bps.ge(5) & bps.lt(25),
        bps.ge(25),
    ]
    choices = [
        "positive_cross_mild_lt5bps",
        "positive_cross_moderate_5to25bps",
        "positive_cross_severe_ge25bps",
    ]
    work["positive_cross_bucket"] = pd.Series(np.select(conditions, choices, default="positive_cross_unknown"), index=work.index, dtype="string")

    summary = (
        work.groupby(["taxonomy", "positive_cross_bucket"], dropna=False)
        .agg(
            sample_files=("file", "count"),
            sample_tickers=("ticker", "nunique"),
            crossed_ask_zero_share_pct_median=("crossed_ask_zero_share_pct", "median"),
            crossed_ask_positive_share_pct_median=("crossed_ask_positive_share_pct", "median"),
            cross_rel_bps_median_ask_positive=("cross_rel_bps_median_ask_positive", "median"),
            cross_rel_bps_p90_ask_positive=("cross_rel_bps_p90_ask_positive", lambda s: float(pd.Series(s).quantile(0.9))),
            mild_share_pct_ask_positive_median=("mild_share_pct_ask_positive", "median"),
            moderate_share_pct_ask_positive_median=("moderate_share_pct_ask_positive", "median"),
            severe_share_pct_ask_positive_median=("severe_share_pct_ask_positive", "median"),
        )
        .reset_index()
        .sort_values(["taxonomy", "cross_rel_bps_median_ask_positive"], ascending=[True, False])
        .reset_index(drop=True)
    )

    work.to_parquet(cache_cases, index=False)
    summary.to_parquet(cache_summary, index=False)
    return {
        "positive_cross_review_summary": summary,
        "positive_cross_review_cases": work,
    }


def build_quotes_cd_artifacts(handle: QuotesAuditHandle, refresh: bool = False) -> dict[str, Any]:
    print(json.dumps({"stage": "snapshot_artifacts_lt1b", "status": "started"}))
    snapshot_payload = build_snapshot_artifacts_cached(handle, refresh=refresh)
    print(json.dumps({"stage": "snapshot_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "root_cause_artifacts_lt1b", "status": "started"}))
    root_payload = build_root_cause_outputs_cached(handle, refresh=refresh)
    print(json.dumps({"stage": "root_cause_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "concentration_artifacts_lt1b", "status": "started"}))
    concentration_payload = build_concentration_artifacts_cached(handle, top_n=30, refresh=refresh)
    print(json.dumps({"stage": "concentration_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "microstructure_artifacts_lt1b", "status": "started"}))
    micro_payload = build_microstructure_outputs_cached(handle, sample_max_n=250_000, top_n=25, random_state=7, refresh=refresh)
    print(json.dumps({"stage": "microstructure_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "focus_examples_artifacts_lt1b", "status": "started"}))
    focus_issue, focus_warn, issue_examples, warn_examples = build_focus_examples_cached(
        handle,
        root_payload["hard_issue_counts"],
        root_payload["warn_counts"],
        top_n=20,
        refresh=refresh,
    )
    print(json.dumps({"stage": "focus_examples_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "forensic_artifacts_lt1b", "status": "started"}))
    forensic_candidates = build_forensic_candidates_cached(handle, initial_focus="HARD_FAIL", top_n=20, refresh=refresh)
    print(json.dumps({"stage": "forensic_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "taxonomy_artifacts_lt1b", "status": "started"}))
    taxonomy_summary = build_taxonomy_summary_cached(handle, refresh=refresh)
    print(json.dumps({"stage": "taxonomy_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "case_index_artifacts_lt1b", "status": "started"}))
    case_index = build_case_index_cached(handle, root_payload["hard_issue_counts"], root_payload["warn_counts"], top_n_per_block=50, refresh=refresh)
    print(json.dumps({"stage": "case_index_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "crossed_gap_severity_artifacts_lt1b", "status": "started"}))
    crossed_gap_payload = build_crossed_gap_severity_cached(handle, refresh=refresh)
    print(json.dumps({"stage": "crossed_gap_severity_artifacts_lt1b", "status": "completed"}))
    print(json.dumps({"stage": "positive_cross_review_artifacts_lt1b", "status": "started"}))
    positive_cross_payload = build_positive_cross_review_cached(handle, refresh=refresh)
    print(json.dumps({"stage": "positive_cross_review_artifacts_lt1b", "status": "completed"}))

    return {
        **snapshot_payload,
        **root_payload,
        **concentration_payload,
        **micro_payload,
        "focus_issue": focus_issue,
        "focus_warn": focus_warn,
        "issue_examples": issue_examples,
        "warn_examples": warn_examples,
        "forensic_candidates": forensic_candidates,
        "taxonomy_summary": taxonomy_summary,
        "case_index": case_index,
        **crossed_gap_payload,
        **positive_cross_payload,
    }


def write_manifest(handle: QuotesAuditHandle, refresh: bool = False) -> dict[str, Any]:
    manifest_path = handle.cache_path("manifest", suffix=".json")
    if manifest_path.exists() and not refresh:
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    artifacts = sorted([path.name for path in handle.cache_dir.glob(f"*_{handle.label}.parquet")])
    manifest = {
        "builder_version": "quotes_cd_lt1b_v2",
        "source_parquet": str(handle.path),
        "source_size_bytes": int(handle.path.stat().st_size),
        "source_mtime_utc": pd.Timestamp(handle.path.stat().st_mtime, unit="s", tz="UTC").isoformat(),
        "row_count_source_full": handle.row_count(),
        "target_lt1b_path": None if handle.target_path is None else str(handle.target_path),
        "target_lt1b_tickers": None if handle.target_tickers is None else len(handle.target_tickers),
        "cache_dir": str(handle.cache_dir),
        "artifacts": artifacts,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
