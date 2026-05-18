#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp
import pandas as pd


STATUS_COLUMNS = [
    "ticker",
    "status",
    "related_count",
    "http_status",
    "error",
    "fetched_at_utc",
    "run_id",
]

EDGE_COLUMNS = [
    "requested_ticker",
    "related_ticker",
    "fetched_at_utc",
    "run_id",
]


@dataclass
class Config:
    tickers_csv: Path
    output_dir: Path
    api_key: str
    run_id: str
    concurrent: int
    timeout_sec: int
    resume: bool
    progress_every: int
    base_url: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_tickers(path: Path) -> list[str]:
    df = pd.read_csv(path)
    if "ticker" not in df.columns:
        raise ValueError("El CSV de entrada debe tener columna 'ticker'")
    s = df["ticker"].astype(str).str.upper().str.strip()
    return sorted(x for x in s.dropna().unique().tolist() if x)


def load_status(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=STATUS_COLUMNS)
    df = pd.read_csv(path)
    for c in STATUS_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    return df[STATUS_COLUMNS].copy()


def load_edges(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=EDGE_COLUMNS)
    df = pd.read_csv(path)
    for c in EDGE_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    return df[EDGE_COLUMNS].copy()


async def fetch_related(session: aiohttp.ClientSession, cfg: Config, ticker: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    url = f"{cfg.base_url.rstrip('/')}/v1/related-companies/{ticker}"
    params = {"apiKey": cfg.api_key}
    fetched_at = utc_now()
    try:
        async with session.get(url, params=params, timeout=cfg.timeout_sec) as resp:
            http_status = int(resp.status)
            data = await resp.json(content_type=None)
            results = data.get("results") or []
            status_value = str(data.get("status") or "")

            if http_status != 200:
                return (
                    {
                        "ticker": ticker,
                        "status": "FAIL",
                        "related_count": pd.NA,
                        "http_status": http_status,
                        "error": f"http_{http_status}",
                        "fetched_at_utc": fetched_at,
                        "run_id": cfg.run_id,
                    },
                    [],
                )

            edges = [
                {
                    "requested_ticker": ticker,
                    "related_ticker": str(item.get("ticker", "")).upper().strip(),
                    "fetched_at_utc": fetched_at,
                    "run_id": cfg.run_id,
                }
                for item in results
                if str(item.get("ticker", "")).strip()
            ]

            status = "OK" if status_value.upper() == "OK" else "FAIL"
            if status == "OK" and len(edges) == 0:
                status = "EMPTY"

            return (
                {
                    "ticker": ticker,
                    "status": status,
                    "related_count": int(len(edges)),
                    "http_status": http_status,
                    "error": pd.NA,
                    "fetched_at_utc": fetched_at,
                    "run_id": cfg.run_id,
                },
                edges,
            )
    except Exception as exc:
        return (
            {
                "ticker": ticker,
                "status": "FAIL",
                "related_count": pd.NA,
                "http_status": pd.NA,
                "error": f"{type(exc).__name__}: {exc}",
                "fetched_at_utc": fetched_at,
                "run_id": cfg.run_id,
            },
            [],
        )


async def run(cfg: Config) -> None:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    status_csv = cfg.output_dir / "related_companies_status.csv"
    edges_csv = cfg.output_dir / "related_companies_edges.csv"
    summary_json = cfg.output_dir / "related_companies_summary.json"

    tickers = read_tickers(cfg.tickers_csv)
    existing_status = load_status(status_csv)
    existing_edges = load_edges(edges_csv)

    done_tickers: set[str] = set()
    if cfg.resume and len(existing_status):
        done_mask = existing_status["status"].isin(["OK", "EMPTY"])
        done_tickers = set(existing_status.loc[done_mask, "ticker"].astype(str).str.upper())

    todo = [t for t in tickers if t not in done_tickers]

    print(f"run_id={cfg.run_id}")
    print(f"output_dir={cfg.output_dir}")
    print(f"tickers_total={len(tickers)}")
    print(f"tickers_already_done={len(done_tickers)}")
    print(f"tickers_to_process={len(todo)}")

    timeout = aiohttp.ClientTimeout(total=None, sock_connect=cfg.timeout_sec, sock_read=cfg.timeout_sec)
    connector = aiohttp.TCPConnector(limit=max(1, cfg.concurrent))
    status_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    processed = 0

    sem = asyncio.Semaphore(cfg.concurrent)

    async def worker(ticker: str, session: aiohttp.ClientSession) -> None:
        nonlocal processed
        async with sem:
            status_row, edges = await fetch_related(session, cfg, ticker)
            status_rows.append(status_row)
            edge_rows.extend(edges)
            processed += 1
            if cfg.progress_every > 0 and (processed % cfg.progress_every == 0 or processed == len(todo)):
                print(f"processed={processed}/{len(todo)}", flush=True)

    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        await asyncio.gather(*(worker(t, session) for t in todo))

    status_new = pd.DataFrame(status_rows, columns=STATUS_COLUMNS)
    edges_new = pd.DataFrame(edge_rows, columns=EDGE_COLUMNS)

    status_out = pd.concat([existing_status, status_new], ignore_index=True)
    if len(status_out):
        status_out = status_out.sort_values("fetched_at_utc").drop_duplicates(subset=["ticker"], keep="last")
    status_out.to_csv(status_csv, index=False, encoding="utf-8")

    edges_out = pd.concat([existing_edges, edges_new], ignore_index=True)
    if len(edges_out):
        edges_out = edges_out.drop_duplicates(subset=["requested_ticker", "related_ticker"], keep="last")
    edges_out.to_csv(edges_csv, index=False, encoding="utf-8")

    summary = {
        "run_id": cfg.run_id,
        "tickers_total": int(len(tickers)),
        "tickers_already_done": int(len(done_tickers)),
        "tickers_processed_this_run": int(len(todo)),
        "status_counts": status_out["status"].value_counts(dropna=False).to_dict() if len(status_out) else {},
        "edges_total": int(len(edges_out)),
        "fetched_at_utc": utc_now(),
        "tickers_csv": str(cfg.tickers_csv),
        "output_dir": str(cfg.output_dir),
        "base_url": cfg.base_url,
    }
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def parse_args() -> Config:
    p = argparse.ArgumentParser(description="Descarga Polygon related-companies para un universo de tickers")
    p.add_argument("--tickers-csv", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--run-id", default="related_companies_prod")
    p.add_argument("--api-key", default=None)
    p.add_argument("--concurrent", type=int, default=8)
    p.add_argument("--timeout-sec", type=int, default=30)
    p.add_argument("--progress-every", type=int, default=100)
    p.add_argument("--base-url", default="https://api.polygon.io")
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()

    api_key = args.api_key or os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("ERROR: falta POLYGON_API_KEY", file=sys.stderr)
        raise SystemExit(2)

    return Config(
        tickers_csv=Path(args.tickers_csv),
        output_dir=Path(args.output_dir),
        api_key=api_key,
        run_id=args.run_id,
        concurrent=max(1, int(args.concurrent)),
        timeout_sec=max(5, int(args.timeout_sec)),
        resume=bool(args.resume),
        progress_every=max(0, int(args.progress_every)),
        base_url=str(args.base_url),
    )


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
