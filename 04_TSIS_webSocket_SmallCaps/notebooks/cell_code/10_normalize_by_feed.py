from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from _ws_common import CURATED_DIR, RAW_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run")
    return parser.parse_args()


def load_raw_events(raw_path: Path) -> list[dict]:
    rows: list[dict] = []
    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            event = payload["event"]
            rows.append(
                {
                    "captured_at_utc": payload["captured_at_utc"],
                    "ev": event.get("ev"),
                    "sym": event.get("sym"),
                    "event_json": event,
                }
            )
    return rows


def normalize_trades(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return pd.DataFrame(
        {
            "captured_at_utc": df["captured_at_utc"],
            "sym": df["sym"],
            "event_time": df["event_json"].map(lambda x: x.get("t")),
            "sequence": df["event_json"].map(lambda x: x.get("q")),
            "trade_id": df["event_json"].map(lambda x: x.get("i")),
            "exchange": df["event_json"].map(lambda x: x.get("x")),
            "price": df["event_json"].map(lambda x: x.get("p")),
            "size": df["event_json"].map(lambda x: x.get("s")),
            "tape": df["event_json"].map(lambda x: x.get("z")),
            "conditions": df["event_json"].map(lambda x: json.dumps(x.get("c"))),
            "raw_event": df["event_json"].map(lambda x: json.dumps(x, separators=(",", ":"))),
        }
    )


def normalize_quotes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return pd.DataFrame(
        {
            "captured_at_utc": df["captured_at_utc"],
            "sym": df["sym"],
            "event_time": df["event_json"].map(lambda x: x.get("t")),
            "sequence": df["event_json"].map(lambda x: x.get("q")),
            "bid_exchange": df["event_json"].map(lambda x: x.get("bx")),
            "bid_price": df["event_json"].map(lambda x: x.get("bp")),
            "bid_size": df["event_json"].map(lambda x: x.get("bs")),
            "ask_exchange": df["event_json"].map(lambda x: x.get("ax")),
            "ask_price": df["event_json"].map(lambda x: x.get("ap")),
            "ask_size": df["event_json"].map(lambda x: x.get("as")),
            "conditions": df["event_json"].map(lambda x: json.dumps(x.get("c"))),
            "indicators": df["event_json"].map(lambda x: json.dumps(x.get("i"))),
            "tape": df["event_json"].map(lambda x: x.get("z")),
            "raw_event": df["event_json"].map(lambda x: json.dumps(x, separators=(",", ":"))),
        }
    )


def normalize_aggs(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return pd.DataFrame(
        {
            "captured_at_utc": df["captured_at_utc"],
            "sym": df["sym"],
            "window_start": df["event_json"].map(lambda x: x.get("s")),
            "window_end": df["event_json"].map(lambda x: x.get("e")),
            "open": df["event_json"].map(lambda x: x.get("o")),
            "high": df["event_json"].map(lambda x: x.get("h")),
            "low": df["event_json"].map(lambda x: x.get("l")),
            "close": df["event_json"].map(lambda x: x.get("c")),
            "vwap": df["event_json"].map(lambda x: x.get("vw")),
            "avg_size": df["event_json"].map(lambda x: x.get("a")),
            "volume": df["event_json"].map(lambda x: x.get("v")),
            "accumulated_volume": df["event_json"].map(lambda x: x.get("av")),
            "official_open": df["event_json"].map(lambda x: x.get("op")),
            "tape": df["event_json"].map(lambda x: x.get("z")),
            "otc": df["event_json"].map(lambda x: x.get("otc")),
            "raw_event": df["event_json"].map(lambda x: json.dumps(x, separators=(",", ":"))),
        }
    )


def write_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def main() -> None:
    args = parse_args()
    raw_path = RAW_DIR / args.label / "events.jsonl"
    out_dir = CURATED_DIR / args.label / "normalized"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_raw_events(raw_path)
    raw_df = pd.DataFrame(rows)

    frames = {
        "trades": normalize_trades(raw_df[raw_df["ev"] == "T"].copy()),
        "quotes": normalize_quotes(raw_df[raw_df["ev"] == "Q"].copy()),
        "minute_aggs": normalize_aggs(raw_df[raw_df["ev"] == "AM"].copy()),
        "second_aggs": normalize_aggs(raw_df[raw_df["ev"] == "A"].copy()),
        "status": raw_df[raw_df["ev"] == "status"][["captured_at_utc", "ev", "sym"]].copy(),
    }

    manifest: dict[str, dict[str, object]] = {}
    for name, frame in frames.items():
        output_path = out_dir / f"{name}.parquet"
        if frame.empty:
            manifest[name] = {"rows": 0, "path": str(output_path), "written": False}
            continue
        write_frame(frame, output_path)
        manifest[name] = {"rows": int(len(frame)), "path": str(output_path), "written": True}

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print(f"\nManifest: {manifest_path}")


if __name__ == "__main__":
    main()
