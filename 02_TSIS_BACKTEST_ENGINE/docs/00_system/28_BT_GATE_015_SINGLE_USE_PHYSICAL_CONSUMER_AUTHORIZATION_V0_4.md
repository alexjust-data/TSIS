# BT-GATE-015 Single-Use Physical Event State Consumer Authorization V0.4

Status:

```text
AUTHORIZATION_ID = BT-GATE-015-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-4
V0.4 = AUTHORIZED_NOT_CONSUMED
PHYSICAL_COMMAND_EXECUTION = NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
EVENT_STATE_PHYSICAL_READ = NOT_EXECUTED
PHYSICAL_STATE_RECORDS_SCANNED = 0
PHYSICAL_STATE_ROWS_SELECTED = 0
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED
V0.3 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3 = PROHIBITED
```

This document issues a bounded single-use authorization candidate. It does not
approve execution. The command may run once only after an independent review
accepts the exact pre-execution ZIP and SHA-256.

## 1. Frozen Scope

```text
event_type = event_type:market_data:session_opened
instrument = AAME / figi_share_class:BBG001S5N8T1
exchange = XNYS
session = 2021-01-19
window = session_opened_at_anchor_context_v0_1
profile = event_state_core_four_intraday_profile_v0_1

candidate files = 1
candidate records scanned = 8
records selected = 1
Event State events = 1
EventStateStore inserts = 1
bounded observations = 1
```

The eight candidate records belong to the already governed provider file. The
single-use boundary authorizes opening that file and selecting exactly one row;
it does not authorize eight Event State deliveries.

## 2. Frozen Physical Identity

```text
candidate relative path =
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/
08_RUNTIME_CAPABILITIES/runs/
event_state_on_demand_bounded_execution_v0_1_20260727T200322Z/
event_state_candidate_records.jsonl

candidate SHA-256 =
ed975ad7d7a3e0ac68bd7dfe2c91743c86931a545162a4440d270cbb689477dd

candidate size = 70001 bytes

event_state_record_id =
e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76

event_state_record_fingerprint =
31f1463baf0dc8f0dba3bc130c0bb1d61092897595849df57abc6b1023853a01
```

Selection is exact by both record ID and Event State record fingerprint.

## 3. Dataset Fingerprint Domain Binding

V0.3 is `CONSUMED_FAILED_FINAL` and may never be reused. Its consumer
incorrectly compared the physical provenance fingerprint with the independent
availability-evidence dataset fingerprint.

V0.4 freezes two intentionally distinct authorities:

```text
physical Event State provenance:
source_market_state_candidate_dataset_fingerprint
=
market_state_dependency_dataset_fingerprint
=
433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

Market State replay availability evidence:
market_state replay sidecar candidate_dataset_fingerprint
=
market_state_availability_evidence_dataset_fingerprint
=
516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
```

The two values must remain different. Substituting one for the other fails
closed. Any physical-sidecar identity failure must persist the divergent field,
expected value and observed value in `failure_manifest.json`.

This correction changes only the backtester consumer, fixtures and diagnostics.
Provider data, provider handoffs and the frozen physical slice remain unchanged.
## 4. Governed Inputs

The machine-readable specification freezes eleven inputs:

```text
1. Event State candidate JSONL
2. Event State physical validation scope
3. Event State schema
4. initial provider handoff ZIP
5. Market State replay-availability sidecar
6. Market State schema
7. provider completion handoff ZIP
8. replay-availability authorization consumption
9. replay-availability sidecar contract
10. replay-availability sidecar manifest
11. typed payload binding
```

All metadata inputs are hashed before consumption. The candidate JSONL content
must not be opened before consumption; only existence and size may be checked.
After consumption, its bytes are SHA-256 checked before parsing and checked
again after the run to detect mutation.

## 5. Causal Execution

The only authorized sequence is:

```text
ReplayBarEvent
-> BoundedMarketStateAvailable dependency reconstructed from governed sidecar
-> BoundedEventStateAvailable
-> EventStateStore insert
-> bounded observation
```

At equal availability the canonical priority is:

```text
BAR = 1
MARKET_STATE = 2
EVENT_STATE = 3
```

The Market State dependency reconstruction does not open Market State Parquet
and is not inserted into `MarketStateStore` in this gate.

## 6. Durable Single-Use State Machine

```text
AUTHORIZED_NOT_CONSUMED
-> durable preconsumption guard
-> atomic state transition
-> CONSUMED_BY_RUN_bt_gate_015_single_use_physical_event_state_consumer_v0_4
-> durable receipt
-> physical access attempt
```

Any second use is prohibited. A failure after state consumption leaves V0.4
consumed and produces durable progress and failure evidence. It must never be
reset to `AUTHORIZED_NOT_CONSUMED`.

## 7. Required Evidence

Success must produce at least:

```text
authorization_consumption_receipt.json
pre_run_manifest.json
physical_progress.json
resolved_input_manifest.json
physical_selection_report.json
physical_identity_and_fingerprint_report.json
state_aware_event_sequence.json
bounded_market_state_dependency.json
bounded_event_state_event.json
event_state_store_trace.json
bounded_probe_observations.json
boundary_preservation_report.json
determinism_report.json
failure_manifest.json superseded by PASS
final_manifest.json
```

Failure after consumption must preserve the receipt when available, progress,
the exact failure code and a fail-closed manifest.

## 8. Explicitly Prohibited

```text
Market State physical read
provider modification
StateReplayFeed
general Event State consumption
other Event Types, instruments or sessions
strategy callbacks
orders
fills
PnL
execution or valuation use
full-history backtest
optimization or edge claims
```

## 9. Pre-Execution Command

The exact command, after an external PASS only, is:

```text
python -B RUN_BT_GATE_015_PHYSICAL_V0_4.py \
  --execute-authorized-physical-read
```

Running tests, validation or package generation must not invoke that command.

## 10. Next Decision

The pre-execution reviewer may return only:

```text
PASS_APPROVED_SINGLE_USE_V0_4
FAIL_TARGETED_CORRECTIONS_REQUIRED
```

Even after physical execution succeeds, `BT-GATE-015` remains open until the
post-execution evidence receives independent acceptance.
