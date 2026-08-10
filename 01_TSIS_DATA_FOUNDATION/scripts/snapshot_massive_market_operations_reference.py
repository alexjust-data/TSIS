from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests


SNAPSHOT_ID = "massive_stock_market_operations_reference_snapshot_v0_1"
API_BASE = "https://api.massive.com"
CONDITIONS_ENDPOINT = "/v3/reference/conditions"
EXCHANGES_ENDPOINT = "/v3/reference/exchanges"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _without_api_key(url: str) -> str:
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if key.lower() != "apikey"]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _fetch_all(
    session: requests.Session,
    *,
    endpoint: str,
    params: dict[str, Any],
    api_key: str,
    timeout: int,
) -> dict[str, Any]:
    url = f"{API_BASE}{endpoint}"
    request_params = {**params, "apiKey": api_key}
    results: list[dict[str, Any]] = []
    request_ids: list[str] = []
    page_count = 0
    terminal_status = ""

    while url:
        response = session.get(url, params=request_params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        page_count += 1
        terminal_status = str(payload.get("status") or "")
        if payload.get("request_id"):
            request_ids.append(str(payload["request_id"]))
        page_results = payload.get("results") or []
        if isinstance(page_results, dict):
            page_results = [page_results]
        if not isinstance(page_results, list):
            raise ValueError(f"Unexpected results payload for {endpoint}: {type(page_results).__name__}")
        results.extend(item for item in page_results if isinstance(item, dict))

        next_url = payload.get("next_url")
        if next_url:
            url = str(next_url)
            request_params = None
            if "apiKey=" not in url:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}apiKey={api_key}"
        else:
            url = ""

    return {
        "endpoint": endpoint,
        "query": params,
        "page_count": page_count,
        "request_ids": request_ids,
        "terminal_status": terminal_status,
        "results": results,
    }


def _nested_bool(item: dict[str, Any], path: tuple[str, ...]) -> bool | None:
    current: Any = item
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return bool(current) if isinstance(current, bool) else None


def normalize_conditions(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in results:
        rows.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "abbreviation": item.get("abbreviation"),
                "description": item.get("description"),
                "asset_class": item.get("asset_class"),
                "data_types_json": json.dumps(item.get("data_types") or [], sort_keys=True),
                "type": item.get("type"),
                "exchange": item.get("exchange"),
                "legacy": item.get("legacy"),
                "sip_mapping_json": json.dumps(item.get("sip_mapping") or {}, sort_keys=True),
                "update_rules_json": json.dumps(item.get("update_rules") or {}, sort_keys=True),
                "consolidated_updates_high_low": _nested_bool(
                    item, ("update_rules", "consolidated", "updates_high_low")
                ),
                "consolidated_updates_open_close": _nested_bool(
                    item, ("update_rules", "consolidated", "updates_open_close")
                ),
                "consolidated_updates_volume": _nested_bool(
                    item, ("update_rules", "consolidated", "updates_volume")
                ),
                "market_center_updates_high_low": _nested_bool(
                    item, ("update_rules", "market_center", "updates_high_low")
                ),
                "market_center_updates_open_close": _nested_bool(
                    item, ("update_rules", "market_center", "updates_open_close")
                ),
                "market_center_updates_volume": _nested_bool(
                    item, ("update_rules", "market_center", "updates_volume")
                ),
            }
        )
    return sorted(rows, key=lambda row: (row["id"] is None, row["id"], str(row["name"])))


def normalize_exchanges(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    columns = [
        "id",
        "type",
        "asset_class",
        "locale",
        "name",
        "acronym",
        "mic",
        "operating_mic",
        "participant_id",
        "url",
    ]
    rows = [{column: item.get(column) for column in columns} for item in results]
    return sorted(rows, key=lambda row: (row["id"] is None, row["id"], str(row["name"])))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty snapshot: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def materialize_snapshot(
    *,
    condition_response: dict[str, Any],
    exchange_response: dict[str, Any],
    output_dir: Path,
    captured_at_utc: str,
    overwrite: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "conditions_raw_json": output_dir / "massive_stock_trade_conditions_raw_v0_1.json",
        "conditions_csv": output_dir / "massive_stock_trade_conditions_normalized_v0_1.csv",
        "exchanges_raw_json": output_dir / "massive_stock_exchanges_raw_v0_1.json",
        "exchanges_csv": output_dir / "massive_stock_exchanges_normalized_v0_1.csv",
        "manifest": output_dir / f"{SNAPSHOT_ID}.manifest.json",
    }
    if not overwrite and any(path.exists() for path in paths.values()):
        raise FileExistsError(f"Snapshot output exists; pass --overwrite: {output_dir}")

    condition_rows = normalize_conditions(condition_response["results"])
    exchange_rows = normalize_exchanges(exchange_response["results"])

    sanitized_conditions = {
        **condition_response,
        "captured_at_utc": captured_at_utc,
        "source_url": f"{API_BASE}{CONDITIONS_ENDPOINT}",
    }
    sanitized_exchanges = {
        **exchange_response,
        "captured_at_utc": captured_at_utc,
        "source_url": f"{API_BASE}{EXCHANGES_ENDPOINT}",
    }
    paths["conditions_raw_json"].write_text(
        json.dumps(sanitized_conditions, indent=2, sort_keys=True), encoding="utf-8"
    )
    paths["exchanges_raw_json"].write_text(
        json.dumps(sanitized_exchanges, indent=2, sort_keys=True), encoding="utf-8"
    )
    _write_csv(paths["conditions_csv"], condition_rows)
    _write_csv(paths["exchanges_csv"], exchange_rows)

    artifacts = {
        name: {"path": str(path), "sha256": _sha256_file(path), "size_bytes": path.stat().st_size}
        for name, path in paths.items()
        if name != "manifest"
    }
    manifest = {
        "snapshot_id": SNAPSHOT_ID,
        "captured_at_utc": captured_at_utc,
        "provider": "Massive",
        "asset_class": "stocks",
        "condition_data_type": "trade",
        "condition_count": len(condition_rows),
        "exchange_count": len(exchange_rows),
        "condition_page_count": condition_response["page_count"],
        "exchange_page_count": exchange_response["page_count"],
        "condition_terminal_status": condition_response["terminal_status"],
        "exchange_terminal_status": exchange_response["terminal_status"],
        "provider_effective_history": "NOT_AVAILABLE_FROM_REFERENCE_ENDPOINT",
        "api_key_persisted": False,
        "artifacts": artifacts,
        "canonical_promotion": "NOT_AUTHORIZED",
        "massive_backfill_state": "DEFERRED_PENDING_MASSIVE_BACKFILL",
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"manifest": str(paths["manifest"]), "summary": manifest}


def snapshot_market_operations_reference(
    *,
    output_dir: Path,
    api_key: str,
    timeout: int,
    overwrite: bool,
) -> dict[str, Any]:
    if not api_key:
        raise ValueError("Missing provider API key")
    captured_at = _utc_now_iso()
    with requests.Session() as session:
        conditions = _fetch_all(
            session,
            endpoint=CONDITIONS_ENDPOINT,
            params={
                "asset_class": "stocks",
                "data_type": "trade",
                "limit": 1000,
                "sort": "id",
                "order": "asc",
            },
            api_key=api_key,
            timeout=timeout,
        )
        exchanges = _fetch_all(
            session,
            endpoint=EXCHANGES_ENDPOINT,
            params={"asset_class": "stocks", "locale": "us"},
            api_key=api_key,
            timeout=timeout,
        )
    return materialize_snapshot(
        condition_response=conditions,
        exchange_response=exchanges,
        output_dir=output_dir,
        captured_at_utc=captured_at,
        overwrite=overwrite,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--api-key-env", default="POLYGON_API_KEY")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    api_key = os.getenv(args.api_key_env, "")
    result = snapshot_market_operations_reference(
        output_dir=args.output_dir,
        api_key=api_key,
        timeout=args.timeout,
        overwrite=bool(args.overwrite),
    )
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if api_key and api_key in serialized:
        raise RuntimeError("Provider credential leaked into snapshot output")
    print(serialized)


if __name__ == "__main__":
    main()

