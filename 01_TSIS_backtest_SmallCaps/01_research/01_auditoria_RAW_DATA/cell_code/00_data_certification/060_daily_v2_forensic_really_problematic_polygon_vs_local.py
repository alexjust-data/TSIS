from __future__ import annotations

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://api.polygon.io"
_THREAD_LOCAL = threading.local()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = (
            Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit")
            / f"{stamp}_daily_forensic_really_problematic"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def get_session(api_key: str) -> requests.Session:
    sess = getattr(_THREAD_LOCAL, "session", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update({"Authorization": f"Bearer {api_key}"})
        _THREAD_LOCAL.session = sess
    return sess


def load_problematic_tickers(path: Path) -> set[str]:
    if not path.exists():
        raise FileNotFoundError(f"Problematic parquet not found: {path}")
    df = pd.read_parquet(path, columns=["ticker"]).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    return set(df.loc[df["ticker"] != "", "ticker"].drop_duplicates().tolist())


def load_tasks(path: Path, problematic: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Tasks parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "year"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Missing required columns in tasks parquet: {required}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ticker", "year"]).copy()
    df["year"] = df["year"].astype(int)
    df = df[df["ticker"].isin(problematic)].copy()
    if "task_key" not in df.columns:
        df["task_key"] = df["ticker"] + "|" + df["year"].astype(str)
    if "date_from" not in df.columns:
        df["date_from"] = df["year"].astype(str) + "-01-01"
    if "date_to" not in df.columns:
        df["date_to"] = df["year"].astype(str) + "-12-31"
    return df.sort_values(["ticker", "year"], ascending=[True, True]).reset_index(drop=True)


def load_ticker_audit(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Ticker audit CSV not found: {path}")
    df = pd.read_csv(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError("Ticker audit CSV missing ticker column")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    for col in ["http_status", "rows", "pages"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def local_file_info(outdir: Path, ticker: str, year: int) -> dict[str, Any]:
    path = outdir / f"ticker={ticker}" / f"year={year}" / f"day_aggs_{ticker}_{year}.parquet"
    exists = path.exists()
    rows = None
    date_min = None
    date_max = None
    size_bytes = None
    read_ok = None
    if exists:
        size_bytes = int(path.stat().st_size)
        try:
            d = pd.read_parquet(path, columns=[c for c in ["date"]])
            rows = int(len(d))
            if "date" in d.columns and not d.empty:
                s = d["date"].dropna().astype(str)
                if not s.empty:
                    date_min = str(s.min())
                    date_max = str(s.max())
            read_ok = True
        except Exception:
            read_ok = False
    return {
        "target_path": str(path),
        "file_exists_local": bool(exists),
        "local_rows": rows,
        "local_date_min": date_min,
        "local_date_max": date_max,
        "local_size_bytes": size_bytes,
        "local_read_ok": read_ok,
    }


def request_json_with_retry(
    sess: requests.Session,
    url: str,
    params: dict[str, Any],
    timeout: int,
    max_retries: int,
    backoff_base: float,
    backoff_max: float,
) -> tuple[dict[str, Any] | None, int, str]:
    last_status = 0
    last_msg = "unknown"
    for attempt in range(max_retries + 1):
        try:
            resp = sess.get(url, params=params, timeout=timeout)
            last_status = int(resp.status_code)
            if resp.status_code == 200:
                return resp.json(), 200, "ok"
            last_msg = resp.text[:500]
            if resp.status_code not in (429, 500, 502, 503, 504):
                return None, int(resp.status_code), last_msg
        except Exception as exc:
            last_msg = str(exc)
        if attempt < max_retries:
            sleep_s = min(backoff_max, backoff_base * (2**attempt))
            time.sleep(sleep_s)
    return None, last_status, last_msg


def fetch_polygon_year(
    *,
    api_key: str,
    ticker: str,
    start: str,
    end: str,
    adjusted: bool,
    limit: int,
    timeout: int,
    max_pages: int,
    max_retries: int,
    backoff_base: float,
    backoff_max: float,
) -> dict[str, Any]:
    sess = get_session(api_key)
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
    params = {
        "adjusted": str(adjusted).lower(),
        "sort": "asc",
        "limit": limit,
        "apiKey": api_key,
    }

    pages = 0
    rows_total = 0
    ts_min = None
    ts_max = None
    first_o = None
    last_c = None
    status = 200
    msg = "ok"

    while True:
        pages += 1
        payload, status, msg = request_json_with_retry(
            sess=sess,
            url=url,
            params=params,
            timeout=timeout,
            max_retries=max_retries,
            backoff_base=backoff_base,
            backoff_max=backoff_max,
        )
        if status != 200 or payload is None:
            return {
                "polygon_http_status": int(status),
                "polygon_msg": str(msg),
                "polygon_pages": int(pages),
                "polygon_rows_returned": None,
                "polygon_first_date": None,
                "polygon_last_date": None,
                "polygon_first_o": None,
                "polygon_last_c": None,
            }

        results = payload.get("results") or []
        if results:
            rows_total += len(results)
            t0 = results[0].get("t")
            t1 = results[-1].get("t")
            if t0 is not None:
                ts_min = t0 if ts_min is None else min(ts_min, t0)
            if t1 is not None:
                ts_max = t1 if ts_max is None else max(ts_max, t1)
            if first_o is None and "o" in results[0]:
                first_o = results[0].get("o")
            if "c" in results[-1]:
                last_c = results[-1].get("c")

        next_url = payload.get("next_url")
        if not next_url:
            break
        if pages >= max_pages:
            return {
                "polygon_http_status": 206,
                "polygon_msg": f"partial:max_pages={max_pages}",
                "polygon_pages": int(pages),
                "polygon_rows_returned": int(rows_total),
                "polygon_first_date": (
                    pd.to_datetime(ts_min, unit="ms", utc=True).strftime("%Y-%m-%d") if ts_min is not None else None
                ),
                "polygon_last_date": (
                    pd.to_datetime(ts_max, unit="ms", utc=True).strftime("%Y-%m-%d") if ts_max is not None else None
                ),
                "polygon_first_o": first_o,
                "polygon_last_c": last_c,
            }
        url = next_url
        params = {"apiKey": api_key}

    return {
        "polygon_http_status": 200,
        "polygon_msg": "ok",
        "polygon_pages": int(pages),
        "polygon_rows_returned": int(rows_total),
        "polygon_first_date": (
            pd.to_datetime(ts_min, unit="ms", utc=True).strftime("%Y-%m-%d") if ts_min is not None else None
        ),
        "polygon_last_date": (
            pd.to_datetime(ts_max, unit="ms", utc=True).strftime("%Y-%m-%d") if ts_max is not None else None
        ),
        "polygon_first_o": first_o,
        "polygon_last_c": last_c,
    }


def derive_verdict(row: dict[str, Any]) -> str:
    file_exists = bool(row.get("file_exists_local"))
    local_rows = row.get("local_rows")
    local_ok = bool(row.get("local_read_ok")) if row.get("local_read_ok") is not None else False
    polygon_status = row.get("polygon_http_status")
    polygon_rows = row.get("polygon_rows_returned")

    if file_exists and local_ok and (local_rows or 0) > 0:
        return "LOCAL_FILE_PRESENT"
    if polygon_status == 200 and (polygon_rows or 0) == 0:
        return "PROVIDER_NO_DATA_FOR_YEAR"
    if polygon_status == 200 and (polygon_rows or 0) > 0 and not file_exists:
        return "LOCAL_MATERIALIZATION_GAP"
    if polygon_status == 200 and (polygon_rows or 0) > 0 and file_exists and not local_ok:
        return "LOCAL_FILE_READ_ERROR"
    if polygon_status == 206 and (polygon_rows or 0) >= 0:
        return "POLYGON_PARTIAL_RESPONSE_REVIEW"
    if polygon_status and int(polygon_status) != 200:
        return "POLYGON_ERROR_REVIEW"
    return "UNCLASSIFIED_REVIEW"


def process_one(
    row: dict[str, Any],
    *,
    outdir: Path,
    ticker_audit_by_ticker: pd.DataFrame,
    api_key: str,
    adjusted: bool,
    limit: int,
    timeout: int,
    max_pages: int,
    max_retries: int,
    backoff_base: float,
    backoff_max: float,
) -> dict[str, Any]:
    ticker = str(row["ticker"])
    year = int(row["year"])

    local = local_file_info(outdir, ticker, year)
    polygon = fetch_polygon_year(
        api_key=api_key,
        ticker=ticker,
        start=str(row["date_from"]),
        end=str(row["date_to"]),
        adjusted=adjusted,
        limit=limit,
        timeout=timeout,
        max_pages=max_pages,
        max_retries=max_retries,
        backoff_base=backoff_base,
        backoff_max=backoff_max,
    )

    audit_row = ticker_audit_by_ticker.get(ticker, {})
    out = {
        **row,
        **local,
        **polygon,
        "download_audit_status": audit_row.get("status"),
        "download_audit_http_status": audit_row.get("http_status"),
        "download_audit_rows": audit_row.get("rows"),
        "download_audit_pages": audit_row.get("pages"),
        "download_audit_msg": audit_row.get("msg"),
    }
    out["verdict"] = derive_verdict(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Forensic verification of really problematic daily ticker-years against local files and Polygon"
    )
    ap.add_argument("--problematic-parquet", required=True)
    ap.add_argument("--tasks-parquet", required=True)
    ap.add_argument("--ticker-audit-csv", required=True)
    ap.add_argument("--daily-root", default=r"D:\ohlcv_daily")
    ap.add_argument("--outdir", default="")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=50000)
    ap.add_argument("--timeout", type=int, default=40)
    ap.add_argument("--max-pages", type=int, default=1000)
    ap.add_argument("--max-retries", type=int, default=6)
    ap.add_argument("--backoff-base", type=float, default=1.0)
    ap.add_argument("--backoff-max", type=float, default=30.0)
    ap.add_argument("--adjusted", action="store_true", default=False)
    args = ap.parse_args()

    api_key = os.environ.get("POLYGON_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("POLYGON_API_KEY no está definido en el entorno")

    outdir = build_outdir(args.outdir)
    problematic = load_problematic_tickers(Path(args.problematic_parquet))
    tasks = load_tasks(Path(args.tasks_parquet), problematic)
    ticker_audit = load_ticker_audit(Path(args.ticker_audit_csv))
    ticker_audit_by_ticker = (
        ticker_audit.sort_values(["ticker"]).drop_duplicates(subset=["ticker"], keep="last").set_index("ticker").to_dict(orient="index")
    )
    daily_root = Path(args.daily_root)

    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
        futs = [
            ex.submit(
                process_one,
                row,
                outdir=daily_root,
                ticker_audit_by_ticker=ticker_audit_by_ticker,
                api_key=api_key,
                adjusted=bool(args.adjusted),
                limit=int(args.limit),
                timeout=int(args.timeout),
                max_pages=int(args.max_pages),
                max_retries=int(args.max_retries),
                backoff_base=float(args.backoff_base),
                backoff_max=float(args.backoff_max),
            )
            for row in tasks.to_dict(orient="records")
        ]
        for i, fut in enumerate(as_completed(futs), start=1):
            records.append(fut.result())
            if i % 25 == 0 or i == len(futs):
                print(f"processed {i}/{len(futs)}")

    forensic = pd.DataFrame(records).sort_values(["ticker", "year"], ascending=[True, True]).reset_index(drop=True)
    by_verdict = (
        forensic["verdict"].value_counts(dropna=False).rename_axis("verdict").reset_index(name="rows")
    )
    by_ticker = (
        forensic.groupby("ticker", dropna=False)
        .agg(
            task_rows=("task_key", "size"),
            years=("year", lambda s: sorted(pd.Series(s).dropna().astype(int).unique().tolist())),
            verdicts=("verdict", lambda s: sorted(pd.Series(s).dropna().astype(str).unique().tolist())),
            local_file_present_rows=("file_exists_local", lambda s: int(pd.Series(s).fillna(False).astype(bool).sum())),
            polygon_positive_rows=("polygon_rows_returned", lambda s: int((pd.to_numeric(pd.Series(s), errors="coerce").fillna(0) > 0).sum())),
        )
        .reset_index()
        .sort_values(["task_rows", "ticker"], ascending=[False, True])
    )

    forensic_parquet = outdir / "daily_really_problematic_forensic.parquet"
    forensic_csv = outdir / "daily_really_problematic_forensic.csv"
    verdict_parquet = outdir / "daily_really_problematic_forensic_by_verdict.parquet"
    verdict_csv = outdir / "daily_really_problematic_forensic_by_verdict.csv"
    by_ticker_parquet = outdir / "daily_really_problematic_forensic_by_ticker.parquet"
    by_ticker_csv = outdir / "daily_really_problematic_forensic_by_ticker.csv"
    summary_json = outdir / "daily_really_problematic_forensic_summary.json"

    forensic.to_parquet(forensic_parquet, index=False)
    forensic.to_csv(forensic_csv, index=False)
    by_verdict.to_parquet(verdict_parquet, index=False)
    by_verdict.to_csv(verdict_csv, index=False)
    by_ticker.to_parquet(by_ticker_parquet, index=False)
    by_ticker.to_csv(by_ticker_csv, index=False)

    summary = {
        "audited_at_utc": utc_now(),
        "problematic_tickers_input": int(len(problematic)),
        "task_rows_input": int(len(tasks)),
        "workers": int(args.workers),
        "verdict_counts": {str(r["verdict"]): int(r["rows"]) for r in by_verdict.to_dict(orient="records")},
        "tickers_with_polygon_positive_rows": int(
            by_ticker["polygon_positive_rows"].fillna(0).gt(0).sum()
        ),
        "tickers_with_local_present_rows": int(
            by_ticker["local_file_present_rows"].fillna(0).gt(0).sum()
        ),
        "inputs": {
            "problematic_parquet": str(args.problematic_parquet),
            "tasks_parquet": str(args.tasks_parquet),
            "ticker_audit_csv": str(args.ticker_audit_csv),
            "daily_root": str(args.daily_root),
        },
        "outputs": {
            "forensic_parquet": str(forensic_parquet),
            "forensic_csv": str(forensic_csv),
            "verdict_parquet": str(verdict_parquet),
            "verdict_csv": str(verdict_csv),
            "by_ticker_parquet": str(by_ticker_parquet),
            "by_ticker_csv": str(by_ticker_csv),
            "summary_json": str(summary_json),
        },
        "outdir": str(outdir),
    }
    summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
