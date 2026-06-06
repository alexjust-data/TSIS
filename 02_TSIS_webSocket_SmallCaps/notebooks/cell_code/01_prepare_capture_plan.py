from __future__ import annotations

import argparse
import json
from pathlib import Path

from _ws_common import (
    CURATED_DIR,
    DEFAULT_CHANNELS,
    DEFAULT_TICKERS,
    RAW_DIR,
    build_subscription,
    build_ws_url,
    dump_json,
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_layout()
    api_env, api_key = resolve_api_key()
    channels = normalize_csv_arg(args.channels, DEFAULT_CHANNELS)
    symbols = normalize_csv_arg(args.symbols, DEFAULT_TICKERS)
    subscription = build_subscription(channels, symbols)

    run_plan = {
        "generated_at_utc": utc_now_iso(),
        "feed_mode": args.feed_mode,
        "ws_url": build_ws_url(args.feed_mode),
        "api_key_env": api_env,
        "api_key_present": bool(api_key),
        "channels": channels,
        "symbols": symbols,
        "subscription": subscription,
        "duration_sec": args.duration_sec,
        "label": args.label,
        "raw_output_dir": str(RAW_DIR / args.label),
        "curated_output_dir": str(CURATED_DIR / args.label),
    }

    plan_path = Path(RAW_DIR / args.label / "capture_plan.json")
    dump_json(plan_path, run_plan)
    print(json.dumps(run_plan, indent=2))
    print(f"\nPlan guardado en: {plan_path}")


if __name__ == "__main__":
    main()
