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
        r"C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache",
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

    def parquet(self) -> pq.ParquetFile:
        return pq.ParquetFile(self.path)

    def row_count(self) -> int:
        return int(self.parquet().metadata.num_rows)

    def file_size_mb(self) -> float:
        return round(self.path.stat().st_size / 1024 / 1024, 2)

    def iter_batches(self, columns: list[str], batch_size: int = 200_000):
        pf = self.parquet()
        for batch in pf.iter_batches(columns=columns, batch_size=batch_size):
            df = batch.to_pandas()
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            yield df

    def cache_path(self, stem: str, suffix: str = ".parquet") -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir / f"{stem}_{self.label}{suffix}"


def load_quotes_artifacts() -> dict[str, Any]:
    handle_cd = QuotesAuditHandle(CURRENT_PARQUET_CD, "cd", CACHE_DIR)
    handle_d = QuotesAuditHandle(CURRENT_PARQUET_D, "d", CACHE_DIR)
    handle_c = QuotesAuditHandle(CURRENT_PARQUET_C, "c", CACHE_DIR)
    return {
        "current_parquet_cd": CURRENT_PARQUET_CD,
        "current_parquet_d": CURRENT_PARQUET_D,
        "current_parquet_c": CURRENT_PARQUET_C,
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
### Loader quotes C+D

- current final `C + D`: `{cd.path}`
- current D: `{d.path}`
- current C: `{c.path}`
- rows C+D: `{cd.row_count():,}` | parquet `{cd.file_size_mb():,.2f} MB`
- rows D: `{d.row_count():,}` | parquet `{d.file_size_mb():,.2f} MB`
- rows C: `{c.row_count():,}` | parquet `{c.file_size_mb():,.2f} MB`
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
    for df in handle.iter_batches(cols, batch_size=50_000):
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

    for df in handle.iter_batches(["severity", "root", "issues", "warns"]):
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

    for df in handle.iter_batches(["ticker", "date", "severity"], batch_size=100_000):
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
    for df in handle.iter_batches(cols):
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
    for df in handle.iter_batches(cols):
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
    for df in handle.iter_batches(cols):
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

    for df in handle.iter_batches(["ticker", "date", "severity", "rows", "issues", "warns", "metrics_json"]):
        metrics = df["metrics_json"].map(_parse_metrics)
        work = pd.DataFrame(
            {
                "ticker": df["ticker"].astype(str),
                "date": df["date"],
                "severity": df["severity"].astype(str),
                "rows": pd.to_numeric(df["rows"], errors="coerce"),
                "m.crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "m.ask_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_integer_pct")), errors="coerce"),
                "m.ask_eq_round_bid_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_eq_round_bid_pct")), errors="coerce"),
                "m.timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
            }
        )
        work["issues_list"] = df["issues"].map(_parse_token_list)
        work["warns_list"] = df["warns"].map(_parse_token_list)

        conditions = [
            work.apply(lambda row: "ask_integer_with_crossed_anomaly" in set(row["issues_list"]) or ((row["m.ask_integer_pct"] or 0) >= 95 and (row["m.crossed_ratio_pct"] or 0) > 20), axis=1),
            work.apply(lambda row: "crossed_ratio_gt_hard_cap" in set(row["issues_list"]) or (row["m.crossed_ratio_pct"] or 0) > 5, axis=1),
            work.apply(lambda row: "crossed_ratio_gt_threshold" in set(row["issues_list"]) and (row["rows"] or 0) <= 100, axis=1),
            work.apply(lambda row: "crossed_ratio_gt_threshold" in set(row["issues_list"]), axis=1),
            work.apply(lambda row: bool(row["m.timestamp_out_of_partition_day"]) and "crossed_rows_present_but_under_threshold" in set(row["warns_list"]), axis=1),
            work["m.timestamp_out_of_partition_day"].fillna(False),
            work.apply(lambda row: "crossed_rows_present_but_under_threshold" in set(row["warns_list"]) and (row["m.crossed_ratio_pct"] or 0) <= 0.1, axis=1),
            work.apply(lambda row: "crossed_rows_present_but_under_threshold" in set(row["warns_list"]), axis=1),
            work["m.ask_eq_round_bid_pct"].fillna(0).ge(80),
        ]
        choices = [
            "integerized_crossed_anomaly",
            "hard_crossed_market",
            "small_file_hard_crossed",
            "moderate_crossed_market",
            "soft_crossed_plus_timestamp_shift",
            "timestamp_partition_shift",
            "mild_crossed_micro_noise",
            "persistent_soft_crossed_market",
            "rounded_ask_pattern_without_cross_hard",
        ]
        work["taxonomy"] = np.select(conditions, choices, default="clean_pass_or_other")

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
        taxonomy=None,
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
        taxonomy=None,
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
        taxonomy=None,
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


def build_quotes_cd_artifacts(handle: QuotesAuditHandle, refresh: bool = False) -> dict[str, Any]:
    snapshot_payload = build_snapshot_artifacts_cached(handle, refresh=refresh)
    root_payload = build_root_cause_outputs_cached(handle, refresh=refresh)
    concentration_payload = build_concentration_artifacts_cached(handle, top_n=30, refresh=refresh)
    micro_payload = build_microstructure_outputs_cached(handle, sample_max_n=250_000, top_n=25, random_state=7, refresh=refresh)
    focus_issue, focus_warn, issue_examples, warn_examples = build_focus_examples_cached(
        handle,
        root_payload["hard_issue_counts"],
        root_payload["warn_counts"],
        top_n=20,
        refresh=refresh,
    )
    forensic_candidates = build_forensic_candidates_cached(handle, initial_focus="HARD_FAIL", top_n=20, refresh=refresh)
    taxonomy_summary = build_taxonomy_summary_cached(handle, refresh=refresh)
    case_index = build_case_index_cached(handle, root_payload["hard_issue_counts"], root_payload["warn_counts"], top_n_per_block=50, refresh=refresh)

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
    }


def write_manifest(handle: QuotesAuditHandle, refresh: bool = False) -> dict[str, Any]:
    manifest_path = handle.cache_path("manifest", suffix=".json")
    if manifest_path.exists() and not refresh:
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    artifacts = sorted([path.name for path in handle.cache_dir.glob(f"*_{handle.label}.parquet")])
    manifest = {
        "builder_version": "quotes_cd_v1",
        "source_parquet": str(handle.path),
        "source_size_bytes": int(handle.path.stat().st_size),
        "source_mtime_utc": pd.Timestamp(handle.path.stat().st_mtime, unit="s", tz="UTC").isoformat(),
        "row_count": handle.row_count(),
        "cache_dir": str(handle.cache_dir),
        "artifacts": artifacts,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
