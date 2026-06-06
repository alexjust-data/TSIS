from __future__ import annotations

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests

BASE_URL = "https://api.polygon.io"

DATASET_SPECS = {
    "splits": {
        "path": "/v3/reference/splits",
        "query_mode": "ticker_param",
        "ticker_param": "ticker",
        "results_mode": "results_list",
        "group": "corporate_actions",
    },
    "dividends": {
        "path": "/v3/reference/dividends",
        "query_mode": "ticker_param",
        "ticker_param": "ticker",
        "results_mode": "results_list",
        "group": "corporate_actions",
    },
    "ticker_events": {
        "path": "/vX/reference/tickers/{ticker}/events",
        "query_mode": "path_ticker",
        "results_mode": "events_object",
        "group": "corporate_actions",
    },
    "news": {
        "path": "/v2/reference/news",
        "query_mode": "ticker_param",
        "ticker_param": "ticker",
        "results_mode": "results_list",
        "group": "news",
    },
    "ipos": {
        "path": "/vX/reference/ipos",
        "query_mode": "ticker_param",
        "ticker_param": "ticker",
        "results_mode": "results_list",
        "group": "ipos",
    },
    "income_statements": {
        "path": "/stocks/financials/v1/income-statements",
        "query_mode": "ticker_param",
        "ticker_param": "tickers",
        "results_mode": "results_list",
        "group": "financials",
    },
    "balance_sheets": {
        "path": "/stocks/financials/v1/balance-sheets",
        "query_mode": "ticker_param",
        "ticker_param": "tickers",
        "results_mode": "results_list",
        "group": "financials",
    },
    "cash_flow_statements": {
        "path": "/stocks/financials/v1/cash-flow-statements",
        "query_mode": "ticker_param",
        "ticker_param": "tickers",
        "results_mode": "results_list",
        "group": "financials",
    },
    "ratios": {
        "path": "/stocks/financials/v1/ratios",
        "query_mode": "ticker_param",
        "ticker_param": "ticker",
        "results_mode": "results_list",
        "group": "financials",
    },
}

THREAD_LOCAL = threading.local()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env_file(env_file: Path) -> None:
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_api_key(env_file: Path) -> str:
    load_env_file(env_file)
    api_key = os.environ.get("POLYGON_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(f"POLYGON_API_KEY not found in environment or env file: {env_file}")
    return api_key


def get_session(api_key: str) -> requests.Session:
    sess = getattr(THREAD_LOCAL, "session", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update({"Authorization": f"Bearer {api_key}"})
        THREAD_LOCAL.session = sess
    return sess


def load_universe_tickers(universe_parquet: Path) -> List[str]:
    df = pd.read_parquet(universe_parquet, columns=["ticker"])
    ser = df["ticker"].astype("string").str.strip().dropna()
    tickers = sorted({x.upper() for x in ser.tolist() if x})
    return tickers


def build_request(dataset: str, ticker: str, limit: int, api_key: str) -> Tuple[str, Dict[str, object]]:
    spec = DATASET_SPECS[dataset]
    path = spec["path"]
    if spec["query_mode"] == "path_ticker":
        url = f"{BASE_URL}{path.format(ticker=ticker)}"
        params: Dict[str, object] = {"apiKey": api_key}
    else:
        url = f"{BASE_URL}{path}"
        params = {spec["ticker_param"]: ticker, "limit": limit, "apiKey": api_key}
    return url, params


def normalize_records(dataset: str, ticker: str, payload: Dict[str, object]) -> List[Dict[str, object]]:
    mode = DATASET_SPECS[dataset]["results_mode"]
    if mode == "results_list":
        records = payload.get("results", [])
        if isinstance(records, dict):
            records = [records]
        if not isinstance(records, list):
            return []
        out: List[Dict[str, object]] = []
        for rec in records:
            if not isinstance(rec, dict):
                continue
            item = dict(rec)
            item["ticker"] = ticker
            out.append(item)
        return out

    if mode == "events_object":
        results = payload.get("results", {})
        if not isinstance(results, dict):
            return []
        events = results.get("events", [])
        name = results.get("name")
        if not isinstance(events, list):
            return []
        out = []
        for rec in events:
            if not isinstance(rec, dict):
                continue
            item = dict(rec)
            item["ticker"] = ticker
            if name is not None:
                item["name"] = name
            out.append(item)
        return out

    raise ValueError(f"Unsupported results_mode={mode}")


def fetch_all_pages(
    session: requests.Session,
    dataset: str,
    ticker: str,
    api_key: str,
    limit: int,
    max_pages: int,
    timeout: int,
    pause_sec: float,
) -> Tuple[List[Dict[str, object]], int, str, int]:
    url, params = build_request(dataset, ticker, limit, api_key)
    rows: List[Dict[str, object]] = []
    pages = 0

    while url and pages < max_pages:
        response = session.get(url, params=params, timeout=timeout)

        if response.status_code == 404:
            return rows, 404, "not_found", pages

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "2"))
            time.sleep(max(1, retry_after))
            continue

        try:
            response.raise_for_status()
        except Exception as exc:
            return rows, response.status_code, f"http_error: {exc}", pages

        pages += 1
        payload = response.json()
        rows.extend(normalize_records(dataset, ticker, payload))

        next_url = payload.get("next_url")
        if next_url:
            url = str(next_url)
            params = {"apiKey": api_key}
            if pause_sec > 0:
                time.sleep(pause_sec)
        else:
            break

    if pages >= max_pages:
        return rows, 206, "hit_page_cap", pages

    return rows, 200, "ok", pages


def write_ticker_parquet(out_root: Path, dataset: str, ticker: str, rows: List[Dict[str, object]]) -> Path:
    group = DATASET_SPECS[dataset]["group"]
    out_dir = out_root / group / dataset / f"ticker={ticker}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{dataset}_{ticker}.parquet"

    if rows:
        df = pd.json_normalize(rows, sep=".")
        if "ticker" not in df.columns:
            df["ticker"] = ticker
    else:
        df = pd.DataFrame([{"ticker": ticker, "_empty": True}])

    df["_dataset"] = dataset
    df["_ingested_utc"] = utc_now_iso()
    df.to_parquet(out_file, index=False)
    return out_file


def is_existing_output_valid(path: Path, ticker: str) -> bool:
    if not path.exists():
        return False
    try:
        df = pd.read_parquet(path, columns=["ticker"])
    except Exception:
        return False
    if "ticker" not in df.columns:
        return False
    vals = df["ticker"].astype("string").str.strip().dropna().str.upper().unique().tolist()
    if not vals:
        return True
    return len(vals) == 1 and vals[0] == ticker.upper()


def output_path_for(out_root: Path, dataset: str, ticker: str) -> Path:
    group = DATASET_SPECS[dataset]["group"]
    return out_root / group / dataset / f"ticker={ticker}" / f"{dataset}_{ticker}.parquet"


def worker(
    ticker: str,
    datasets: Iterable[str],
    api_key: str,
    out_root: Path,
    limit: int,
    max_pages: int,
    timeout: int,
    pause_sec: float,
    resume: bool,
) -> List[Dict[str, object]]:
    session = get_session(api_key)
    events: List[Dict[str, object]] = []

    for dataset in datasets:
        out_file = output_path_for(out_root, dataset, ticker)
        if resume and is_existing_output_valid(out_file, ticker):
            try:
                df = pd.read_parquet(out_file)
                row_count = int(len(df))
            except Exception:
                row_count = None
            events.append(
                {
                    "ticker": ticker,
                    "dataset": dataset,
                    "status": "resume_skip",
                    "http_status": 200,
                    "rows_saved": row_count,
                    "pages": None,
                    "out_file": str(out_file),
                    "ts_utc": utc_now_iso(),
                }
            )
            continue

        rows, http_status, msg, pages = fetch_all_pages(
            session=session,
            dataset=dataset,
            ticker=ticker,
            api_key=api_key,
            limit=limit,
            max_pages=max_pages,
            timeout=timeout,
            pause_sec=pause_sec,
        )
        out_file = write_ticker_parquet(out_root, dataset, ticker, rows)
        events.append(
            {
                "ticker": ticker,
                "dataset": dataset,
                "status": "ok" if http_status in {200, 206, 404} else "error",
                "http_status": http_status,
                "message": msg,
                "rows_saved": int(len(rows)),
                "pages": pages,
                "out_file": str(out_file),
                "ts_utc": utc_now_iso(),
            }
        )

    return events


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def summarize_rows(path: Optional[Path], dataset: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    if path is None or not path.exists():
        return None, None, None
    try:
        df = pd.read_parquet(path)
    except Exception:
        return None, None, None

    date_col = None
    for candidate in [
        "execution_date",
        "ex_dividend_date",
        "date",
        "listing_date",
        "published_utc",
        "period_end",
        "filing_date",
    ]:
        if candidate in df.columns:
            date_col = candidate
            break

    if date_col is None:
        return int(len(df)), None, None

    try:
        ser = pd.to_datetime(df[date_col], errors="coerce", utc=False).dropna()
    except Exception:
        ser = pd.Series(dtype="datetime64[ns]")
    if ser.empty:
        return int(len(df)), None, None
    return int(len(df)), ser.min().isoformat(), ser.max().isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download ticker-based Polygon additional datasets for LT<1B universe. "
        "Default scope is only datasets not already covered in D:\\reference and D:\\financial."
    )
    parser.add_argument("--universe-parquet", required=True)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument(
        "--datasets",
        default="news,ipos",
    )
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--pause-sec", type=float, default=0.0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    universe_parquet = Path(args.universe_parquet)
    env_file = Path(args.env_file)
    out_root = Path(args.out_root)
    run_dir = Path(args.run_dir)
    datasets = [x.strip() for x in str(args.datasets).split(",") if x.strip()]
    invalid = [x for x in datasets if x not in DATASET_SPECS]
    if invalid:
        raise SystemExit(f"Unsupported datasets: {invalid}")

    api_key = get_api_key(env_file)
    tickers = load_universe_tickers(universe_parquet)

    run_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"ticker": tickers}).to_csv(run_dir / "input_universe_tickers.csv", index=False)

    started_at = utc_now_iso()
    manifest_rows: List[Dict[str, object]] = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                worker,
                ticker,
                datasets,
                api_key,
                out_root,
                args.limit,
                args.max_pages,
                args.timeout,
                args.pause_sec,
                args.resume,
            ): ticker
            for ticker in tickers
        }
        for future in as_completed(futures):
            manifest_rows.extend(future.result())

    manifest = pd.DataFrame(manifest_rows)
    manifest = manifest.sort_values(["dataset", "ticker"], kind="stable").reset_index(drop=True)
    manifest_path_parquet = run_dir / "download_manifest.parquet"
    manifest_path_csv = run_dir / "download_manifest.csv"
    manifest.to_parquet(manifest_path_parquet, index=False)
    manifest.to_csv(manifest_path_csv, index=False)

    summary_by_dataset = []
    for dataset in datasets:
        sub = manifest[manifest["dataset"] == dataset].copy()
        ok_mask = sub["status"].isin(["ok", "resume_skip"])
        ok = int(ok_mask.sum())
        error = int((sub["status"] == "error").sum())
        rows_total = int(sub["rows_saved"].fillna(0).sum())
        paths = [Path(p) for p in sub.loc[ok_mask, "out_file"].dropna().astype(str).tolist()]
        spans = [summarize_rows(p, dataset) for p in paths[: min(len(paths), 50)]]
        summary_by_dataset.append(
            {
                "dataset": dataset,
                "ok": ok,
                "error": error,
                "rows_total": rows_total,
                "sampled_files_for_span": len(spans),
            }
        )

    summary = {
        "started_at_utc": started_at,
        "finished_at_utc": utc_now_iso(),
        "universe_parquet": str(universe_parquet),
        "universe_tickers": len(tickers),
        "datasets": datasets,
        "out_root": str(out_root),
        "run_dir": str(run_dir),
        "workers": args.workers,
        "resume": bool(args.resume),
        "pause_sec": args.pause_sec,
        "submitted_tasks": len(tickers) * len(datasets),
        "ok_tasks": int(manifest["status"].isin(["ok", "resume_skip"]).sum()) if len(manifest) else 0,
        "error_tasks": int((manifest["status"] == "error").sum()) if len(manifest) else 0,
        "summary_by_dataset": summary_by_dataset,
        "sources": {
            "splits": "https://polygon.io/docs/rest/stocks/corporate-actions/splits",
            "dividends": "https://polygon.io/docs/rest/stocks/corporate-actions/dividends",
            "ticker_events": "https://polygon.io/docs/rest/stocks/corporate-actions/ticker-events",
            "news": "https://polygon.io/docs/rest/stocks/news/",
            "ipos": "https://polygon.io/docs/rest/stocks/corporate-actions/ipos",
            "balance_sheets": "https://polygon.io/docs/rest/stocks/fundamentals/balance-sheets",
            "income_statements": "https://polygon.io/docs/rest/stocks/fundamentals/income-statements",
            "cash_flow_statements": "https://polygon.io/docs/rest/stocks/fundamentals/cash-flow-statements",
            "ratios": "https://polygon.io/docs/rest/stocks/fundamentals/ratios",
        },
    }
    write_json(run_dir / "download_summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
