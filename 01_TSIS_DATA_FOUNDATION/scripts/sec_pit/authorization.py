"""Hash-bound authorization gate for SEC PIT primary-document acquisition."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from sec_pit.predownload_control import POLICY_ID


@dataclass(frozen=True)
class AuthorizationDecision:
    gate: str
    reason: str
    allowed_tickers: tuple[str, ...]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_download_authorization(
    authorization_path: Path,
    *,
    probe_manifest_path: Path,
    selection_plan_path: Path,
    technically_eligible_tickers: Iterable[str],
) -> AuthorizationDecision:
    if not authorization_path.is_file():
        return AuthorizationDecision("FAIL", "AUTHORIZATION_FILE_MISSING", ())
    payload = json.loads(authorization_path.read_text(encoding="utf-8-sig"))
    if payload.get("status") != "AUTHORIZED":
        return AuthorizationDecision("FAIL", "AUTHORIZATION_STATUS_NOT_AUTHORIZED", ())
    if payload.get("policy_id") != POLICY_ID:
        return AuthorizationDecision("FAIL", "AUTHORIZATION_POLICY_MISMATCH", ())
    if payload.get("probe_manifest_sha256") != file_sha256(probe_manifest_path):
        return AuthorizationDecision("FAIL", "PROBE_MANIFEST_HASH_MISMATCH", ())
    if payload.get("selection_plan_sha256") != file_sha256(selection_plan_path):
        return AuthorizationDecision("FAIL", "SELECTION_PLAN_HASH_MISMATCH", ())
    allowed = tuple(sorted(set(payload.get("allowed_tickers") or [])))
    eligible = set(technically_eligible_tickers)
    if not allowed or not set(allowed).issubset(eligible):
        return AuthorizationDecision("FAIL", "AUTHORIZED_SCOPE_EXCEEDS_TECHNICAL_GATE", allowed)
    return AuthorizationDecision("PASS", "HASH_BOUND_SCOPE_AUTHORIZED", allowed)
