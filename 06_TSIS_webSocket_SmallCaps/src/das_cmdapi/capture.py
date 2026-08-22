"""Terminal entry point for DAS CMD API live capture v0."""

from __future__ import annotations

import argparse
import csv
import getpass
import json
import os
import sys
import time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from .allowlist import BLOCKED_PREFIXES, redacted_command, validate_command
from .client import DasCmdApiClient
from .config import CaptureConfig, MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT, config_to_dict, load_config
from .market_cap import MarketCapReference, load_market_cap_reference
from .parsing import (
    extract_price_volume_from_quote,
    infer_data_family,
    infer_symbol,
    parse_quote_line,
    parse_toplist_symbols,
    split_response_lines,
)
from .run_files import append_jsonl, append_log, atomic_write_json, ensure_run_files, make_run_id, raw_run_root, screener_run_root, utc_now
from .screener import candidate_passes_denominator, denominator_to_dict

ET_ZONE = ZoneInfo("America/New_York")
CSV_FIELDS = (
    "run_id",
    "observed_at_utc",
    "market_date",
    "session",
    "symbol",
    "filter_status",
    "failure_reasons",
    "price_usd",
    "price_source",
    "volume_shares",
    "volume_source",
    "market_cap_usd",
    "market_cap_source",
    "market_cap_asof_date",
    "quote_raw_line",
)


def build_command_plan(config: CaptureConfig) -> list[str]:
    commands: list[str] = ["ECHO OFF", "CLIENT", "ReturnFullLv1 YES"]
    if config.socket_login_enabled:
        commands.insert(0, "LOGIN <user> <password> <account> 0")
    if "TOPLIST" in {c.upper() for c in config.channels}:
        commands.extend(["SB TOPLIST", "UNSB TOPLIST"])
    for symbol in config.symbols:
        channels = {c.upper() for c in config.channels}
        if "LV1" in channels:
            commands.extend([f"SB {symbol} Lv1", f"UNSB {symbol} Lv1"])
        if "TMS" in channels:
            commands.extend([f"SB {symbol} tms", f"UNSB {symbol} tms"])
        if "LV2" in channels:
            commands.extend([f"SB {symbol} Lv2", f"UNSB {symbol} Lv2"])
        if "DAYCHART" in channels:
            commands.extend([f"SB {symbol} DAYCHART <start> <end>", f"UNSB {symbol} DAYCHART"])
        if "MINCHART" in channels:
            commands.extend([f"SB {symbol} MINCHART <start> <end> 1", f"UNSB {symbol} MINCHART"])
        for query in config.symbol_queries:
            q = query.upper()
            if q == "SHORTINFO":
                commands.append(f"GET SHORTINFO {symbol}")
            elif q == "LDLU":
                commands.append(f"GET LDLU {symbol}")
            elif q == "SYMSTATUS":
                commands.append(f"GET SymStatus {symbol}")
    if config.account_queries_enabled:
        for query in config.account_queries:
            commands.append(_account_query_command(query))
    if config.locate_queries_enabled:
        commands.extend(["SLReuseQuery ALL", "SLRouteMinCharge ALLROUTE"])
        for symbol in config.symbols:
            commands.extend([f"SLAvailQuery <account> {symbol}", f"SLReuseQuery {symbol}"])
            for route in config.locate_price_routes:
                commands.append(f"SLPRICEINQUIRE {symbol} {config.locate_price_shares} {route}")
    commands.append("QUIT")
    return commands


def validate_plan(config: CaptureConfig, commands: Iterable[str]) -> list[dict[str, str | bool]]:
    rows: list[dict[str, str | bool]] = []
    for command in commands:
        validation = validate_command(
            command,
            socket_login_enabled=config.socket_login_enabled,
            locate_queries_enabled=config.locate_queries_enabled,
        )
        rows.append(
            {
                "command": redacted_command(command),
                "allowed": validation.allowed,
                "blocked": validation.blocked,
                "reason": validation.reason,
            }
        )
    return rows


def _channel_enabled(config: CaptureConfig, channel: str) -> bool:
    return channel.upper() in {c.upper() for c in config.channels}


def _yes_answer(value: str) -> bool:
    return value.strip().lower() in {"s", "si", "sí", "y", "yes"}


def _prompt_credentials() -> tuple[str, str, str]:
    print("DAS CMD API credential prompt. Credentials are not written to disk.")
    username = input("DAS username: ").strip()
    password = getpass.getpass("DAS password: ")
    account = input("DAS account: ").strip()
    if not username or not password or not account:
        raise SystemExit("Missing DAS username, password, or account.")
    return username, password, account


def _prompt_download() -> bool:
    return _yes_answer(input("Descargar full data para candidatos PASS? [s/N]: "))


def _market_clock() -> tuple[str, str]:
    now_et = datetime.now(timezone.utc).astimezone(ET_ZONE)
    market_date = now_et.date().isoformat()
    minutes = now_et.hour * 60 + now_et.minute
    if 4 * 60 <= minutes < 9 * 60 + 30:
        session = "premarket"
    elif 9 * 60 + 30 <= minutes < 16 * 60:
        session = "regular_market"
    elif 16 * 60 <= minutes < 20 * 60:
        session = "afterhours"
    else:
        session = "outside_market_hours"
    return market_date, session


def _chart_ranges(config: CaptureConfig) -> dict[str, str]:
    now_et = datetime.now(timezone.utc).astimezone(ET_ZONE)
    day_start = (now_et.date() - timedelta(days=config.daychart_days_back)).strftime("%Y/%m/%d")
    day_end = now_et.date().strftime("%Y/%m/%d")
    min_start = (now_et - timedelta(minutes=config.minchart_minutes_back)).strftime("%Y/%m/%d-%H:%M")
    min_end = now_et.strftime("%Y/%m/%d-%H:%M")
    return {
        "day_start": day_start,
        "day_end": day_end,
        "min_start": min_start,
        "min_end": min_end,
    }


def _status_from_lines(lines: list[str]) -> str:
    if not lines:
        return "no_response"
    upper = "\n".join(lines).upper()
    if "ERROR" in upper or "FAILED" in upper:
        return "error_response"
    return "ok"


def _active_subscription_rows(active: set[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"symbol": symbol, "channel": channel} for symbol, channel in sorted(active)]


def _write_subscription_state(paths: dict[str, Path], run_id: str, mode: str, active: set[tuple[str, str]]) -> None:
    atomic_write_json(
        paths["subscription_state"],
        {
            "schema_version": "das_cmdapi_subscription_state_v0_1",
            "updated_at_utc": utc_now(),
            "run_id": run_id,
            "mode": mode,
            "active_subscriptions": _active_subscription_rows(active),
        },
    )


def _write_heartbeat(
    paths: dict[str, Path],
    run_id: str,
    mode: str,
    stage: str,
    state: dict[str, Any],
    *,
    last_error: str | None = None,
    active_symbol: str | None = None,
) -> None:
    atomic_write_json(
        paths["heartbeat"],
        {
            "schema_version": "das_cmdapi_heartbeat_v0_1",
            "updated_at_utc": utc_now(),
            "run_id": run_id,
            "stage": stage,
            "mode": mode,
            "das_commands_sent": state.get("das_commands_sent", 0),
            "command_transcript_lines": state.get("command_transcript_lines", 0),
            "event_lines": state.get("event_lines", 0),
            "response_bytes": state.get("response_bytes", 0),
            "evaluated_candidates": state.get("evaluated_candidates", 0),
            "passed_candidates": state.get("passed_candidates", 0),
            "active_symbol": active_symbol,
            "active_subscriptions": _active_subscription_rows(state.get("active_subscriptions", set())),
            "last_error": last_error or state.get("last_error"),
        },
    )


def _record_response(
    paths: dict[str, Path],
    run_id: str,
    mode: str,
    state: dict[str, Any],
    *,
    command: str,
    response: str | None,
    wait_seconds: float,
    stage: str,
    sent_to_socket: bool,
    allowed: bool,
    blocked: bool,
    reason: str,
    active_symbol: str | None = None,
    status_override: str | None = None,
    empty_event_type: str = "no_response",
    write_empty_event: bool = True,
) -> list[str]:
    observed_at = utc_now()
    lines = split_response_lines(response)
    status = status_override or _status_from_lines(lines)
    response_bytes = len(response.encode("ascii", errors="replace")) if response else 0
    transcript = {
        "schema_version": "das_cmdapi_command_transcript_v0_1",
        "observed_at_utc": observed_at,
        "run_id": run_id,
        "mode": mode,
        "stage": stage,
        "command": redacted_command(command),
        "allowed": allowed,
        "blocked": blocked,
        "reason": reason,
        "sent_to_socket": sent_to_socket,
        "wait_seconds": wait_seconds,
        "status": status,
        "response_line_count": len(lines),
        "response_bytes": response_bytes,
        "response": response if response else None,
    }
    append_jsonl(paths["command_transcript"], transcript)
    state["command_transcript_lines"] = state.get("command_transcript_lines", 0) + 1
    state["response_bytes"] = state.get("response_bytes", 0) + response_bytes

    if lines:
        for line_index, line in enumerate(lines):
            data_family = infer_data_family(command, line)
            symbol = infer_symbol(command, line) or active_symbol
            event: dict[str, Any] = {
                "schema_version": "das_cmdapi_event_v0_1",
                "observed_at_utc": observed_at,
                "run_id": run_id,
                "mode": mode,
                "stage": stage,
                "event_type": "cmdapi_line",
                "command": redacted_command(command),
                "data_family": data_family,
                "symbol": symbol,
                "line_index": line_index,
                "raw_line": line,
            }
            quote_fields = parse_quote_line(line)
            if quote_fields:
                price, volume, price_source = extract_price_volume_from_quote(quote_fields)
                event["parsed_quote_fields"] = quote_fields
                event["price_usd"] = price
                event["price_source"] = price_source
                event["volume_shares"] = volume
                event["volume_source"] = "das_lv1_V" if volume is not None else None
            append_jsonl(paths["events"], event)
            state["event_lines"] = state.get("event_lines", 0) + 1
    elif write_empty_event:
        append_jsonl(
            paths["events"],
            {
                "schema_version": "das_cmdapi_event_v0_1",
                "observed_at_utc": observed_at,
                "run_id": run_id,
                "mode": mode,
                "stage": stage,
                "event_type": empty_event_type,
                "command": redacted_command(command),
                "data_family": infer_data_family(command),
                "symbol": active_symbol or infer_symbol(command),
                "raw_line": None,
            },
        )
        state["event_lines"] = state.get("event_lines", 0) + 1

    _write_heartbeat(paths, run_id, mode, stage, state, active_symbol=active_symbol)
    return lines


def _send_and_record(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    mode: str,
    config: CaptureConfig,
    state: dict[str, Any],
    command: str,
    *,
    wait_seconds: float,
    stage: str,
    active_symbol: str | None = None,
) -> tuple[str, list[str]]:
    validation = validate_command(
        command,
        socket_login_enabled=config.socket_login_enabled,
        locate_queries_enabled=config.locate_queries_enabled,
    )
    if not validation.allowed:
        _record_response(
            paths,
            run_id,
            mode,
            state,
            command=command,
            response=None,
            wait_seconds=wait_seconds,
            stage=stage,
            sent_to_socket=False,
            allowed=False,
            blocked=validation.blocked,
            reason=validation.reason,
            active_symbol=active_symbol,
            status_override="blocked",
            empty_event_type="blocked_command",
        )
        raise ValueError(f"Refusing DAS command {redacted_command(command)!r}: {validation.reason}")
    response = client.send_readonly(command, wait_seconds=wait_seconds, max_bytes=config.max_response_bytes)
    state["das_commands_sent"] = state.get("das_commands_sent", 0) + 1
    lines = _record_response(
        paths,
        run_id,
        mode,
        state,
        command=command,
        response=response,
        wait_seconds=wait_seconds,
        stage=stage,
        sent_to_socket=True,
        allowed=True,
        blocked=False,
        reason=validation.reason,
        active_symbol=active_symbol,
    )
    return response, lines


def _login_confirmed(lines: list[str]) -> bool:
    upper = "\n".join(lines).upper()
    return "#LOGIN SUCCESSED" in upper or "#LOGIN SUCCEEDED" in upper or "LOGIN SUCCESSED" in upper


def _ensure_screener_files(data_root: Path, run_id: str) -> dict[str, Path]:
    root = screener_run_root(data_root, run_id)
    root.mkdir(parents=True, exist_ok=False)
    paths = {
        "root": root,
        "manifest": root / "screener_manifest.json",
        "candidates_jsonl": root / "candidates.jsonl",
        "candidates_csv": root / "candidates.csv",
    }
    paths["candidates_jsonl"].touch()
    return paths


def _candidate_csv_cell(value: Any) -> str | int | float | None:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _write_candidates_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_FIELDS), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _candidate_csv_cell(row.get(key)) for key in CSV_FIELDS})


def _coerce_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _candidate_symbol_from_row(row: dict[str, Any]) -> str:
    for key in ("symbol", "ticker", "symb"):
        value = row.get(key)
        if value is not None:
            symbol = str(value).strip().upper()
            if symbol:
                return symbol
    return ""


def _read_candidate_rows_from_file(path: Path, filter_status: str | None) -> list[dict[str, Any]]:
    selected = path
    status_filter = filter_status.strip().upper() if filter_status else None
    rows: list[dict[str, Any]] = []
    if selected.suffix.lower() == ".jsonl":
        with selected.open("r", encoding="utf-8-sig") as fh:
            for line in fh:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    continue
                if status_filter and str(row.get("filter_status", "")).strip().upper() != status_filter:
                    continue
                if _candidate_symbol_from_row(row):
                    rows.append(row)
    elif selected.suffix.lower() == ".csv":
        with selected.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if status_filter and str(row.get("filter_status", "")).strip().upper() != status_filter:
                    continue
                if _candidate_symbol_from_row(row):
                    rows.append(dict(row))
    else:
        with selected.open("r", encoding="utf-8-sig") as fh:
            for line in fh:
                symbol = line.strip().upper()
                if symbol and not symbol.startswith("#"):
                    rows.append({"symbol": symbol})
    return rows


def _candidate_symbols_from_file(path: Path, filter_status: str | None) -> list[str]:
    symbols: list[str] = []
    seen: set[str] = set()
    for row in _read_candidate_rows_from_file(path, filter_status):
        symbol = _candidate_symbol_from_row(row)
        if symbol and symbol not in seen:
            symbols.append(symbol)
            seen.add(symbol)
    return symbols


def _value_text(value: Any) -> str:
    if value is None or value == "":
        return "NA"
    return str(value)


def _collect_toplist_symbols(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
) -> list[str]:
    if not _channel_enabled(config, "TOPLIST"):
        print("TOPLIST: disabled by config; screener will use seed symbols only.", flush=True)
        return []
    print(f"TOPLIST: requesting DAS list; wait={config.toplist_wait_seconds}s.", flush=True)
    response, _lines = _send_and_record(
        client,
        paths,
        run_id,
        "live",
        config,
        state,
        "SB TOPLIST",
        wait_seconds=config.toplist_wait_seconds,
        stage="toplist_scan",
    )
    symbols = parse_toplist_symbols(response)
    print(f"TOPLIST: parsed {len(symbols)} symbols.", flush=True)
    _send_and_record(
        client,
        paths,
        run_id,
        "live",
        config,
        state,
        "UNSB TOPLIST",
        wait_seconds=config.query_wait_seconds,
        stage="toplist_scan",
    )
    return symbols


def _reference_record_is_scan_eligible(record: Any, *, active_only: bool) -> bool:
    if not active_only:
        return True
    status = str(getattr(record, "status_rebuilt", "") or "").strip().lower()
    classification = str(getattr(record, "classification_1b", "") or "").strip().lower()
    return status == "active" or classification.startswith("active_")


def _reference_symbol_list(config: CaptureConfig, market_caps: MarketCapReference) -> list[str]:
    source = config.screener_symbol_source.strip().lower()
    if source not in {"market_cap_reference", "seed_toplist_market_cap_reference", "tsis_universe"}:
        return []
    symbols: list[str] = []
    for record in sorted(market_caps.records.values(), key=lambda item: item.ticker):
        if _reference_record_is_scan_eligible(record, active_only=config.screener_reference_active_only):
            symbols.append(record.ticker)
    return symbols


def _candidate_symbol_list(
    config: CaptureConfig,
    toplist_symbols: list[str],
    market_caps: MarketCapReference | None = None,
) -> list[str]:
    source = config.screener_symbol_source.strip().lower()
    reference_symbols = _reference_symbol_list(config, market_caps) if market_caps else []
    if source in {"market_cap_reference", "tsis_universe"}:
        source_symbols = list(config.symbols) + reference_symbols + toplist_symbols
    elif source == "seed_toplist_market_cap_reference":
        source_symbols = list(config.symbols) + toplist_symbols + reference_symbols
    else:
        source_symbols = list(config.symbols) + toplist_symbols

    selected: list[str] = []
    seen: set[str] = set()
    for symbol in source_symbols:
        normalized = symbol.strip().upper()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        selected.append(normalized)
        if len(selected) >= config.max_screener_symbols:
            break
    return selected


def _latest_quote(lines: list[str], symbol: str) -> tuple[dict[str, Any] | None, str | None]:
    latest: dict[str, Any] | None = None
    raw_line: str | None = None
    for line in lines:
        fields = parse_quote_line(line)
        if fields and str(fields.get("symbol", "")).upper() == symbol.upper():
            latest = fields
            raw_line = line
    return latest, raw_line


def _trusted_candidate_rows_from_file(
    config: CaptureConfig,
    run_id: str,
    market_caps: MarketCapReference,
) -> list[dict[str, Any]]:
    if config.candidate_file_path is None:
        raise ValueError("skip_screener requires candidate_file_path")
    market_date, session_now = _market_clock()
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_row in _read_candidate_rows_from_file(config.candidate_file_path, config.candidate_file_filter_status):
        symbol = _candidate_symbol_from_row(source_row)
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        cap_record = market_caps.get(symbol)
        rows.append(
            {
                "schema_version": "das_cmdapi_candidate_registry_v0_1",
                "event_type": "trusted_candidate_from_file",
                "run_id": run_id,
                "observed_at_utc": utc_now(),
                "market_date": source_row.get("market_date") or market_date,
                "session": source_row.get("session") or session_now,
                "symbol": symbol,
                "price_usd": _coerce_number(source_row.get("price_usd")),
                "price_source": source_row.get("price_source"),
                "volume_shares": _coerce_number(source_row.get("volume_shares")),
                "volume_source": source_row.get("volume_source"),
                "market_cap_usd": _coerce_number(source_row.get("market_cap_usd")) if source_row.get("market_cap_usd") not in (None, "") else (cap_record.market_cap_usd if cap_record else None),
                "market_cap_source": source_row.get("market_cap_source") or (cap_record.source if cap_record else "unavailable_in_market_cap_reference"),
                "market_cap_asof_date": source_row.get("market_cap_asof_date") or (cap_record.asof_date if cap_record else None),
                "quote_raw_line": source_row.get("quote_raw_line"),
                "quote_fields": None,
                "toplist_seen": source_row.get("toplist_seen"),
                "filter_status": "PASS",
                "failure_reasons": [],
                "candidate_source": "trusted_candidate_file",
                "candidate_file_path": str(config.candidate_file_path),
                "source_run_id": source_row.get("run_id"),
                "denominator": denominator_to_dict(config.screener),
            }
        )
    return rows


def _write_trusted_candidate_outputs(
    paths: dict[str, Path],
    screener_paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    market_caps: MarketCapReference,
    rows: list[dict[str, Any]],
) -> None:
    for row in rows:
        append_jsonl(paths["candidate_registry"], row)
        append_jsonl(screener_paths["candidates_jsonl"], row)
    _write_candidates_csv(screener_paths["candidates_csv"], rows)
    atomic_write_json(
        screener_paths["manifest"],
        {
            "schema_version": "das_cmdapi_screener_manifest_v0_1",
            "created_at_utc": utc_now(),
            "run_id": run_id,
            "data_root": str(config.data_root),
            "screener_root": str(screener_paths["root"]),
            "denominator": denominator_to_dict(config.screener),
            "screener_skipped": True,
            "candidate_source": "trusted_candidate_file",
            "candidate_file_path": str(config.candidate_file_path) if config.candidate_file_path else None,
            "candidate_file_filter_status": config.candidate_file_filter_status,
            "toplist_symbols_seen": 0,
            "evaluated_symbols": len(rows),
            "passed_candidates": len(rows),
            "market_cap_reference": {
                "path": str(market_caps.path) if market_caps.path else None,
                "records": len(market_caps.records),
                "error": market_caps.error,
            },
            "output_files": {key: str(value) for key, value in screener_paths.items() if key != "root"},
        },
    )


def _evaluate_screener(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    screener_paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
    market_caps: MarketCapReference,
    symbols: list[str],
    toplist_symbols: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    toplist_set = set(toplist_symbols)
    total = len(symbols)
    print(
        "Screener: evaluating "
        f"{total} symbols with denominator "
        f"price={config.screener.price_usd_min}-{config.screener.price_usd_max}, "
        f"volume>={config.screener.min_volume_shares}, "
        f"market_cap<{config.screener.market_cap_usd_lt}.",
        flush=True,
    )
    for index, symbol in enumerate(symbols, start=1):
        market_date, session = _market_clock()
        _response, lines = _send_and_record(
            client,
            paths,
            run_id,
            "live",
            config,
            state,
            f"SB {symbol} Lv1",
            wait_seconds=config.screener_wait_seconds,
            stage="screener_lv1",
            active_symbol=symbol,
        )
        quote_fields, quote_raw_line = _latest_quote(lines, symbol)
        price, volume, price_source = extract_price_volume_from_quote(quote_fields)
        try:
            _send_and_record(
                client,
                paths,
                run_id,
                "live",
                config,
                state,
                f"UNSB {symbol} Lv1",
                wait_seconds=config.query_wait_seconds,
                stage="screener_lv1",
                active_symbol=symbol,
            )
        except Exception as exc:  # pragma: no cover - defensive cleanup path
            append_log(paths["capture_log"], f"warning unsub screener {symbol} Lv1 failed: {exc}")

        cap_record = market_caps.get(symbol)
        row: dict[str, Any] = {
            "schema_version": "das_cmdapi_candidate_registry_v0_1",
            "event_type": "screener_evaluated",
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "market_date": market_date,
            "session": session,
            "symbol": symbol,
            "price_usd": price,
            "price_source": price_source,
            "volume_shares": volume,
            "volume_source": "das_lv1_V" if volume is not None else None,
            "market_cap_usd": cap_record.market_cap_usd if cap_record else None,
            "market_cap_source": cap_record.source if cap_record else "unavailable_in_market_cap_reference",
            "market_cap_asof_date": cap_record.asof_date if cap_record else None,
            "quote_raw_line": quote_raw_line,
            "quote_fields": quote_fields,
            "toplist_seen": symbol in toplist_set,
            "denominator": denominator_to_dict(config.screener),
        }
        accepted, failures = candidate_passes_denominator(row, config.screener)
        row["filter_status"] = "PASS" if accepted else "FAIL"
        row["failure_reasons"] = failures
        reasons = ",".join(failures) if failures else "pass"
        print(
            f"[screener {index:03d}/{total:03d}] {row['filter_status']} {symbol} "
            f"price={_value_text(price)} volume={_value_text(volume)} "
            f"market_cap={_value_text(row.get('market_cap_usd'))} session={session} "
            f"reasons={reasons}",
            flush=True,
        )
        append_jsonl(paths["candidate_registry"], row)
        append_jsonl(screener_paths["candidates_jsonl"], row)
        rows.append(row)
        state["evaluated_candidates"] = len(rows)
        state["passed_candidates"] = sum(1 for item in rows if item["filter_status"] == "PASS")
        _write_heartbeat(paths, run_id, "live", "screener_lv1", state, active_symbol=symbol)

    _write_candidates_csv(screener_paths["candidates_csv"], rows)
    atomic_write_json(
        screener_paths["manifest"],
        {
            "schema_version": "das_cmdapi_screener_manifest_v0_1",
            "created_at_utc": utc_now(),
            "run_id": run_id,
            "data_root": str(config.data_root),
            "screener_root": str(screener_paths["root"]),
            "denominator": denominator_to_dict(config.screener),
            "toplist_symbols_seen": len(toplist_symbols),
            "candidate_symbol_source": config.screener_symbol_source,
            "candidate_source_counts": {
                "seed_symbols": len(config.symbols),
                "toplist_symbols": len(toplist_symbols),
                "market_cap_reference_symbols_eligible": len(_reference_symbol_list(config, market_caps)),
                "selected_symbols": len(rows),
                "max_screener_symbols": config.max_screener_symbols,
                "allow_large_screener_scan": config.allow_large_screener_scan,
                "screener_reference_active_only": config.screener_reference_active_only,
            },
            "evaluated_symbols": len(rows),
            "passed_candidates": sum(1 for item in rows if item["filter_status"] == "PASS"),
            "market_cap_reference": {
                "path": str(market_caps.path) if market_caps.path else None,
                "records": len(market_caps.records),
                "error": market_caps.error,
            },
            "output_files": {key: str(value) for key, value in screener_paths.items() if key != "root"},
        },
    )
    return rows


def _append_capture_registry(paths: dict[str, Path], row: dict[str, Any], event_type: str, status: str) -> None:
    payload = dict(row)
    payload["event_type"] = event_type
    payload["capture_status"] = status
    payload["observed_at_utc"] = utc_now()
    append_jsonl(paths["candidate_registry"], payload)


def _account_query_command(query: str) -> str:
    normalized = "".join(str(query).split()).upper()
    commands = {
        "BP": "GET BP",
        "ACCOUNTINFO": "GET AccountInfo",
        "POSITIONS": "GET POSITIONS",
        "ORDERS": "GET ORDERS",
        "TRADES": "GET TRADES",
        "ROUTESTATUS": "GET ROUTESTATUS",
        "LOCATES": "GET LOCATES",
        "INTMSGS": "GET INTMSGS",
    }
    return commands.get(normalized, "GET " + str(query).strip())


def _run_account_queries(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
    *,
    stage: str,
) -> None:
    if not config.account_queries_enabled:
        return
    print(f"[account] running {len(config.account_queries)} read-only account queries ({stage}).", flush=True)
    for query in config.account_queries:
        command = _account_query_command(query)
        print(f"[account] query {command}", flush=True)
        _send_and_record(client, paths, run_id, "live", config, state, command, wait_seconds=config.query_wait_seconds, stage=stage)


def _run_global_locate_queries(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
    *,
    stage: str,
) -> None:
    if not config.locate_queries_enabled:
        return
    for command in ("SLReuseQuery ALL", "SLRouteMinCharge ALLROUTE"):
        print(f"[locate] query {command}", flush=True)
        _send_and_record(client, paths, run_id, "live", config, state, command, wait_seconds=config.locate_query_wait_seconds, stage=stage)


def _run_symbol_locate_queries(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
    *,
    account: str,
    symbol: str,
) -> None:
    if not config.locate_queries_enabled:
        return
    commands = [f"SLAvailQuery {account} {symbol}", f"SLReuseQuery {symbol}"]
    for route in config.locate_price_routes:
        route_text = str(route).strip().upper()
        if route_text:
            commands.append(f"SLPRICEINQUIRE {symbol} {config.locate_price_shares} {route_text}")
    for command in commands:
        print(f"[locate {symbol}] query {redacted_command(command)}", flush=True)
        _send_and_record(
            client,
            paths,
            run_id,
            "live",
            config,
            state,
            command,
            wait_seconds=config.locate_query_wait_seconds,
            stage="candidate_locate_query",
            active_symbol=symbol,
        )


def _subscribe_candidate_bundle(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
    candidate: dict[str, Any],
    *,
    account: str,
) -> None:
    symbol = str(candidate["symbol"]).upper()
    ranges = _chart_ranges(config)
    active: set[tuple[str, str]] = state["active_subscriptions"]
    print(f"[capture {symbol}] starting full data bundle.", flush=True)
    _append_capture_registry(paths, candidate, "capture_started", "started")

    if _channel_enabled(config, "Lv1"):
        print(f"[capture {symbol}] subscribe Lv1", flush=True)
        _send_and_record(client, paths, run_id, "live", config, state, f"SB {symbol} Lv1", wait_seconds=config.full_capture_wait_seconds, stage="candidate_subscribe", active_symbol=symbol)
        active.add((symbol, "Lv1"))
        _write_subscription_state(paths, run_id, "live", active)

    for query in config.symbol_queries:
        q = query.upper()
        if q == "SHORTINFO":
            command = f"GET SHORTINFO {symbol}"
        elif q == "LDLU":
            command = f"GET LDLU {symbol}"
        elif q == "SYMSTATUS":
            command = f"GET SymStatus {symbol}"
        else:
            continue
        print(f"[capture {symbol}] query {q}", flush=True)
        _send_and_record(client, paths, run_id, "live", config, state, command, wait_seconds=config.query_wait_seconds, stage="candidate_static_query", active_symbol=symbol)

    _run_symbol_locate_queries(client, paths, run_id, config, state, account=account, symbol=symbol)

    if _channel_enabled(config, "tms"):
        print(f"[capture {symbol}] subscribe tms", flush=True)
        _send_and_record(client, paths, run_id, "live", config, state, f"SB {symbol} tms", wait_seconds=config.full_capture_wait_seconds, stage="candidate_subscribe", active_symbol=symbol)
        active.add((symbol, "tms"))
        _write_subscription_state(paths, run_id, "live", active)

    if _channel_enabled(config, "Lv2"):
        print(f"[capture {symbol}] subscribe Lv2", flush=True)
        _send_and_record(client, paths, run_id, "live", config, state, f"SB {symbol} Lv2", wait_seconds=config.full_capture_wait_seconds, stage="candidate_subscribe", active_symbol=symbol)
        active.add((symbol, "Lv2"))
        _write_subscription_state(paths, run_id, "live", active)

    if _channel_enabled(config, "DAYCHART"):
        print(f"[capture {symbol}] query DAYCHART {ranges['day_start']}..{ranges['day_end']}", flush=True)
        command = f"SB {symbol} DAYCHART {ranges['day_start']} {ranges['day_end']}"
        _send_and_record(client, paths, run_id, "live", config, state, command, wait_seconds=config.full_capture_wait_seconds, stage="candidate_chart_query", active_symbol=symbol)
        _send_and_record(client, paths, run_id, "live", config, state, f"UNSB {symbol} DAYCHART", wait_seconds=config.query_wait_seconds, stage="candidate_chart_query", active_symbol=symbol)

    if _channel_enabled(config, "MINCHART"):
        print(f"[capture {symbol}] query MINCHART {ranges['min_start']}..{ranges['min_end']} 1m", flush=True)
        command = f"SB {symbol} MINCHART {ranges['min_start']} {ranges['min_end']} 1"
        _send_and_record(client, paths, run_id, "live", config, state, command, wait_seconds=config.full_capture_wait_seconds, stage="candidate_chart_query", active_symbol=symbol)
        _send_and_record(client, paths, run_id, "live", config, state, f"UNSB {symbol} MINCHART", wait_seconds=config.query_wait_seconds, stage="candidate_chart_query", active_symbol=symbol)

    _append_capture_registry(paths, candidate, "capture_subscribed", "streaming")
    print(f"[capture {symbol}] bundle subscribed.", flush=True)


def _stream_active_subscriptions(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
) -> str:
    active = state["active_subscriptions"]
    if not active:
        return "no_active_subscriptions"
    if config.capture_seconds is None:
        print("Live capture active. Press Ctrl+C to stop, unsubscribe, and write final_summary.json.", flush=True)
        deadline = None
    else:
        print(f"Live capture active for {config.capture_seconds} seconds. Press Ctrl+C to stop earlier.", flush=True)
        deadline = time.monotonic() + max(0, config.capture_seconds)

    try:
        while True:
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return "duration_complete"
                wait_seconds = min(config.stream_poll_seconds, remaining)
            else:
                wait_seconds = config.stream_poll_seconds
            response = client.read_available(wait_seconds=wait_seconds, max_bytes=config.max_response_bytes)
            if response:
                _record_response(
                    paths,
                    run_id,
                    "live",
                    state,
                    command="SUBSCRIPTION_STREAM",
                    response=response,
                    wait_seconds=wait_seconds,
                    stage="streaming",
                    sent_to_socket=False,
                    allowed=True,
                    blocked=False,
                    reason="active_subscription_stream_read",
                    write_empty_event=False,
                )
                print(
                    f"[stream] {len(split_response_lines(response))} lines, "
                    f"{len(response.encode('utf-8'))} bytes; active_subscriptions={len(active)}",
                    flush=True,
                )
            else:
                print(f"[stream] idle heartbeat; active_subscriptions={len(active)}", flush=True)
                _write_heartbeat(paths, run_id, "live", "streaming", state)
    except KeyboardInterrupt:
        append_log(paths["capture_log"], "operator requested stop during streaming")
        return "operator_stop"


def _unsubscribe_all(
    client: DasCmdApiClient,
    paths: dict[str, Path],
    run_id: str,
    config: CaptureConfig,
    state: dict[str, Any],
) -> None:
    active: set[tuple[str, str]] = state["active_subscriptions"]
    for symbol, channel in list(sorted(active)):
        try:
            print(f"[shutdown] unsubscribe {symbol} {channel}", flush=True)
            _send_and_record(
                client,
                paths,
                run_id,
                "live",
                config,
                state,
                f"UNSB {symbol} {channel}",
                wait_seconds=config.query_wait_seconds,
                stage="shutdown_unsubscribe",
                active_symbol=symbol,
            )
        except Exception as exc:  # pragma: no cover - defensive socket cleanup
            append_log(paths["capture_log"], f"warning unsubscribe {symbol} {channel} failed: {exc}")
        finally:
            active.discard((symbol, channel))
            _write_subscription_state(paths, run_id, "live", active)


def _write_final_summary(
    paths: dict[str, Path],
    run_id: str,
    mode: str,
    run_root: Path,
    screener_paths: dict[str, Path] | None,
    config: CaptureConfig,
    state: dict[str, Any],
    status: str,
    notes: list[str],
) -> None:
    atomic_write_json(
        paths["final_summary"],
        {
            "schema_version": "das_cmdapi_final_summary_v0_1",
            "created_at_utc": utc_now(),
            "run_id": run_id,
            "status": status,
            "mode": mode,
            "run_root": str(run_root),
            "screener_root": str(screener_paths["root"]) if screener_paths else None,
            "data_root": str(config.data_root),
            "socket_opened": state.get("socket_opened", False),
            "das_commands_sent": state.get("das_commands_sent", 0),
            "command_transcript_lines": state.get("command_transcript_lines", 0),
            "event_lines": state.get("event_lines", 0),
            "response_bytes": state.get("response_bytes", 0),
            "evaluated_candidates": state.get("evaluated_candidates", 0),
            "passed_candidates": state.get("passed_candidates", 0),
            "active_subscriptions_at_close": _active_subscription_rows(state.get("active_subscriptions", set())),
            "last_error": state.get("last_error"),
            "output_files": {key: str(value) for key, value in paths.items()},
            "notes": notes,
        },
    )


def run_dry_run(config: CaptureConfig, run_id: str) -> Path:
    run_root = raw_run_root(config.data_root, run_id)
    paths = ensure_run_files(run_root)
    planned_commands = build_command_plan(config)
    validation_rows = validate_plan(config, planned_commands)
    failures = [row for row in validation_rows if not row["allowed"]]
    started_at = utc_now()

    pre_manifest = {
        "schema_version": "das_cmdapi_pre_manifest_v0_1",
        "created_at_utc": started_at,
        "run_id": run_id,
        "mode": "dry_run",
        "data_root": str(config.data_root),
        "run_root": str(run_root),
        "login_mode": config.login_mode,
        "socket_login_enabled": config.socket_login_enabled,
        "locate_queries_enabled": config.locate_queries_enabled,
        "config": config_to_dict(config),
        "blocked_prefixes": list(BLOCKED_PREFIXES),
        "planned_command_count": len(planned_commands),
        "screener_initial_denominator": denominator_to_dict(config.screener),
    }
    atomic_write_json(paths["pre_manifest"], pre_manifest)

    pid_manifest = {
        "schema_version": "das_cmdapi_pid_manifest_v0_1",
        "created_at_utc": utc_now(),
        "run_id": run_id,
        "pid": os.getpid(),
        "cwd": str(Path.cwd()),
        "python": sys.executable,
        "run_root": str(run_root),
        "output_files": {key: str(value) for key, value in paths.items()},
    }
    atomic_write_json(paths["pid_manifest"], pid_manifest)

    atomic_write_json(
        paths["subscription_state"],
        {
            "schema_version": "das_cmdapi_subscription_state_v0_1",
            "updated_at_utc": utc_now(),
            "run_id": run_id,
            "mode": "dry_run",
            "active_subscriptions": [],
            "planned_symbols": list(config.symbols),
            "planned_channels": list(config.channels),
        },
    )

    for row in validation_rows:
        append_jsonl(
            paths["command_transcript"],
            {
                "schema_version": "das_cmdapi_command_transcript_v0_1",
                "observed_at_utc": utc_now(),
                "run_id": run_id,
                "mode": "dry_run",
                "command": row["command"],
                "allowed": row["allowed"],
                "blocked": row["blocked"],
                "reason": row["reason"],
                "sent_to_socket": False,
                "response": None,
            },
        )

    append_jsonl(
        paths["events"],
        {
            "schema_version": "das_cmdapi_event_v0_1",
            "observed_at_utc": utc_now(),
            "run_id": run_id,
            "mode": "dry_run",
            "event_type": "dry_run_no_socket",
            "raw_line": None,
            "message": "No DAS socket opened; command plan and run files validated only.",
        },
    )
    append_log(paths["capture_log"], "dry_run started")
    append_log(paths["capture_log"], f"planned_commands={len(planned_commands)} failures={len(failures)}")

    heartbeat = {
        "schema_version": "das_cmdapi_heartbeat_v0_1",
        "updated_at_utc": utc_now(),
        "run_id": run_id,
        "stage": "dry_run_complete" if not failures else "dry_run_validation_failed",
        "mode": "dry_run",
        "planned_command_count": len(planned_commands),
        "validation_failures": len(failures),
        "command_transcript_lines": len(validation_rows),
        "event_lines": 1,
        "last_error": None if not failures else "command_plan_contains_disallowed_commands",
    }
    atomic_write_json(paths["heartbeat"], heartbeat)

    summary = {
        "schema_version": "das_cmdapi_final_summary_v0_1",
        "created_at_utc": utc_now(),
        "run_id": run_id,
        "status": "PASS" if not failures else "FAIL",
        "mode": "dry_run",
        "run_root": str(run_root),
        "planned_command_count": len(planned_commands),
        "validation_failures": failures,
        "socket_opened": False,
        "das_commands_sent": 0,
        "notes": [
            "Dry-run validates config, command allowlist/blocklist, and required run files only.",
            "Real DAS capture is implemented by running this command without --dry-run.",
        ],
    }
    atomic_write_json(paths["final_summary"], summary)
    append_log(paths["capture_log"], "dry_run complete")
    if failures:
        raise SystemExit(f"Dry-run validation failed with {len(failures)} disallowed planned commands. Run root: {run_root}")
    return run_root


def run_live_capture(config: CaptureConfig, run_id: str, download_decision: bool | None) -> Path:
    config = replace(config, socket_login_enabled=True, login_mode="terminal_prompt_socket_login")
    username, password, account = _prompt_credentials()
    run_root = raw_run_root(config.data_root, run_id)
    print(f"Run root: {run_root}", flush=True)
    print(f"Data root: {config.data_root}", flush=True)
    screener_cap_note = (
        "large scan explicitly allowed"
        if config.allow_large_screener_scan
        else f"hard cap {MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT}"
    )
    if config.skip_screener:
        print(
            "Candidate-file mode: screener is skipped; TSIS trusts the supplied candidate file "
            "as the already-filtered ticker source.",
            flush=True,
        )
        print(
            f"Candidate file: {config.candidate_file_path}; "
            f"filter_status={config.candidate_file_filter_status or 'none'}.",
            flush=True,
        )
    else:
        print(
            f"Screener contract: max_screener_symbols={config.max_screener_symbols} "
            f"({screener_cap_note}).",
            flush=True,
        )
        print(
            "Initial filter: "
            f"sessions={','.join(config.screener.sessions)}; "
            f"market_cap<{config.screener.market_cap_usd_lt}; "
            f"price={config.screener.price_usd_min}-{config.screener.price_usd_max}; "
            f"volume>={config.screener.min_volume_shares}.",
            flush=True,
        )
    paths = ensure_run_files(run_root)
    screener_paths: dict[str, Path] | None = None
    market_caps = load_market_cap_reference(config.market_cap_reference_path)
    if market_caps.error:
        print(f"Market cap reference warning: {market_caps.error}", flush=True)
    else:
        print(f"Market cap reference loaded: {len(market_caps.records)} records.", flush=True)
    state: dict[str, Any] = {
        "das_commands_sent": 0,
        "command_transcript_lines": 0,
        "event_lines": 0,
        "response_bytes": 0,
        "evaluated_candidates": 0,
        "passed_candidates": 0,
        "active_subscriptions": set(),
        "socket_opened": False,
        "last_error": None,
    }
    notes: list[str] = []
    final_status = "FAIL"
    client = DasCmdApiClient(
        host=config.host,
        port=config.port,
        socket_login_enabled=config.socket_login_enabled,
        locate_queries_enabled=config.locate_queries_enabled,
    )

    atomic_write_json(
        paths["pre_manifest"],
        {
            "schema_version": "das_cmdapi_pre_manifest_v0_1",
            "created_at_utc": utc_now(),
            "run_id": run_id,
            "mode": "live",
            "data_root": str(config.data_root),
            "run_root": str(run_root),
            "credential_handling": {
                "terminal_prompt": True,
                "credentials_written_to_disk": False,
                "login_command_redacted_in_transcript": True,
            },
            "config": config_to_dict(config),
            "blocked_prefixes": list(BLOCKED_PREFIXES),
            "account_queries_enabled": config.account_queries_enabled,
            "account_queries": list(config.account_queries),
            "locate_readonly_queries_enabled": config.locate_queries_enabled,
            "locate_readonly_query_plan": {
                "global_queries": ["SLReuseQuery ALL", "SLRouteMinCharge ALLROUTE"],
                "per_symbol_queries": ["SLAvailQuery <account> <symbol>", "SLReuseQuery <symbol>", "SLPRICEINQUIRE <symbol> <shares> <route>"],
                "locate_price_shares": config.locate_price_shares,
                "locate_price_routes": list(config.locate_price_routes),
            },
            "candidate_symbol_source": config.screener_symbol_source,
            "candidate_file_path": str(config.candidate_file_path) if config.candidate_file_path else None,
            "candidate_file_filter_status": config.candidate_file_filter_status,
            "skip_screener": config.skip_screener,
            "allow_large_screener_scan": config.allow_large_screener_scan,
            "screener_reference_active_only": config.screener_reference_active_only,
            "screener_initial_denominator": denominator_to_dict(config.screener),
            "market_cap_reference": {
                "path": str(market_caps.path) if market_caps.path else None,
                "records": len(market_caps.records),
                "error": market_caps.error,
            },
        },
    )
    atomic_write_json(
        paths["pid_manifest"],
        {
            "schema_version": "das_cmdapi_pid_manifest_v0_1",
            "created_at_utc": utc_now(),
            "run_id": run_id,
            "pid": os.getpid(),
            "cwd": str(Path.cwd()),
            "python": sys.executable,
            "run_root": str(run_root),
            "output_files": {key: str(value) for key, value in paths.items()},
        },
    )
    _write_subscription_state(paths, run_id, "live", state["active_subscriptions"])
    _write_heartbeat(paths, run_id, "live", "starting", state)
    append_log(paths["capture_log"], "live capture starting")

    try:
        print(f"Connecting to DAS CMD API at {config.host}:{config.port} ...", flush=True)
        client.connect()
        print("Socket connected.", flush=True)
        state["socket_opened"] = True
        _write_heartbeat(paths, run_id, "live", "socket_connected", state)

        login_command = f"LOGIN {username} {password} {account} 0"
        print("Sending LOGIN through socket; transcript will redact credentials.", flush=True)
        _login_response, login_lines = _send_and_record(
            client,
            paths,
            run_id,
            "live",
            config,
            state,
            login_command,
            wait_seconds=config.query_wait_seconds,
            stage="login",
        )
        if _login_confirmed(login_lines):
            print("LOGIN: confirmed by DAS.", flush=True)
        if not _login_confirmed(login_lines):
            notes.append("DAS login was not confirmed by the API response.")
            login_text = "\n".join(login_lines).upper()
            invalid_account_or_password = "INVALID ACCOUNT" in login_text or "INVALID PASSWORD" in login_text
            if invalid_account_or_password:
                notes.append("DAS login response included invalid account/password; locate/account-state queries are not reliable.")
                print(
                    "LOGIN error: DAS returned invalid account/password. "
                    "This run cannot certify account-state or locate prices.",
                    flush=True,
                )
                if (config.account_queries_enabled or config.locate_queries_enabled) and not config.allow_invalid_login_continue:
                    final_status = "ABORTED_INVALID_LOGIN_FOR_ACCOUNT_LOCATE"
                    return run_root
            if not _yes_answer(input("DAS did not confirm login. Continue only if already logged in and account/locate queries should work? [s/N]: ")):
                final_status = "ABORTED_LOGIN_NOT_CONFIRMED"
                return run_root

        for command in ("ECHO OFF", "CLIENT", "ReturnFullLv1 YES"):
            print(f"Session setup: {command}", flush=True)
            _send_and_record(client, paths, run_id, "live", config, state, command, wait_seconds=config.query_wait_seconds, stage="session_setup")

        _run_account_queries(client, paths, run_id, config, state, stage="account_query_initial")
        _run_global_locate_queries(client, paths, run_id, config, state, stage="locate_global_initial")

        screener_paths = _ensure_screener_files(config.data_root, run_id)
        if config.skip_screener:
            rows = _trusted_candidate_rows_from_file(config, run_id, market_caps)
            _write_trusted_candidate_outputs(paths, screener_paths, run_id, config, market_caps, rows)
            state["evaluated_candidates"] = len(rows)
            state["passed_candidates"] = len(rows)
            _write_heartbeat(paths, run_id, "live", "trusted_candidate_file_loaded", state)
            passed = rows
            print(
                f"Screener skipped: loaded {len(passed)} trusted PASS candidates "
                f"from {config.candidate_file_path}.",
                flush=True,
            )
        else:
            toplist_symbols = _collect_toplist_symbols(client, paths, run_id, config, state)
            reference_symbols = _reference_symbol_list(config, market_caps)
            symbols = _candidate_symbol_list(config, toplist_symbols, market_caps)
            print(
                f"Candidate universe: {len(symbols)} symbols "
                f"(seed={len(config.symbols)}, toplist={len(toplist_symbols)}, "
                f"reference={len(reference_symbols)}, cap={config.max_screener_symbols}, "
                f"source={config.screener_symbol_source}).",
                flush=True,
            )
            rows = _evaluate_screener(client, paths, screener_paths, run_id, config, state, market_caps, symbols, toplist_symbols)
            passed = [row for row in rows if row.get("filter_status") == "PASS"]
            print(f"Screener evaluated {len(rows)} symbols; PASS candidates: {len(passed)}", flush=True)
        for row in passed[:50]:
            print(
                f"PASS {row['symbol']} price={row.get('price_usd')} volume={row.get('volume_shares')} "
                f"market_cap={row.get('market_cap_usd')} session={row.get('session')}",
                flush=True,
            )
        if len(passed) > 50:
            print(f"... {len(passed) - 50} additional PASS candidates omitted from terminal output.", flush=True)

        if not passed:
            _run_account_queries(client, paths, run_id, config, state, stage="account_query_no_candidates")
            _run_global_locate_queries(client, paths, run_id, config, state, stage="locate_global_no_candidates")
            notes.append("No PASS candidates; full data download was not started.")
            final_status = "PASS_NO_CANDIDATES"
            return run_root

        if download_decision is None:
            download_decision = _prompt_download()
        if not download_decision:
            notes.append("Operator declined full data download after screener.")
            final_status = "PASS_SCREEN_ONLY"
            return run_root

        _run_account_queries(client, paths, run_id, config, state, stage="account_query_after_screener")
        _run_global_locate_queries(client, paths, run_id, config, state, stage="locate_global_after_screener")
        for candidate in passed:
            _subscribe_candidate_bundle(client, paths, run_id, config, state, candidate, account=account)
        stream_result = _stream_active_subscriptions(client, paths, run_id, config, state)
        notes.append(f"stream_result={stream_result}")
        _run_account_queries(client, paths, run_id, config, state, stage="account_query_after_stream")
        _run_global_locate_queries(client, paths, run_id, config, state, stage="locate_global_after_stream")
        final_status = "PASS_OPERATOR_STOP" if stream_result == "operator_stop" else "PASS"
        return run_root

    except Exception as exc:
        state["last_error"] = repr(exc)
        append_log(paths["capture_log"], f"error {repr(exc)}")
        final_status = "FAIL"
        raise
    finally:
        if client.connected:
            try:
                _unsubscribe_all(client, paths, run_id, config, state)
            finally:
                try:
                    _send_and_record(client, paths, run_id, "live", config, state, "QUIT", wait_seconds=config.query_wait_seconds, stage="shutdown")
                except Exception as exc:  # pragma: no cover - defensive shutdown path
                    append_log(paths["capture_log"], f"warning QUIT failed: {exc}")
                client.close()
        _write_heartbeat(paths, run_id, "live", "closed", state)
        _write_final_summary(paths, run_id, "live", run_root, screener_paths, config, state, final_status, notes)
        append_log(paths["capture_log"], f"live capture closed status={final_status}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TSIS DAS CMD API capture v0")
    parser.add_argument("--config", type=Path, help="JSON config path. Defaults are used when omitted.")
    parser.add_argument("--data-root", type=Path, help="Override DAS live data root. Default: E:/TSIS/data_DAS_live")
    parser.add_argument("--run-id", help="Run id. Defaults to timestamped id.")
    parser.add_argument("--symbol", action="append", help="Seed symbol for screener. Can be repeated.")
    parser.add_argument("--candidate-file", type=Path, help="CSV/JSONL/TXT produced by the TSIS screener. Used to load ticker symbols.")
    parser.add_argument("--candidate-file-status", default="PASS", help="Filter status to load from candidate CSV/JSONL. Default: PASS. Use empty string to disable filtering.")
    parser.add_argument("--skip-screener", action="store_true", help="Trust --candidate-file/--symbol inputs as already filtered PASS candidates and download read-only DAS data directly.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and write run files without connecting to DAS.")
    parser.add_argument("--capture-seconds", type=int, help="Stop live stream automatically after N seconds. Omit to run until Ctrl+C.")
    parser.add_argument("--max-screener-symbols", type=int, help="Maximum symbols evaluated by the DAS screener.")
    parser.add_argument("--scan-tsis-universe", action="store_true", help="Add governed TSIS market-cap reference symbols to the screener universe when TOPLIST is empty or incomplete.")
    parser.add_argument("--include-inactive-reference-symbols", action="store_true", help="Include inactive historical TSIS reference symbols in the screener universe. Default scans active reference symbols only.")
    parser.add_argument("--allow-large-scan", action="store_true", help="Allow --max-screener-symbols above the default TSIS contract cap of 100; execution/order commands remain blocked.")
    parser.add_argument("--screener-wait-seconds", type=float, help="Wait after each screener Lv1 subscription before evaluating quote fields.")
    parser.add_argument("--query-wait-seconds", type=float, help="Wait after read-only query/unsubscribe commands.")
    parser.add_argument("--locate-query-wait-seconds", type=float, help="Wait after read-only locate inquiry commands. Default: 3 seconds.")
    parser.add_argument("--toplist-wait-seconds", type=float, help="Wait for DAS TOPLIST lines.")
    parser.add_argument("--full-capture-wait-seconds", type=float, help="Wait after each full candidate subscription bundle.")
    parser.add_argument("--max-readonly", action="store_true", help="Run every implemented read-only DAS query, including account state and locate inquiry commands. Execution/order commands remain blocked.")
    parser.add_argument("--account-queries", action="store_true", help="Execute configured GET account-state queries in live capture.")
    parser.add_argument("--allow-invalid-login-continue", action="store_true", help="Permit continuation after DAS invalid account/password. Not recommended for account-state or locate capture.")
    parser.add_argument("--locate-queries", action="store_true", help="Execute read-only locate inquiry commands in live capture.")
    parser.add_argument("--locate-shares", type=int, help="Share quantity for SLPRICEINQUIRE. Default from config is 100.")
    parser.add_argument("--locate-route", action="append", help="Route for SLPRICEINQUIRE. Can be repeated. Defaults from config.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--yes-download", action="store_true", help="After screener, start full data capture without prompting.")
    group.add_argument("--no-download", action="store_true", help="After screener, write screener outputs and skip full data capture.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    if args.data_root is not None:
        config = replace(config, data_root=args.data_root)
    if args.symbol:
        config = replace(config, symbols=tuple(s.upper() for s in args.symbol))
    if args.candidate_file is not None:
        candidate_status = args.candidate_file_status.strip() or None
        candidate_symbols = _candidate_symbols_from_file(args.candidate_file, candidate_status)
        if not candidate_symbols:
            raise SystemExit(f"No candidate symbols loaded from {args.candidate_file}")
        config = replace(
            config,
            symbols=tuple(candidate_symbols),
            candidate_file_path=args.candidate_file,
            candidate_file_filter_status=candidate_status,
        )
    if args.skip_screener:
        config = replace(config, skip_screener=True)
    if args.capture_seconds is not None:
        config = replace(config, capture_seconds=args.capture_seconds)
    if args.allow_large_scan:
        config = replace(config, allow_large_screener_scan=True)
    if args.scan_tsis_universe:
        config = replace(config, screener_symbol_source="seed_toplist_market_cap_reference")
    if args.include_inactive_reference_symbols:
        config = replace(config, screener_reference_active_only=False)
    if args.screener_wait_seconds is not None:
        config = replace(config, screener_wait_seconds=max(0.05, args.screener_wait_seconds))
    if args.query_wait_seconds is not None:
        config = replace(config, query_wait_seconds=max(0.05, args.query_wait_seconds))
    if args.locate_query_wait_seconds is not None:
        config = replace(config, locate_query_wait_seconds=max(0.05, args.locate_query_wait_seconds))
    if args.toplist_wait_seconds is not None:
        config = replace(config, toplist_wait_seconds=max(0.05, args.toplist_wait_seconds))
    if args.full_capture_wait_seconds is not None:
        config = replace(config, full_capture_wait_seconds=max(0.05, args.full_capture_wait_seconds))
    if args.max_readonly:
        config = replace(config, account_queries_enabled=True, locate_queries_enabled=True)
    if args.account_queries:
        config = replace(config, account_queries_enabled=True)
    if args.allow_invalid_login_continue:
        config = replace(config, allow_invalid_login_continue=True)
    if args.locate_queries:
        config = replace(config, locate_queries_enabled=True)
    if args.locate_shares is not None:
        config = replace(config, locate_price_shares=max(1, args.locate_shares))
    if args.locate_route:
        config = replace(config, locate_price_routes=tuple(route.upper() for route in args.locate_route))
    if args.max_screener_symbols is not None:
        requested_limit = max(1, args.max_screener_symbols)
        if requested_limit > MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT and not config.allow_large_screener_scan:
            print(
                f"Requested --max-screener-symbols={requested_limit}; capped to TSIS DAS contract limit "
                f"{MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT}. Use --allow-large-scan for an explicit TSIS universe scan.",
                file=sys.stderr,
                flush=True,
            )
        config = replace(
            config,
            max_screener_symbols=requested_limit if config.allow_large_screener_scan else min(requested_limit, MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT),
        )

    run_id = args.run_id or make_run_id("dry_run" if args.dry_run else "live")
    if args.dry_run:
        run_root = run_dry_run(config, run_id)
        print(f"DAS CMD API dry-run PASS: {run_root}")
        return 0

    download_decision = True if args.yes_download else False if args.no_download else None
    try:
        run_root = run_live_capture(config, run_id, download_decision)
    except Exception as exc:
        print(f"DAS CMD API capture failed: {exc}", file=sys.stderr)
        return 1
    print(f"DAS CMD API capture closed: {run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
