"""Configuration loading and validation for DAS CMD API capture v0."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_DATA_ROOT = Path("E:/TSIS/data_DAS_live")
DEFAULT_SESSIONS = ("premarket", "regular_market", "afterhours")
DEFAULT_CHANNELS = ("Lv1", "tms", "Lv2", "TOPLIST", "DAYCHART", "MINCHART")
DEFAULT_SYMBOL_QUERIES = ("SHORTINFO", "LDLU", "SymStatus")
DEFAULT_ACCOUNT_QUERIES = ("BP", "AccountInfo", "POSITIONS", "ORDERS", "TRADES", "ROUTESTATUS", "LOCATES", "INTMSGS")


@dataclass(frozen=True)
class ScreenerDenominator:
    sessions: tuple[str, ...] = DEFAULT_SESSIONS
    market_cap_usd_lt: int = 100_000_000
    price_usd_min: float = 0.50
    price_usd_max: float = 20.00
    min_volume_shares: int = 300_000
    volume_source_priority: tuple[str, ...] = (
        "das_lv1_V",
        "das_time_and_sales_sum_if_capture_window_complete",
        "unavailable_record_null",
    )
    market_cap_source: str = "governed_tsis_reference_or_universe_until_das_field_is_proven"


@dataclass(frozen=True)
class CaptureConfig:
    schema_version: str = "das_cmdapi_capture_v0_1"
    host: str = "127.0.0.1"
    port: int = 9800
    data_root: Path = DEFAULT_DATA_ROOT
    login_mode: str = "manual_operator_login"
    socket_login_enabled: bool = False
    locate_queries_enabled: bool = False
    symbols: tuple[str, ...] = ("SOXS",)
    channels: tuple[str, ...] = DEFAULT_CHANNELS
    symbol_queries: tuple[str, ...] = DEFAULT_SYMBOL_QUERIES
    account_queries: tuple[str, ...] = DEFAULT_ACCOUNT_QUERIES
    daychart_days_back: int = 10
    minchart_minutes_back: int = 60
    screener: ScreenerDenominator = field(default_factory=ScreenerDenominator)


def _as_tuple(value: Any, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if isinstance(value, str):
        return (value,)
    return tuple(str(x) for x in value)


def load_config(path: Path | None) -> CaptureConfig:
    if path is None:
        return CaptureConfig()
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    screener_raw = raw.get("screener_initial_denominator", {})
    screener = ScreenerDenominator(
        sessions=_as_tuple(screener_raw.get("sessions"), DEFAULT_SESSIONS),
        market_cap_usd_lt=int(screener_raw.get("market_cap_usd_lt", 100_000_000)),
        price_usd_min=float(screener_raw.get("price_usd_min", 0.50)),
        price_usd_max=float(screener_raw.get("price_usd_max", 20.00)),
        min_volume_shares=int(screener_raw.get("min_volume_shares", 300_000)),
        volume_source_priority=_as_tuple(
            screener_raw.get("volume_source_priority"),
            (
                "das_lv1_V",
                "das_time_and_sales_sum_if_capture_window_complete",
                "unavailable_record_null",
            ),
        ),
        market_cap_source=str(
            screener_raw.get(
                "market_cap_source",
                "governed_tsis_reference_or_universe_until_das_field_is_proven",
            )
        ),
    )
    return CaptureConfig(
        schema_version=str(raw.get("schema_version", "das_cmdapi_capture_v0_1")),
        host=str(raw.get("host", "127.0.0.1")),
        port=int(raw.get("port", 9800)),
        data_root=Path(raw.get("data_root", str(DEFAULT_DATA_ROOT))),
        login_mode=str(raw.get("login_mode", "manual_operator_login")),
        socket_login_enabled=bool(raw.get("socket_login_enabled", False)),
        locate_queries_enabled=bool(raw.get("locate_queries_enabled", False)),
        symbols=tuple(s.upper() for s in _as_tuple(raw.get("symbols"), ("SOXS",))),
        channels=_as_tuple(raw.get("channels"), DEFAULT_CHANNELS),
        symbol_queries=_as_tuple(raw.get("symbol_queries"), DEFAULT_SYMBOL_QUERIES),
        account_queries=_as_tuple(raw.get("account_queries"), DEFAULT_ACCOUNT_QUERIES),
        daychart_days_back=int(raw.get("daychart_days_back", 10)),
        minchart_minutes_back=int(raw.get("minchart_minutes_back", 60)),
        screener=screener,
    )


def config_to_dict(config: CaptureConfig) -> dict[str, Any]:
    return {
        "schema_version": config.schema_version,
        "host": config.host,
        "port": config.port,
        "data_root": str(config.data_root),
        "login_mode": config.login_mode,
        "socket_login_enabled": config.socket_login_enabled,
        "locate_queries_enabled": config.locate_queries_enabled,
        "symbols": list(config.symbols),
        "channels": list(config.channels),
        "symbol_queries": list(config.symbol_queries),
        "account_queries": list(config.account_queries),
        "daychart_days_back": config.daychart_days_back,
        "minchart_minutes_back": config.minchart_minutes_back,
        "screener_initial_denominator": {
            "sessions": list(config.screener.sessions),
            "market_cap_usd_lt": config.screener.market_cap_usd_lt,
            "price_usd_min": config.screener.price_usd_min,
            "price_usd_max": config.screener.price_usd_max,
            "min_volume_shares": config.screener.min_volume_shares,
            "volume_source_priority": list(config.screener.volume_source_priority),
            "market_cap_source": config.screener.market_cap_source,
        },
    }
