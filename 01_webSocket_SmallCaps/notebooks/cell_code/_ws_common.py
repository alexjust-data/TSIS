from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_webSocket_SmallCaps")
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
CELL_CODE_DIR = NOTEBOOKS_DIR / "cell_code"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw_ws"
CURATED_DIR = DATA_DIR / "curated_ws"

DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "AMD", "PLTR"]
DEFAULT_CHANNELS = ["AM", "T"]


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def ensure_layout() -> dict[str, Path]:
    for path in [RUNTIME_DIR, DATA_DIR, RAW_DIR, CURATED_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    return {
        "project_root": PROJECT_ROOT,
        "notebooks_dir": NOTEBOOKS_DIR,
        "cell_code_dir": CELL_CODE_DIR,
        "runtime_dir": RUNTIME_DIR,
        "data_dir": DATA_DIR,
        "raw_dir": RAW_DIR,
        "curated_dir": CURATED_DIR,
    }


def resolve_api_key() -> tuple[str | None, str | None]:
    for env_name in ("MASSIVE_API_KEY", "POLYGON_API_KEY"):
        value = os.environ.get(env_name)
        if value:
            return env_name, value
    return None, None


def build_ws_url(feed_mode: str, asset_class: str = "stocks") -> str:
    if feed_mode == "realtime":
        return f"wss://socket.massive.com/{asset_class}"
    if feed_mode == "delayed":
        return f"wss://delayed.massive.com/{asset_class}"
    raise ValueError(f"Unsupported feed_mode: {feed_mode}")


def normalize_csv_arg(raw_value: str | None, default: list[str]) -> list[str]:
    if not raw_value:
        return default[:]
    return [item.strip().upper() for item in raw_value.split(",") if item.strip()]


def build_subscription(channels: list[str], symbols: list[str]) -> str:
    parts: list[str] = []
    for channel in channels:
        for symbol in symbols:
            parts.append(f"{channel}.{symbol}")
    return ",".join(parts)


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

