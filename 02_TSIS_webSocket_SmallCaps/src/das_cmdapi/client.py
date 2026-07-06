"""Minimal DAS CMD API TCP client shell.

The real socket path is intentionally not wired into capture.py yet. v0 dry-run
uses this module only as the future boundary for read-only sends.
"""

from __future__ import annotations

import socket
from dataclasses import dataclass, field

from .allowlist import redacted_command, validate_command


@dataclass
class DasCmdApiClient:
    host: str = "127.0.0.1"
    port: int = 9800
    timeout_seconds: float = 2.0
    socket_login_enabled: bool = False
    locate_queries_enabled: bool = False
    _socket: socket.socket | None = field(default=None, init=False, repr=False)

    def connect(self) -> None:
        self._socket = socket.create_connection((self.host, self.port), timeout=self.timeout_seconds)

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def send_readonly(self, command: str) -> str:
        validation = validate_command(
            command,
            socket_login_enabled=self.socket_login_enabled,
            locate_queries_enabled=self.locate_queries_enabled,
        )
        if not validation.allowed:
            raise ValueError(f"Refusing DAS command {redacted_command(command)!r}: {validation.reason}")
        if self._socket is None:
            raise RuntimeError("DAS socket is not connected")
        payload = command.rstrip("\r\n") + "\r\n"
        self._socket.sendall(payload.encode("ascii"))
        return self._socket.recv(65536).decode("ascii", errors="replace")
