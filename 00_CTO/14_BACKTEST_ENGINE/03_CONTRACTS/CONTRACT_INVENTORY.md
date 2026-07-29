# Contract inventory

| Contract | State | Authority / evidence |
|---|---|---|
| `backtest_input_manifest_contract_v0_1.json` | `DRAFT_CONSUMER_CONTRACT_NOT_AUTHORIZED_FOR_STATE_CONSUMPTION` | implementation tree |
| `backtest_run_spec_contract_v0_1.json` | `DRAFT_CONSUMER_CONTRACT_NOT_AUTHORIZED_FOR_STATE_CONSUMPTION` | implementation tree |
| `01_RUNPREFLIGHT_IMPLEMENTATION_PLAN_V0_1.md` | `IMPLEMENTED_BASELINE_WITH_STALE_HISTORICAL_STATUS` | preflight code/tests/runs supersede early snapshot |
| `03_REPLAY_IMPLEMENTATION_PLAN_V0_1.md` | `IMPLEMENTED_MINIMUM` | replay code/tests/run |
| `04_ACCOUNTING_IMPLEMENTATION_PLAN_V0_1.md` | `CLOSED_PASS` | accounting code/tests/run |
| `05_RUNPREFLIGHT_STATE_CONSUMPTION_IMPLEMENTATION_PLAN_V0_1.md` | `PROPOSED_NOT_AUTHORIZED` | no implementation |
| `06_STATE_REPLAY_FEED_IMPLEMENTATION_PLAN_V0_1.md` | `PROPOSED_NOT_IMPLEMENTED` | no implementation |
| `07_EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.md` | `CORRECTED_DRAFT_READY_FOR_REVIEW` | definition authorized; code not authorized |

## Lifecycle

```text
PROPOSED
→ DEFINITION_AUTHORIZED
→ DRAFT_FOR_REVIEW
→ REVIEWED_READY_FOR_IMPLEMENTATION_AUTHORIZATION
→ IMPLEMENTATION_AUTHORIZED
→ IMPLEMENTED
→ VERIFIED
→ CLOSED_PASS
```

`SUPERSEDED`, `DEFERRED`, `REJECTED` and `WITHDRAWN` may terminate or replace a lifecycle. No artifact may skip from draft to implemented merely because code exists.

