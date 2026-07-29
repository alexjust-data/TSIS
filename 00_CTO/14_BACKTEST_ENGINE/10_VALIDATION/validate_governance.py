from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTERS = {
    "decisions": ROOT / "04_DECISIONS" / "DECISION_LEDGER.json",
    "policies": ROOT / "05_POLICIES" / "POLICY_REGISTER.json",
    "traceability": ROOT / "06_TRACEABILITY" / "TRACEABILITY_MATRIX.json",
    "exceptions": ROOT / "07_EXCEPTIONS" / "EXCEPTION_AND_WAIVER_REGISTER.json",
    "gates": ROOT / "08_GATES_AND_REVIEWS" / "GATE_REGISTER.json",
}


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    docs = {name: load(path) for name, path in REGISTERS.items()}
    decisions = {row["decision_id"] for row in docs["decisions"]["entries"]}
    policies = {row["policy_id"]: row for row in docs["policies"]["entries"]}
    gates = {row["gate_id"] for row in docs["gates"]["gates"]}
    exceptions = {row["exception_id"] for row in docs["exceptions"]["entries"]}

    assert len(decisions) == len(docs["decisions"]["entries"])
    assert len(policies) == len(docs["policies"]["entries"])
    assert len(gates) == len(docs["gates"]["gates"])
    assert len(exceptions) == len(docs["exceptions"]["entries"])

    for row in docs["decisions"]["entries"]:
        assert set(row["policy_ids"]) <= set(policies)
        assert row["authorized_by_gate"] in gates
    for row in policies.values():
        assert row["decision_id"] in decisions
    for row in docs["traceability"]["entries"]:
        assert set(row["decision_ids"]) <= decisions
        assert set(row["policy_ids"]) <= set(policies)
        assert row["gate_id"] in gates

    print(
        json.dumps(
            {
                "status": "PASS",
                "decision_count": len(decisions),
                "policy_count": len(policies),
                "traceability_capability_count": len(docs["traceability"]["entries"]),
                "exception_count": len(exceptions),
                "gate_count": len(gates),
                "register_sha256": {
                    name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for name, path in REGISTERS.items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
