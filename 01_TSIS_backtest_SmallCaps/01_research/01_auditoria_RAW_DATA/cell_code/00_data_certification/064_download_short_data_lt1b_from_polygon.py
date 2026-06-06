from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests


BASE_URL = "https://api.polygon.io"
DEFAULT_TIMEOUT = 60


@dataclass(frozen=True)
class EndpointSpec:
    name: str
    url: str
    date_col: str
    required_cols: list[str]


ENDPOINTS: dict[str, EndpointSpec] = {
    "short_interest": EndpointSpec(
        name="short_interest",
        url=f"{BASE_URL}/stocks/v1/short-interest",
        date_col="settlement_date",
        required_cols=[
            "settlement_date",
            "ticker",
            "short_interest",
            "avg_daily_volume",
            "days_to_cover",
        ],
    ),
    "short_volume": EndpointSpec(
        name="short_volume",
        url=f"{BASE_URL}/stocks/v1/short-volume",
        date_col="date",
        required_cols=[
            "ticker",
            "date",
            "total_volume",
            "short_volume",
            "exempt_volume",
            "non_exempt_volume",
            "short_volume_ratio",
            "nyse_short_volume",
            "nyse_short_volume_exempt",
            "nasdaq_carteret_short_volume",
            "nasdaq_carteret_short_volume_exempt",
            "nasdaq_chicago_short_volume",
            "nasdaq_chicago_short_volume_exempt",
            "adf_short_volume",
            "adf_short_volume_exempt",
            "short_ratio",
            "exempt_ratio",
            "short_ratio_ma5",
            "short_ratio_change",
            "short_ratio_zscore",
        ],
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        env[key] = value
    return env


def get_polygon_api_key(env_file: Path) -> str:
    file_env = load_env_file(env_file)
    api_key = os.getenv("POLYGON_API_KEY") or file_env.get("POLYGON_API_KEY", "")
    if not api_key:
        raise SystemExit(f"Missing POLYGON_API_KEY in environment or env file: {env_file}")
    return api_key


def load_universe_tickers(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Universe parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "first_seen_date", "last_observed_date", "status_rebuilt", "classification_1b"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"Universe parquet missing required columns: {sorted(missing)}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df = df[df["ticker"] != ""].copy()
    df = df.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    return df


def build_run_dir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_downloads") / f"{stamp}_download_short_data_lt1b_from_polygon"
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def fetch_all_pages(session: requests.Session, url: str, params: dict[str, Any], api_key: str, pause_sec: float) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    next_url: str | None = url
    next_params: dict[str, Any] | None = dict(params)

    while next_url:
        if next_params is None:
            req_url = next_url
            sep = "&" if "?" in req_url else "?"
            if "apiKey=" not in req_url:
                req_url = f"{req_url}{sep}apiKey={api_key}"
            resp = session.get(req_url, timeout=DEFAULT_TIMEOUT)
        else:
            resp = session.get(next_url, params=next_params, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
        results = payload.get("results", []) or []
        all_rows.extend(results)
        next_url = payload.get("next_url")
        next_params = None
        if next_url and pause_sec > 0:
            time.sleep(pause_sec)
    return all_rows


def normalize_frame(df: pd.DataFrame, spec: EndpointSpec, ticker: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=spec.required_cols)
    if "ticker" not in df.columns:
        df["ticker"] = ticker
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    if spec.date_col in df.columns:
        df[spec.date_col] = pd.to_datetime(df[spec.date_col], errors="coerce")
        df = df.sort_values([spec.date_col], ascending=True, na_position="last")
    cols = list(df.columns)
    front = [c for c in spec.required_cols if c in cols]
    rest = [c for c in cols if c not in front]
    return df[front + rest].reset_index(drop=True)


def write_dataset_file(df: pd.DataFrame, out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_file, index=False)


def download_one(
    spec: EndpointSpec,
    ticker: str,
    api_key: str,
    out_root: Path,
    pause_sec: float,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "ticker": ticker,
        "limit": 50000,
        "apiKey": api_key,
    }
    started = utc_now()
    try:
        with requests.Session() as session:
            session.headers.update({"User-Agent": "backtest-smallcaps-short-data-downloader/1.0"})
            rows = fetch_all_pages(session, spec.url, params, api_key=api_key, pause_sec=pause_sec)
        df = normalize_frame(pd.DataFrame(rows), spec, ticker=ticker)
        out_file = out_root / spec.name / f"{ticker}.parquet"
        write_dataset_file(df, out_file)
        date_min = None
        date_max = None
        if spec.date_col in df.columns and not df.empty:
            s = pd.to_datetime(df[spec.date_col], errors="coerce")
            if s.notna().any():
                date_min = s.min().date().isoformat()
                date_max = s.max().date().isoformat()
        return {
            "dataset": spec.name,
            "ticker": ticker,
            "status": "ok",
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
            "rows": int(len(df)),
            "date_min": date_min,
            "date_max": date_max,
            "file_path": str(out_file),
            "error": None,
        }
    except Exception as exc:
        return {
            "dataset": spec.name,
            "ticker": ticker,
            "status": "error",
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
            "rows": None,
            "date_min": None,
            "date_max": None,
            "file_path": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def parse_datasets(raw: str) -> list[EndpointSpec]:
    names = [x.strip() for x in raw.split(",") if x.strip()]
    bad = [x for x in names if x not in ENDPOINTS]
    if bad:
        raise SystemExit(f"Unsupported datasets: {bad}. Allowed: {sorted(ENDPOINTS)}")
    return [ENDPOINTS[x] for x in names]


def main() -> None:
    ap = argparse.ArgumentParser(description="Download Polygon short data for the LT<1B universe")
    ap.add_argument(
        "--universe-parquet",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    )
    ap.add_argument(
        "--env-file",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\.env",
    )
    ap.add_argument(
        "--out-root",
        default=r"C:\TSIS_Data\data\short",
        help="Root where short_interest/ and short_volume/ parquet files will be written",
    )
    ap.add_argument(
        "--run-dir",
        default="",
        help="Optional run directory for manifests and logs",
    )
    ap.add_argument(
        "--datasets",
        default="short_interest,short_volume",
        help="Comma-separated list among short_interest,short_volume",
    )
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--pause-sec", type=float, default=0.0)
    ap.add_argument("--limit-tickers", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    api_key = get_polygon_api_key(Path(args.env_file))
    universe = load_universe_tickers(Path(args.universe_parquet))
    specs = parse_datasets(args.datasets)
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = build_run_dir(args.run_dir)

    if args.limit_tickers and args.limit_tickers > 0:
        universe = universe.head(args.limit_tickers).copy()

    tasks: list[tuple[EndpointSpec, str]] = []
    for spec in specs:
        for ticker in universe["ticker"].tolist():
            out_file = out_root / spec.name / f"{ticker}.parquet"
            if args.resume and out_file.exists():
                continue
            tasks.append((spec, ticker))

    manifest_rows: list[dict[str, Any]] = []
    started_at = utc_now()

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        future_map = {
            ex.submit(
                download_one,
                spec,
                ticker,
                api_key,
                out_root,
                args.pause_sec,
            ): (spec.name, ticker)
            for spec, ticker in tasks
        }
        for fut in as_completed(future_map):
            rec = fut.result()
            manifest_rows.append(rec)
            status = rec["status"]
            ticker = rec["ticker"]
            dataset = rec["dataset"]
            rows = rec["rows"]
            if status == "ok":
                print(f"[OK] {dataset} {ticker} rows={rows} date_min={rec['date_min']} date_max={rec['date_max']}")
            else:
                print(f"[ERR] {dataset} {ticker} {rec['error']}")

    manifest = pd.DataFrame(manifest_rows)
    if manifest.empty:
        manifest = pd.DataFrame(
            columns=[
                "dataset",
                "ticker",
                "status",
                "started_at_utc",
                "finished_at_utc",
                "rows",
                "date_min",
                "date_max",
                "file_path",
                "error",
            ]
        )

    summary = {
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "universe_parquet": str(args.universe_parquet),
        "universe_tickers": int(len(universe)),
        "datasets": [s.name for s in specs],
        "out_root": str(out_root),
        "run_dir": str(run_dir),
        "workers": int(args.workers),
        "resume": bool(args.resume),
        "pause_sec": float(args.pause_sec),
        "submitted_tasks": int(len(tasks)),
        "ok_tasks": int((manifest["status"] == "ok").sum()) if not manifest.empty else 0,
        "error_tasks": int((manifest["status"] == "error").sum()) if not manifest.empty else 0,
    }

    summary_by_dataset = []
    if not manifest.empty:
        for dataset, g in manifest.groupby("dataset", dropna=False):
            summary_by_dataset.append(
                {
                    "dataset": dataset,
                    "ok": int((g["status"] == "ok").sum()),
                    "error": int((g["status"] == "error").sum()),
                    "rows_total": int(pd.to_numeric(g["rows"], errors="coerce").fillna(0).sum()),
                }
            )

    manifest_csv = run_dir / "download_manifest.csv"
    manifest_parquet = run_dir / "download_manifest.parquet"
    summary_json = run_dir / "download_summary.json"
    universe_csv = run_dir / "input_universe_tickers.csv"

    manifest.to_csv(manifest_csv, index=False)
    manifest.to_parquet(manifest_parquet, index=False)
    universe.to_csv(universe_csv, index=False)
    summary_json.write_text(
        json.dumps(
            {
                **summary,
                "summary_by_dataset": summary_by_dataset,
                "outputs": {
                    "manifest_csv": str(manifest_csv),
                    "manifest_parquet": str(manifest_parquet),
                    "summary_json": str(summary_json),
                    "input_universe_csv": str(universe_csv),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({**summary, "summary_by_dataset": summary_by_dataset}, indent=2))


if __name__ == "__main__":
    main()
