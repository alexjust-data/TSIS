"""Configuration loading and validation for DAS CMD API capture v0."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .market_cap import DEFAULT_MARKET_CAP_REFERENCE_PATH

DEFAULT_DATA_ROOT = Path("E:/TSIS/data_DAS_live")
DEFAULT_SESSIONS = ("premarket", "regular_market", "afterhours")
DEFAULT_CHANNELS = ("Lv1", "tms", "Lv2", "TOPLIST", "DAYCHART", "MINCHART")
DEFAULT_SYMBOL_QUERIES = ("SHORTINFO", "LDLU", "SymStatus")
DEFAULT_ACCOUNT_QUERIES = ("BP", "AccountInfo", "POSITIONS", "ORDERS", "TRADES", "ROUTESTATUS", "LOCATES", "INTMSGS")
DEFAULT_LOCATE_PRICE_ROUTES = ("SAGE", "TESTSL")
MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT = 100


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
    login_mode: str = "terminal_prompt_socket_login"
    socket_login_enabled: bool = False
    locate_queries_enabled: bool = False
    account_queries_enabled: bool = False
    allow_invalid_login_continue: bool = False
    locate_price_shares: int = 100
    locate_price_routes: tuple[str, ...] = DEFAULT_LOCATE_PRICE_ROUTES
    symbols: tuple[str, ...] = ("SOXS",)
    candidate_file_path: Path | None = None
    candidate_file_filter_status: str | None = None
    skip_screener: bool = False
    channels: tuple[str, ...] = DEFAULT_CHANNELS
    symbol_queries: tuple[str, ...] = DEFAULT_SYMBOL_QUERIES
    account_queries: tuple[str, ...] = DEFAULT_ACCOUNT_QUERIES
    daychart_days_back: int = 10
    minchart_minutes_back: int = 60
    max_screener_symbols: int = MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT
    allow_large_screener_scan: bool = False
    screener_symbol_source: str = "seed_plus_toplist"
    screener_reference_active_only: bool = True
    query_wait_seconds: float = 1.0
    locate_query_wait_seconds: float = 3.0
    screener_wait_seconds: float = 1.0
    toplist_wait_seconds: float = 3.0
    full_capture_wait_seconds: float = 3.0
    stream_poll_seconds: float = 1.0
    capture_seconds: int | None = None
    max_response_bytes: int = 50_000_000
    market_cap_reference_path: Path | None = DEFAULT_MARKET_CAP_REFERENCE_PATH
    screener: ScreenerDenominator = field(default_factory=ScreenerDenominator)


def _as_tuple(value: Any, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if isinstance(value, str):
        return (value,)
    return tuple(str(x) for x in value)


def _optional_path(value: Any, default: Path | None) -> Path | None:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return None
    return Path(text)


def _optional_int(value: Any, default: int | None) -> int | None:
    if value is None or value == "":
        return default
    return int(value)


def load_config(path: Path | None) -> CaptureConfig:
    if path is None:
        return CaptureConfig()
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    screener_raw = raw.get("screener_initial_denominator", {})
    allow_large_screener_scan = bool(raw.get("allow_large_screener_scan", False))
    max_screener_symbols = max(1, int(raw.get("max_screener_symbols", MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT)))
    if not allow_large_screener_scan:
        max_screener_symbols = min(max_screener_symbols, MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT)
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
        login_mode=str(raw.get("login_mode", "terminal_prompt_socket_login")),
        socket_login_enabled=bool(raw.get("socket_login_enabled", False)),
        locate_queries_enabled=bool(raw.get("locate_queries_enabled", False)),
        account_queries_enabled=bool(raw.get("account_queries_enabled", False)),
        allow_invalid_login_continue=bool(raw.get("allow_invalid_login_continue", False)),
        locate_price_shares=max(1, int(raw.get("locate_price_shares", 100))),
        locate_price_routes=tuple(r.upper() for r in _as_tuple(raw.get("locate_price_routes"), DEFAULT_LOCATE_PRICE_ROUTES)),
        symbols=tuple(s.upper() for s in _as_tuple(raw.get("symbols"), ("SOXS",))),
        candidate_file_path=_optional_path(raw.get("candidate_file_path"), None),
        candidate_file_filter_status=(str(raw.get("candidate_file_filter_status")) if raw.get("candidate_file_filter_status") is not None else None),
        skip_screener=bool(raw.get("skip_screener", False)),
        channels=_as_tuple(raw.get("channels"), DEFAULT_CHANNELS),
        symbol_queries=_as_tuple(raw.get("symbol_queries"), DEFAULT_SYMBOL_QUERIES),
        account_queries=_as_tuple(raw.get("account_queries"), DEFAULT_ACCOUNT_QUERIES),
        daychart_days_back=int(raw.get("daychart_days_back", 10)),
        minchart_minutes_back=int(raw.get("minchart_minutes_back", 60)),
        max_screener_symbols=max_screener_symbols,
        allow_large_screener_scan=allow_large_screener_scan,
        screener_symbol_source=str(raw.get("screener_symbol_source", "seed_plus_toplist")),
        screener_reference_active_only=bool(raw.get("screener_reference_active_only", True)),
        query_wait_seconds=float(raw.get("query_wait_seconds", 1.0)),
        locate_query_wait_seconds=float(raw.get("locate_query_wait_seconds", 3.0)),
        screener_wait_seconds=float(raw.get("screener_wait_seconds", 1.0)),
        toplist_wait_seconds=float(raw.get("toplist_wait_seconds", 3.0)),
        full_capture_wait_seconds=float(raw.get("full_capture_wait_seconds", 3.0)),
        stream_poll_seconds=float(raw.get("stream_poll_seconds", 1.0)),
        capture_seconds=_optional_int(raw.get("capture_seconds"), None),
        max_response_bytes=int(raw.get("max_response_bytes", 50_000_000)),
        market_cap_reference_path=_optional_path(raw.get("market_cap_reference_path"), DEFAULT_MARKET_CAP_REFERENCE_PATH),
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
        "account_queries_enabled": config.account_queries_enabled,
        "allow_invalid_login_continue": config.allow_invalid_login_continue,
        "locate_price_shares": config.locate_price_shares,
        "locate_price_routes": list(config.locate_price_routes),
        "symbols": list(config.symbols),
        "candidate_file_path": str(config.candidate_file_path) if config.candidate_file_path else None,
        "candidate_file_filter_status": config.candidate_file_filter_status,
        "skip_screener": config.skip_screener,
        "channels": list(config.channels),
        "symbol_queries": list(config.symbol_queries),
        "account_queries": list(config.account_queries),
        "daychart_days_back": config.daychart_days_back,
        "minchart_minutes_back": config.minchart_minutes_back,
        "max_screener_symbols": config.max_screener_symbols,
        "allow_large_screener_scan": config.allow_large_screener_scan,
        "screener_symbol_source": config.screener_symbol_source,
        "screener_reference_active_only": config.screener_reference_active_only,
        "query_wait_seconds": config.query_wait_seconds,
        "locate_query_wait_seconds": config.locate_query_wait_seconds,
        "screener_wait_seconds": config.screener_wait_seconds,
        "toplist_wait_seconds": config.toplist_wait_seconds,
        "full_capture_wait_seconds": config.full_capture_wait_seconds,
        "stream_poll_seconds": config.stream_poll_seconds,
        "capture_seconds": config.capture_seconds,
        "max_response_bytes": config.max_response_bytes,
        "market_cap_reference_path": str(config.market_cap_reference_path) if config.market_cap_reference_path else None,
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