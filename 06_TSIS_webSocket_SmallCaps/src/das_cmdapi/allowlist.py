"""Read-only command allowlist and execution blocklist for DAS CMD API v0."""

from __future__ import annotations

from dataclasses import dataclass

BLOCKED_PREFIXES: tuple[str, ...] = (
    "NEWORDER",
    "REPLACE",
    "CANCEL ALL",
    "CANCEL",
    "COMPLEXORDER",
    "SLNEWORDER",
    "SLCANCELORDER",
    "SLOFFEROPERATION",
)

ALLOWLIST_PREFIXES: tuple[str, ...] = (
    "ECHO OFF",
    "CLIENT",
    "QUIT",
    "RETURNFULLLV1",
    "SB ",
    "UNSB ",
    "GET BP",
    "GET ACCOUNTINFO",
    "GET POSITIONS",
    "GET ORDERS",
    "GET TRADES",
    "GET ROUTESTATUS",
    "GET LOCATES",
    "GET INTMSGS",
    "GET SHORTINFO ",
    "GET LDLU ",
    "GET SYMSTATUS ",
    "SLPRICEINQUIRE ",
    "SLAVAILQUERY ",
    "SLREUSEQUERY ",
    "SLROUTEMINCHARGE ",
)

SOCKET_LOGIN_PREFIX = "LOGIN "


@dataclass(frozen=True)
class CommandValidation:
    command: str
    allowed: bool
    blocked: bool
    reason: str


def normalize_command(command: str) -> str:
    return " ".join(command.strip().split()).upper()


def redacted_command(command: str) -> str:
    normalized = " ".join(command.strip().split())
    command_key = normalize_command(normalized)
    if command_key.startswith(SOCKET_LOGIN_PREFIX):
        parts = normalized.split()
        if len(parts) >= 4:
            return "LOGIN [REDACTED_USER] [REDACTED_PASSWORD] [REDACTED_ACCOUNT]" + (
                " " + " ".join(parts[4:]) if len(parts) > 4 else ""
            )
    if command_key.startswith("SLAVAILQUERY "):
        parts = normalized.split()
        if len(parts) >= 3:
            return f"{parts[0]} [REDACTED_ACCOUNT] " + " ".join(parts[2:])
    return normalized


def is_blocked_command(command: str) -> bool:
    normalized = normalize_command(command)
    return any(normalized == prefix or normalized.startswith(prefix + " ") for prefix in BLOCKED_PREFIXES)


def is_allowed_command(command: str, *, socket_login_enabled: bool = False, locate_queries_enabled: bool = False) -> bool:
    normalized = normalize_command(command)
    if not normalized:
        return False
    if is_blocked_command(normalized):
        return False
    if normalized.startswith(SOCKET_LOGIN_PREFIX):
        return socket_login_enabled
    if normalized.startswith(("SLPRICEINQUIRE ", "SLAVAILQUERY ", "SLREUSEQUERY ", "SLROUTEMINCHARGE ")):
        return locate_queries_enabled
    return any(normalized == prefix.rstrip() or normalized.startswith(prefix) for prefix in ALLOWLIST_PREFIXES)


def validate_command(
    command: str,
    *,
    socket_login_enabled: bool = False,
    locate_queries_enabled: bool = False,
) -> CommandValidation:
    normalized = normalize_command(command)
    if is_blocked_command(normalized):
        return CommandValidation(command=command, allowed=False, blocked=True, reason="hard_blocked_execution_command")
    if normalized.startswith(SOCKET_LOGIN_PREFIX) and not socket_login_enabled:
        return CommandValidation(command=command, allowed=False, blocked=False, reason="socket_login_disabled_by_contract")
    if normalized.startswith(("SLPRICEINQUIRE ", "SLAVAILQUERY ", "SLREUSEQUERY ", "SLROUTEMINCHARGE ")) and not locate_queries_enabled:
        return CommandValidation(command=command, allowed=False, blocked=False, reason="locate_queries_disabled_by_config")
    if is_allowed_command(command, socket_login_enabled=socket_login_enabled, locate_queries_enabled=locate_queries_enabled):
        return CommandValidation(command=command, allowed=True, blocked=False, reason="allowed_readonly_command")
    return CommandValidation(command=command, allowed=False, blocked=False, reason="not_in_readonly_allowlist")
