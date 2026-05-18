from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from typing import Any

import websockets

from _ws_common import (
    CURATED_DIR,
    DEFAULT_CHANNELS,
    DEFAULT_TICKERS,
    RAW_DIR,
    build_subscription,
    build_ws_url,
    ensure_layout,
    normalize_csv_arg,
    resolve_api_key,
    utc_now_iso,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed-mode", choices=["realtime", "delayed"], default="realtime")
    parser.add_argument("--channels", default="AM,T")
    parser.add_argument("--symbols", default="AAPL,MSFT,NVDA,AMD,PLTR")
    parser.add_argument("--duration-sec", type=int, default=60)
    parser.add_argument("--label", default="prototype")
    parser.add_argument("--max-reconnects", type=int, default=5)
    parser.add_argument("--reconnect-delay-sec", type=float, default=2.0)
    return parser.parse_args()


def flatten_events(message_text: str) -> list[dict[str, Any]]:
    payload = json.loads(message_text)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


async def run_capture(args: argparse.Namespace) -> None:
    ensure_layout()
    api_env, api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError("Missing MASSIVE_API_KEY or POLYGON_API_KEY")

    channels = normalize_csv_arg(args.channels, DEFAULT_CHANNELS)
    symbols = normalize_csv_arg(args.symbols, DEFAULT_TICKERS)
    subscription = build_subscription(channels, symbols)
    ws_url = build_ws_url(args.feed_mode)

    run_dir = RAW_DIR / args.label
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "events_resilient.jsonl"
    meta_path = run_dir / "capture_resilient_meta.json"
    log_path = run_dir / "capture_resilient_log.jsonl"

    counters: Counter[str] = Counter()
    total_messages = 0
    total_events = 0
    reconnect_attempts = 0
    successful_connections = 0
    start_utc = utc_now_iso()
    deadline = asyncio.get_running_loop().time() + args.duration_sec

    def append_log(payload: dict[str, Any]) -> None:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, separators=(",", ":")) + "\n")

    with raw_path.open("w", encoding="utf-8") as raw_file:
        while asyncio.get_running_loop().time() < deadline:
            try:
                append_log({"ts_utc": utc_now_iso(), "type": "connect_attempt", "ws_url": ws_url})
                async with websockets.connect(ws_url, max_size=None, ping_interval=20) as websocket:
                    successful_connections += 1
                    append_log({"ts_utc": utc_now_iso(), "type": "connected", "connection_num": successful_connections})

                    await websocket.send(json.dumps({"action": "auth", "params": api_key}))
                    auth_reply = await websocket.recv()
                    append_log({"ts_utc": utc_now_iso(), "type": "auth_reply", "payload": auth_reply})

                    await websocket.send(json.dumps({"action": "subscribe", "params": subscription}))
                    append_log({"ts_utc": utc_now_iso(), "type": "subscribed", "subscription": subscription})

                    while asyncio.get_running_loop().time() < deadline:
                        timeout = max(deadline - asyncio.get_running_loop().time(), 0.1)
                        try:
                            message_text = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                        except TimeoutError:
                            continue

                        total_messages += 1
                        events = flatten_events(message_text)
                        if not events:
                            continue

                        for event in events:
                            total_events += 1
                            event_type = str(event.get("ev", "UNKNOWN"))
                            counters[event_type] += 1
                            raw_file.write(
                                json.dumps(
                                    {
                                        "captured_at_utc": utc_now_iso(),
                                        "event": event,
                                    },
                                    separators=(",", ":"),
                                )
                                + "\n"
                            )

                    break

            except Exception as exc:
                reconnect_attempts += 1
                append_log(
                    {
                        "ts_utc": utc_now_iso(),
                        "type": "connection_error",
                        "reconnect_attempt": reconnect_attempts,
                        "error": repr(exc),
                    }
                )
                if reconnect_attempts > args.max_reconnects:
                    append_log(
                        {
                            "ts_utc": utc_now_iso(),
                            "type": "abort_max_reconnects",
                            "max_reconnects": args.max_reconnects,
                        }
                    )
                    raise
                await asyncio.sleep(args.reconnect_delay_sec)

    meta = {
        "started_at_utc": start_utc,
        "finished_at_utc": utc_now_iso(),
        "feed_mode": args.feed_mode,
        "ws_url": ws_url,
        "api_key_env": api_env,
        "channels": channels,
        "symbols": symbols,
        "subscription": subscription,
        "duration_sec": args.duration_sec,
        "total_messages": total_messages,
        "total_events": total_events,
        "event_counts": dict(counters),
        "successful_connections": successful_connections,
        "reconnect_attempts": reconnect_attempts,
        "raw_path": str(raw_path),
        "log_path": str(log_path),
        "curated_dir": str(CURATED_DIR / args.label),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(f"\nRaw events: {raw_path}")
    print(f"Log: {log_path}")
    print(f"Metadata: {meta_path}")


def main() -> None:
    args = parse_args()
    asyncio.run(run_capture(args))


if __name__ == "__main__":
    main()
