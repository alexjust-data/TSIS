from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import requests

BASE_URL = "https://api.polygon.io"

DATASET_SPECS = {
    "inflation": {
        "path": "/fed/v1/inflation",
        "sort": "date.asc",
        "group": "economic",
    },
    "inflation_expectations": {
        "path": "/fed/v1/inflation-expectations",
        "sort": "date.asc",
        "group": "economic",
    },
    "treasury_yields": {
        "path": "/fed/v1/treasury-yields",
        "sort": "date.asc",
        "group": "economic",
    },
}


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


def fetch_all_pages(session: requests.Session, dataset: str, api_key: str, limit: int, timeout: int) -> Tuple[List[Dict], int, str, int]:
    spec = DATASET_SPECS[dataset]
    url = f"{BASE_URL}{spec['path']}"
    params: Dict[str, object] = {"limit": limit, "sort": spec["sort"], "apiKey": api_key}
    rows: List[Dict] = []
    pages = 0

    while url:
        response = session.get(url, params=params, timeout=timeout)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "2"))
            import time
            time.sleep(max(1, retry_after))
            continue

        try:
            response.raise_for_status()
        except Exception as exc:
            return rows, response.status_code, f"http_error: {exc}", pages

        pages += 1
        payload = response.json()
        results = payload.get("results", [])
        if isinstance(results, dict):
            results = [results]
        if isinstance(results, list):
            rows.extend([x for x in results if isinstance(x, dict)])

        next_url = payload.get("next_url")
        if next_url:
            url = str(next_url)
            params = {"apiKey": api_key}
        else:
            break

    return rows, 200, "ok", pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Polygon economy datasets used in additional/economic")
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--datasets", default="inflation,inflation_expectations,treasury_yields")
    parser.add_argument("--limit", type=int, default=50000)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    env_file = Path(args.env_file)
    out_root = Path(args.out_root)
    run_dir = Path(args.run_dir)
    datasets = [x.strip() for x in str(args.datasets).split(",") if x.strip()]
    invalid = [x for x in datasets if x not in DATASET_SPECS]
    if invalid:
        raise SystemExit(f"Unsupported datasets: {invalid}")

    api_key = get_api_key(env_file)
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {api_key}"})

    run_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now_iso()
    manifest_rows: List[Dict[str, object]] = []

    for dataset in datasets:
        rows, http_status, msg, pages = fetch_all_pages(session, dataset, api_key, args.limit, args.timeout)
        group = DATASET_SPECS[dataset]["group"]
        out_dir = out_root / group
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{dataset}.parquet"
        df = pd.json_normalize(rows, sep=".") if rows else pd.DataFrame()
        df["_dataset"] = dataset
        df["_ingested_utc"] = utc_now_iso()
        df.to_parquet(out_file, index=False)
        manifest_rows.append(
            {
                "dataset": dataset,
                "status": "ok" if http_status == 200 else "error",
                "http_status": http_status,
                "message": msg,
                "rows_saved": int(len(df)),
                "pages": pages,
                "out_file": str(out_file),
                "ts_utc": utc_now_iso(),
            }
        )

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_parquet(run_dir / "download_manifest.parquet", index=False)
    manifest.to_csv(run_dir / "download_manifest.csv", index=False)

    summary = {
        "started_at_utc": started_at,
        "finished_at_utc": utc_now_iso(),
        "datasets": datasets,
        "out_root": str(out_root),
        "run_dir": str(run_dir),
        "submitted_tasks": len(datasets),
        "ok_tasks": int((manifest["status"] == "ok").sum()) if len(manifest) else 0,
        "error_tasks": int((manifest["status"] == "error").sum()) if len(manifest) else 0,
        "summary_by_dataset": manifest.to_dict(orient="records"),
        "sources": {
            "inflation": "https://polygon.io/docs/rest/economy/inflation",
            "inflation_expectations": "https://polygon.io/docs/rest/economy/inflation-expectations",
            "treasury_yields": "https://polygon.io/docs/rest/economy/treasury-yields",
        },
    }
    (run_dir / "download_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
