"""DAS CMD API TCP client boundary for read-only capture."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass, field

from .allowlist import redacted_command, validate_command


@dataclass
class DasCmdApiClient:
    host: str = "127.0.0.1"
    port: int = 9800
    timeout_seconds: float = 2.0
    read_poll_seconds: float = 0.2
    socket_login_enabled: bool = False
    locate_queries_enabled: bool = False
    _socket: socket.socket | None = field(default=None, init=False, repr=False)

    def __enter__(self) -> "DasCmdApiClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    @property
    def connected(self) -> bool:
        return self._socket is not None

    def connect(self) -> None:
        self._socket = socket.create_connection((self.host, self.port), timeout=self.timeout_seconds)
        self._socket.settimeout(self.read_poll_seconds)

    def close(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def read_available(self, *, wait_seconds: float = 1.0, max_bytes: int = 5_000_000) -> str:
        if self._socket is None:
            raise RuntimeError("DAS socket is not connected")
        chunks: list[bytes] = []
        total = 0
        deadline = time.monotonic() + max(0.0, wait_seconds)
        while time.monotonic() < deadline:
            try:
                chunk = self._socket.recv(65536)
            except TimeoutError:
                continue
            except socket.timeout:
                continue
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total >= max_bytes:
                break
        return b"".join(chunks).decode("ascii", errors="replace")

    def send_readonly(self, command: str, *, wait_seconds: float = 1.0, max_bytes: int = 5_000_000) -> str:
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
        self._socket.sendall(payload.encode("ascii", errors="replace"))
        return self.read_available(wait_seconds=wait_seconds, max_bytes=max_bytes)