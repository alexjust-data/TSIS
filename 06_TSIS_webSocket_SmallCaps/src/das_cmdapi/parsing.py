"""Conservative parsers for DAS CMD API text lines.

Raw lines remain the source of truth. These helpers only extract fields needed
for the first screener and routing decisions.
"""

from __future__ import annotations

import re
from typing import Any

_SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")


def split_response_lines(response: str | None) -> list[str]:
    if not response:
        return []
    return [line.strip() for line in response.replace("\r", "\n").split("\n") if line.strip()]


def _coerce(value: str) -> str | int | float:
    try:
        if re.fullmatch(r"[-+]?\d+", value):
            return int(value)
        if re.fullmatch(r"[-+]?(\d+\.\d*|\d*\.\d+)", value):
            return float(value)
    except ValueError:
        pass
    return value


def parse_quote_line(line: str) -> dict[str, Any] | None:
    parts = line.strip().split()
    if len(parts) < 2 or parts[0] != "$Quote":
        return None
    fields: dict[str, Any] = {"symbol": parts[1].upper()}
    for token in parts[2:]:
        if ":" not in token:
            continue
        key, value = token.split(":", 1)
        fields[key] = _coerce(value)
    return fields


def extract_price_volume_from_quote(fields: dict[str, Any] | None) -> tuple[float | None, int | None, str | None]:
    if not fields:
        return None, None, None
    price: float | None = None
    price_source: str | None = None
    last = fields.get("L")
    if isinstance(last, (int, float)) and float(last) > 0:
        price = float(last)
        price_source = "das_lv1_L"
    else:
        bid = fields.get("B")
        ask = fields.get("A")
        if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and bid > 0 and ask > 0:
            price = (float(bid) + float(ask)) / 2.0
            price_source = "das_lv1_mid_B_A"
    volume: int | None = None
    raw_volume = fields.get("V")
    if isinstance(raw_volume, (int, float)) and int(raw_volume) >= 0:
        volume = int(raw_volume)
    return price, volume, price_source


def parse_toplist_symbols(response: str) -> list[str]:
    symbols: list[str] = []
    seen: set[str] = set()
    for line in split_response_lines(response):
        parts = line.split()
        if len(parts) < 3 or parts[0] != "$TopLst":
            continue
        for token in parts[2:]:
            symbol = token.strip().upper()
            if _SYMBOL_RE.match(symbol) and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols


def infer_data_family(command: str, line: str | None = None) -> str:
    normalized = " ".join(command.strip().split()).upper()
    if line:
        if line.startswith("$Quote"):
            return "lv1"
        if line.startswith("$T&S"):
            return "tms"
        if line.startswith("$Lv2"):
            return "lv2"
        if line.startswith("$TopLst"):
            return "toplist"
        if line.startswith("$SHORTINFO"):
            return "shortinfo"
        if line.startswith("$SymStatus"):
            return "symstatus"
        if line.startswith("$LDLU"):
            return "ldlu"
        if line.startswith("$Bar"):
            if " MINCHART " in normalized:
                return "minchart_1m"
            if " DAYCHART " in normalized:
                return "daychart"
            return "bar"
        if line.startswith("$AccountInfo") or line.startswith("BP ") or line.startswith("#POS"):
            return "account_state"
    if " TOPLIST" in normalized:
        return "toplist"
    if " LV1" in normalized or normalized.startswith("RETURNFULLLV1"):
        return "lv1"
    if " TMS" in normalized:
        return "tms"
    if " LV2" in normalized:
        return "lv2"
    if " SHORTINFO" in normalized:
        return "shortinfo"
    if " SYMSTATUS" in normalized:
        return "symstatus"
    if " LDLU" in normalized:
        return "ldlu"
    if " DAYCHART" in normalized:
        return "daychart"
    if " MINCHART" in normalized:
        return "minchart_1m"
    if normalized.startswith("LOGIN") or normalized in {"ECHO OFF", "CLIENT", "QUIT"}:
        return "session"
    if normalized.startswith("GET "):
        return "account_state"
    return "unknown"


def infer_symbol(command: str, line: str | None = None) -> str | None:
    if line:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] in {"$Quote", "$T&S", "$Lv2", "$SHORTINFO", "$SymStatus", "$LDLU", "$Bar"}:
            candidate = parts[1].upper()
            if _SYMBOL_RE.match(candidate):
                return candidate
    parts = command.strip().split()
    if not parts:
        return None
    upper = [p.upper() for p in parts]
    if upper[0] == "SB" and len(upper) >= 3 and upper[2] != "TOPLIST":
        return upper[1]
    if upper[0] == "UNSB" and len(upper) >= 3 and upper[2] != "TOPLIST":
        return upper[1]
    if upper[:2] == ["GET", "SHORTINFO"] and len(upper) >= 3:
        return upper[2]
    if upper[:2] == ["GET", "LDLU"] and len(upper) >= 3:
        return upper[2]
    if upper[:2] == ["GET", "SYMSTATUS"] and len(upper) >= 3:
        return upper[2]
    return None
