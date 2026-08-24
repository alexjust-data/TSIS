# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "sec_pit"))

from run_massive_sec_acquisition import build_chain_plan, load_target_groups
from sec_pit.massive_sec_authorization import validate_frozen_target
from sec_pit.massive_sec_models import (
    CONDITIONAL_ENDPOINT_IDS,
    DIRECT_ENDPOINT_IDS,
    ENDPOINT_SPECS,
)


def test_target_manifest_freezes_exact_4824_membership() -> None:
    target_manifest = ROOT / "configs" / "massive_sec_target_manifest_v0_1.json"
    target = validate_frozen_target(target_manifest)

    assert target.row_count == 4_824
    assert target.unique_ticker_count == 4_824
    assert target.unique_cik_count == 4_288


def test_probe_is_first_250_cases_and_deduplicates_only_request_ciks() -> None:
    target_manifest = ROOT / "configs" / "massive_sec_target_manifest_v0_1.json"
    target = validate_frozen_target(target_manifest)
    groups, case_count = load_target_groups(target, execution_mode="PROBE")

    assert case_count == 250
    assert 1 <= len(groups) <= 250
    assert sum(len(group.tickers) for group in groups) == 250
    assert len({group.cik for group in groups}) == len(groups)


def test_direct_scope_excludes_both_conditional_endpoints() -> None:
    config = json.loads(
        (ROOT / "configs" / "massive_sec_acquisition_v0_1.json").read_text(
            encoding="utf-8"
        )
    )

    assert tuple(config["endpoint_ids"]) == DIRECT_ENDPOINT_IDS
    assert set(CONDITIONAL_ENDPOINT_IDS) == {"eight_k_text", "form_13f"}
    assert not set(config["endpoint_ids"]).intersection(CONDITIONAL_ENDPOINT_IDS)


def test_chain_plan_preserves_every_direct_endpoint() -> None:
    groups = [
        SimpleNamespace(cik="0000000001"),
        SimpleNamespace(cik="0000000002"),
    ]
    plan = build_chain_plan(DIRECT_ENDPOINT_IDS, groups)

    per_cik = sum(
        1
        for endpoint_id in DIRECT_ENDPOINT_IDS
        if ENDPOINT_SPECS[endpoint_id].query_strategy == "PER_ISSUER_CIK"
    )
    singleton = sum(
        1
        for endpoint_id in DIRECT_ENDPOINT_IDS
        if ENDPOINT_SPECS[endpoint_id].query_strategy == "SINGLETON"
    )
    assert len(plan) == per_cik * len(groups) + singleton
