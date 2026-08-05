from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TSIS_ROOT = ROOT.parents[1]
ENGINE = TSIS_ROOT / "02_TSIS_BACKTEST_ENGINE"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    regs = {
        "decisions": load(ROOT / "04_DECISIONS/DECISION_LEDGER.json"),
        "policies": load(ROOT / "05_POLICIES/POLICY_REGISTER.json"),
        "traceability": load(ROOT / "06_TRACEABILITY/TRACEABILITY_MATRIX.json"),
        "exceptions": load(ROOT / "07_EXCEPTIONS/EXCEPTION_AND_WAIVER_REGISTER.json"),
        "gates": load(ROOT / "08_GATES_AND_REVIEWS/GATE_REGISTER.json"),
    }
    decisions = {item["decision_id"] for item in regs["decisions"]["entries"]}
    policies = {item["policy_id"]: item for item in regs["policies"]["entries"]}
    gates = {item["gate_id"]: item for item in regs["gates"]["gates"]}
    exceptions = {item["exception_id"]: item for item in regs["exceptions"]["entries"]}
    assert len(decisions) == len(regs["decisions"]["entries"])
    assert len(policies) == len(regs["policies"]["entries"])
    assert len(gates) == len(regs["gates"]["gates"])
    assert len(exceptions) == len(regs["exceptions"]["entries"])
    for item in regs["decisions"]["entries"]:
        assert set(item["policy_ids"]) <= set(policies)
        assert item["authorized_by_gate"] in gates
    for item in policies.values():
        assert item["decision_id"] in decisions
    for item in regs["traceability"]["entries"]:
        assert set(item["decision_ids"]) <= decisions
        assert set(item["policy_ids"]) <= set(policies)
        assert item["gate_id"] in gates

    market_status = "CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS"
    market_rows = {
        next(item for item in regs["decisions"]["entries"] if item["decision_id"] == "BT-STATE-002")["status"],
        policies["BT-POL-STATE-002"]["status"],
        next(item for item in regs["traceability"]["entries"] if item["capability_id"] == "BT-CAP-PIT-MARKET-STATE-CONSUMER-V0-1")["status"],
        next(item for item in regs["exceptions"]["entries"] if item["exception_id"] == "BT-EXC-010")["status"],
        gates["BT-GATE-014"]["status"],
    }
    assert market_rows == {market_status}
    run5 = ENGINE / "runs/bt_gate_014_single_use_physical_market_state_consumer_v0_5"
    assert load(run5 / "final_manifest.json")["validation_status"] == "PASS"

    bt15_status = "CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS"
    decision = next(item for item in regs["decisions"]["entries"] if item["decision_id"] == "BT-STATE-003")
    policy = policies["BT-POL-STATE-003"]
    trace = next(item for item in regs["traceability"]["entries"] if item["capability_id"] == "BT-CAP-PIT-EVENT-STATE-CONSUMER-V0-1")
    gate = gates["BT-GATE-015"]
    assert {decision["status"], policy["status"], trace["status"], gate["status"]} == {bt15_status}
    assert gate["implementation_acceptance"] == "ACCEPTED"
    assert gate["physical_execution"] == "V0_4_EXECUTED_ONCE_PASS_ACCEPTED"
    assert gate["postexecution_review"] == "PASS"
    assert gate["physical_authorization_v0_4"] == "CONSUMED_FINAL"
    assert gate["physical_state_rows_read"] == 8 and gate["physical_state_rows_selected"] == 1
    assert gate["event_state_events_emitted"] == 1 and gate["event_state_store_inserts"] == 1

    auth3 = load(ENGINE / "configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_3.json")
    assert auth3["status"] == "CONSUMED_BY_RUN_bt_gate_015_single_use_physical_event_state_consumer_v0_3"
    assert auth3["authorization_consumption_count"] == 1
    assert auth3["root_cause"] == "CONFIRMED_CONSUMER_DATASET_FINGERPRINT_DOMAIN_BINDING_ERROR"

    auth4 = load(ENGINE / "configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_4.json")
    run4 = ENGINE / "runs/bt_gate_015_single_use_physical_event_state_consumer_v0_4"
    expected_consumed = "CONSUMED_BY_RUN_bt_gate_015_single_use_physical_event_state_consumer_v0_4"
    assert auth4["status"] == expected_consumed
    assert auth4["consumed_by_run_id"] == "bt_gate_015_single_use_physical_event_state_consumer_v0_4"
    assert auth4["authorization_consumption_count"] == 1
    assert auth4["event_state_physical_read"] == "EXECUTED_PASS"
    assert auth4["physical_command_status"] == "EXECUTED_ONCE_PASS"
    assert auth4["postexecution_review_status"] == "PENDING_EXTERNAL_REVIEW"
    final4 = load(run4 / "final_manifest.json")
    assert final4["validation_status"] == "PASS"
    assert final4["physical_data_files_opened"] == 1
    assert final4["physical_state_records_scanned"] == 8
    assert final4["physical_state_rows_selected"] == 1
    assert final4["market_state_dependency_events"] == 1
    assert final4["event_state_events_emitted"] == 1
    assert final4["event_state_store_inserts"] == 1
    assert final4["bounded_probe_observations"] == 1
    assert final4["delivery_before_available_at"] == 0
    assert (final4["orders"], final4["fills"], final4["pnl_calculated"]) == (0, 0, False)
    assert final4["deterministic_output_hash"] == "35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a"
    for name, expected in final4["output_artifact_hashes"].items():
        assert sha(run4 / name) == expected, name
    assert load(run4 / "failure_manifest.json")["status"] == "SUPERSEDED_BY_FINAL_MANIFEST_PASS"

    review = ENGINE / "docs/00_system/31_BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW.md"
    assert "BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW = PASS" in review.read_text(encoding="utf-8")
    acceptance = ENGINE / "docs/00_system/34_BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE.md"
    acceptance_text = acceptance.read_text(encoding="utf-8")
    assert "BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW = PASS" in acceptance_text
    assert "92a723ed5a704c4631431fafc928abd01d223e3218467a0c423ad3046f98c9be" in acceptance_text
    external_reviews = ENGINE / "evidence/external_reviews/bt_gate_015"
    retained_reports = {
        "bt_gate_015_v0_3_postexecution_external_review_20260805.md": "faf069958509ee07d87db02e3e6bf9cc594758524d9eac77465b62e86d50e590",
        "bt_gate_015_v0_4_preexecution_external_review_20260805.md": "6f339fdfcb65e1a8b19b127bc9e4b9388d24ff381b1934032d9f6ab62615c405",
        "bt_gate_015_v0_4_postexecution_external_review_20260805.md": "92a723ed5a704c4631431fafc928abd01d223e3218467a0c423ad3046f98c9be",
    }
    for name, expected in retained_reports.items():
        assert sha(external_reviews / name) == expected, name
    governance_acceptance = ROOT / "08_GATES_AND_REVIEWS/BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE_V0_1.md"
    governance_acceptance_text = governance_acceptance.read_text(encoding="utf-8")
    assert "BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW = PASS" in governance_acceptance_text
    assert bt15_status in governance_acceptance_text
    postexecution_package = ENGINE / "deliverables/bt_gate_015_v0_4_physical_postexecution_packet_r1_20260805T150757Z.zip"
    assert sha(postexecution_package) == "62f1503694c9a3d9153179289b37bc4809d660315a0779cb8a30a52f367e0870"
    handoff = (ENGINE / "docs/00_system/CURRENT_PROJECT_HANDOFF.md").read_text(encoding="utf-8")
    assert "Status: `LIVE_RESTART_AUTHORITY`" in handoff and bt15_status in handoff

    pm = load(ROOT / "PACKAGE_MANIFEST.json")
    assert pm["status"] == "BT_GATE_015_CLOSED_PASS_POINT_IN_TIME_EVENT_STATE_CONSUMPTION_WITH_RESTRICTIONS"
    assert pm["manifest_regenerated_reason"] == "bt_gate_015_v0_4_postexecution_external_review_pass_and_gate_closed"
    current = pm["current_gate"]
    assert current["gate_id"] == "BT-GATE-015" and current["status"] == bt15_status
    assert current["v0_4"] == "CONSUMED_FINAL"
    assert current["physical_consumer_read"] == "V0_4_EXECUTED_PASS"
    assert current["postexecution_review"] == "PASS"
    assert current["next_required_action"] == "DEFINE_AND_REVIEW_BT_GATE_016_CONTRACT"
    candidate = pm["next_candidate_gate"]
    assert candidate["gate_id"] == "BT-GATE-016" and candidate["status"] == "NOT_OPEN"
    assert candidate["code_implementation"] == "NOT_AUTHORIZED"
    assert candidate["physical_read"] == "NOT_AUTHORIZED"
    assert pm["file_count"] == len(pm["files"])
    for relative, expected in pm["files"].items():
        assert sha(TSIS_ROOT / relative) == expected, relative

    print(json.dumps({
        "status": "PASS",
        "decision_count": len(decisions),
        "policy_count": len(policies),
        "traceability_capability_count": len(regs["traceability"]["entries"]),
        "exception_count": len(exceptions),
        "gate_count": len(gates),
        "bt_gate_015_status": bt15_status,
        "bt_gate_015_v0_3_state": auth3["status"],
        "bt_gate_015_v0_4_state": auth4["status"],
        "bt_gate_015_v0_4_validation": final4["validation_status"],
        "bt_gate_015_v0_4_records_scanned": final4["physical_state_records_scanned"],
        "bt_gate_015_v0_4_rows_selected": final4["physical_state_rows_selected"],
        "bt_gate_015_v0_4_events": final4["event_state_events_emitted"],
        "governance_package_hashes_verified": len(pm["files"]),
        "retained_external_review_reports": len(retained_reports),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
