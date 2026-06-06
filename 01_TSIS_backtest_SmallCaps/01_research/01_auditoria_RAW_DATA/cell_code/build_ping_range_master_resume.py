from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

BASE = "https://api.polygon.io"
DEFAULT_UNIVERSE = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti\hybrid_enriched\universe_hybrid_enriched_with_financial_ranges.parquet")
DEFAULT_OUTDIR = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Construye ping_range_master.parquet con progreso y resume")
    ap.add_argument("--universe-parquet", default=str(DEFAULT_UNIVERSE))
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    ap.add_argument("--ping-start", default="2004-01-01")
    ap.add_argument("--ping-end", default="2026-12-31")
    ap.add_argument("--block-size", type=int, default=100)
    ap.add_argument("--sleep-per-ticker-sec", type=float, default=0.12)
    ap.add_argument("--timeout-sec", type=int, default=30)
    ap.add_argument("--max-retries", type=int, default=5)
    ap.add_argument("--retry-backoff-sec", type=float, default=1.5)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--limit-tickers", type=int, default=0)
    return ap.parse_args()


def load_universe_tickers(path: Path, limit_tickers: int = 0) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"No existe universo: {path}")
    u = pd.read_parquet(path)
    ticker_col = next((c for c in ["ticker", "symbol", "Ticker", "SYMBOL"] if c in u.columns), None)
    if ticker_col is None:
        raise RuntimeError("No se encontr? columna ticker/symbol en el universo.")
    tickers = (
        u[ticker_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    if limit_tickers and limit_tickers > 0:
        tickers = tickers[:limit_tickers]
    return tickers


def request_with_retry(session: requests.Session, url: str, params: dict[str, Any], timeout_sec: int, max_retries: int, retry_backoff_sec: float) -> requests.Response | None:
    last_resp = None
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=timeout_sec)
            last_resp = resp
            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = resp.headers.get("Retry-After")
                if retry_after and str(retry_after).isdigit():
                    sleep_s = float(retry_after)
                else:
                    sleep_s = retry_backoff_sec ** (attempt + 1)
                time.sleep(max(0.0, sleep_s))
                continue
            return resp
        except Exception:
            time.sleep(retry_backoff_sec ** (attempt + 1))
    return last_resp


def ping_side(session: requests.Session, api_key: str, ticker: str, ping_start: str, ping_end: str, sort: str, timeout_sec: int, max_retries: int, retry_backoff_sec: float) -> dict[str, Any]:
    url = f"{BASE}/v2/aggs/ticker/{ticker}/range/1/day/{ping_start}/{ping_end}"
    params = {
        "adjusted": "true",
        "sort": sort,
        "limit": 1,
        "apiKey": api_key,
    }
    resp = request_with_retry(session, url, params, timeout_sec, max_retries, retry_backoff_sec)
    if resp is None:
        return {"ok": False, "status_code": None, "data": None, "error": "request_failed_no_response"}
    if resp.status_code != 200:
        return {"ok": False, "status_code": int(resp.status_code), "data": None, "error": (resp.text or "")[:400]}
    try:
        js = resp.json()
    except Exception as exc:
        return {"ok": False, "status_code": 200, "data": None, "error": f"json_error:{exc}"[:400]}
    results = js.get("results", []) if isinstance(js, dict) else []
    if not results:
        return {"ok": True, "status_code": 200, "data": None, "error": None}
    t_ms = results[0].get("t") if isinstance(results[0], dict) else None
    dt_val = pd.to_datetime(t_ms, unit="ms", utc=True).date() if t_ms is not None else None
    return {"ok": True, "status_code": 200, "data": str(dt_val) if dt_val is not None else None, "error": None}


def ping_ticker_range(session: requests.Session, api_key: str, ticker: str, ping_start: str, ping_end: str, timeout_sec: int, max_retries: int, retry_backoff_sec: float) -> dict[str, Any]:
    asc = ping_side(session, api_key, ticker, ping_start, ping_end, "asc", timeout_sec, max_retries, retry_backoff_sec)
    desc = ping_side(session, api_key, ticker, ping_start, ping_end, "desc", timeout_sec, max_retries, retry_backoff_sec)
    has_data = bool(asc.get("data") and desc.get("data"))
    return {
        "ticker": ticker,
        "has_data": has_data,
        "first_day": asc.get("data"),
        "last_day": desc.get("data"),
        "asc_status": asc.get("status_code"),
        "desc_status": desc.get("status_code"),
        "asc_error": asc.get("error"),
        "desc_error": desc.get("error"),
    }


def load_partial(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["ticker", "has_data", "first_day", "last_day", "asc_status", "desc_status", "asc_error", "desc_error", "updated_at_utc"])
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError(f"Partial sin columna ticker: {path}")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    return df.drop_duplicates(subset=["ticker"], keep="last")


def save_partial(df: pd.DataFrame, partial_parquet: Path, partial_csv: Path) -> None:
    df = df.copy()
    df.to_parquet(partial_parquet, index=False)
    df.to_csv(partial_csv, index=False)


def main() -> int:
    args = parse_args()
    api_key = os.getenv("POLYGON_API_KEY", "")
    if not api_key:
        raise RuntimeError("Falta POLYGON_API_KEY. Exporta la variable de entorno antes de ejecutar.")

    universe_parquet = Path(args.universe_parquet)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ping_master_parquet = outdir / "ping_range_master.parquet"
    ping_master_csv = outdir / "ping_range_master.csv"
    partial_parquet = outdir / "ping_range_master.partial.parquet"
    partial_csv = outdir / "ping_range_master.partial.csv"
    progress_json = outdir / "ping_range_master.progress.json"

    tickers = load_universe_tickers(universe_parquet, limit_tickers=args.limit_tickers)
    total = len(tickers)
    print(f"UNIVERSE_PARQUET: {universe_parquet}")
    print(f"OUTDIR: {outdir}")
    print(f"tickers_total: {total}")
    print(f"sample: {tickers[:10]}")

    partial_df = load_partial(partial_parquet) if args.resume else pd.DataFrame(columns=["ticker", "has_data", "first_day", "last_day", "asc_status", "desc_status", "asc_error", "desc_error", "updated_at_utc"])
    done_map = {str(t).upper() for t in partial_df.get("ticker", pd.Series(dtype=str)).tolist()}
    pending = [tk for tk in tickers if tk not in done_map]

    print(f"resume: {bool(args.resume)}")
    print(f"already_done: {len(done_map)}")
    print(f"pending: {len(pending)}")

    t0 = time.time()
    rows: list[dict[str, Any]] = partial_df.to_dict(orient="records") if len(partial_df) else []

    with requests.Session() as session:
        for block_start in range(0, len(pending), args.block_size):
            block_end = min(block_start + args.block_size, len(pending))
            block = pending[block_start:block_end]
            for tk in block:
                out = ping_ticker_range(
                    session=session,
                    api_key=api_key,
                    ticker=tk,
                    ping_start=args.ping_start,
                    ping_end=args.ping_end,
                    timeout_sec=args.timeout_sec,
                    max_retries=args.max_retries,
                    retry_backoff_sec=args.retry_backoff_sec,
                )
                out["updated_at_utc"] = utc_now()
                rows.append(out)
                if args.sleep_per_ticker_sec > 0:
                    time.sleep(args.sleep_per_ticker_sec)

            current = pd.DataFrame(rows).drop_duplicates(subset=["ticker"], keep="last").sort_values("ticker").reset_index(drop=True)
            save_partial(current, partial_parquet, partial_csv)

            processed_total = len(current)
            elapsed = time.time() - t0
            rate = processed_total / elapsed if elapsed > 0 else 0.0
            remaining = total - processed_total
            eta_sec = int(remaining / rate) if rate > 0 else None
            http_non_200 = int(((current["asc_status"] != 200) | (current["desc_status"] != 200)).fillna(False).sum()) if len(current) else 0
            has_data_true = int(current["has_data"].fillna(False).sum()) if len(current) else 0

            progress = {
                "status": "running",
                "processed": processed_total,
                "total": total,
                "progress_pct": round(100.0 * processed_total / total, 2) if total else 100.0,
                "pending_remaining": remaining,
                "block_pending_start": block_start + 1,
                "block_pending_end": block_end,
                "block_size": len(block),
                "elapsed_sec": round(elapsed, 2),
                "rate_tickers_per_sec": round(rate, 4),
                "eta_sec": eta_sec,
                "has_data_true": has_data_true,
                "http_non_200": http_non_200,
                "updated_at_utc": utc_now(),
                "partial_parquet": str(partial_parquet),
                "partial_csv": str(partial_csv),
            }
            progress_json.write_text(json.dumps(progress, indent=2), encoding="utf-8")

            eta_txt = f"{eta_sec/60:.1f}m" if eta_sec is not None else "n/a"
            print(
                f"[block] pending={block_start+1}-{block_end}/{len(pending)} | "
                f"done={processed_total}/{total} ({progress['progress_pct']:.2f}%) | "
                f"elapsed={elapsed/60:.1f}m | eta={eta_txt} | "
                f"has_data_true={has_data_true} | http_non_200={http_non_200}"
            )

    final_df = pd.DataFrame(rows).drop_duplicates(subset=["ticker"], keep="last").sort_values("ticker").reset_index(drop=True)
    final_df.to_parquet(ping_master_parquet, index=False)
    final_df.to_csv(ping_master_csv, index=False)

    progress = {
        "status": "completed",
        "processed": int(len(final_df)),
        "total": total,
        "progress_pct": 100.0,
        "has_data_true": int(final_df["has_data"].fillna(False).sum()) if len(final_df) else 0,
        "http_non_200": int(((final_df["asc_status"] != 200) | (final_df["desc_status"] != 200)).fillna(False).sum()) if len(final_df) else 0,
        "updated_at_utc": utc_now(),
        "output_parquet": str(ping_master_parquet),
        "output_csv": str(ping_master_csv),
        "partial_parquet": str(partial_parquet),
        "partial_csv": str(partial_csv),
    }
    progress_json.write_text(json.dumps(progress, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(progress, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
