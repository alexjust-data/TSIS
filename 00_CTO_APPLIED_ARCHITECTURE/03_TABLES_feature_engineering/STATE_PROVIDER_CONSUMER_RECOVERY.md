# State Provider / Consumer Recovery

Status: `current_recovery_authority_v0_1`
As of: `2026-07-30`
Scope: Market State, Event State, State Provider and BT-GATE-014 handoff

This is the canonical cold-start entry for the current State
provider-consumer boundary. It summarizes navigation and current authority; it
does not replace accepted contracts, manifests, matrices, readouts or packages.

## Current State

```text
Market State scope = core-four profile validated for the bounded path
Event State scope = session_opened capability exists with restrictions
State Provider control-plane = REFROZEN_AT_V0_1_2_WITH_RESTRICTIONS
provider/shared-boundary PIT probe = CLOSED_PASS_WITH_RESTRICTIONS
physical rows read by provider probe = 2
bounded temporal envelope events emitted = 2
consumed provider authorization reusable = false
BT-GATE-014 provider evidence handoff = COMPLETE
backtester current-gate authority = 02_TSIS_BACKTEST_ENGINE/AGENTS.md
backtester mutable status duplicated here = false
Event State provider-to-consumer handoff = NOT_OPEN_AT_PROVIDER_HANDOFF
active provider gate = none
restriction-domain clarification = CLOSED_PASS
BT-GATE-014 V0.4 failure evidence = ACCEPTED_FAIL_CLOSED
BT-GATE-014 next required work = consumer adoption of restriction-domain binding
```

The provider probe proved exact physical selection, schema validation,
fingerprint verification, one-to-one temporal sidecar binding and legal replay
ordering. It did not prove that the backtester receives the 17 scientific
core-four values in a typed consumer event.

The later BT-GATE-014 V0.4 consumer probe opened one physical file and read two
rows, then failed closed before event emission because the consumer compared
two different restriction domains for equality. The shared boundary has now
closed:

```text
market_state_restriction_domain_binding_clarification_v0_1
=
CLOSED_PASS_RESTRICTION_DOMAINS_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ_NO_CONSUMER_AUTHORIZATION
```

The binding distinguishes:

```text
physical_provenance_restriction_codes
replay_consumption_restriction_codes
component_replay_restriction_codes
```

V0.4 remains consumed and cannot be reused. No V0.5 authorization was issued.

## Exact Accepted Evidence

```text
provider evidence package path =
99_archive/
bounded_state_bundle_read_and_replay_execution_and_review_v0_1_files_20260730T080831Z.zip

SHA-256 =
8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7

compact BT-GATE-014 handoff package path =
99_archive/
market_state_pit_bt_gate_014_contract_handoff_v0_1_20260730T091041Z.zip

SHA-256 =
2c578ce9216bb3fd9010ef1f4afe8ba4022ab6b15f665d276a957f50acb35112
```

The compact package contains the accepted provider package unchanged plus the
schema/runtime binding and direct metadata needed by the consumer. Neither
package contains the physical parquet. These two exact ZIPs are explicit Git
exceptions because they are accepted institutional handoff evidence. Other
ZIPs remain ignored.

## Schema and Runtime Content Binding

```text
structural schema authority =
PHYSICAL_SCHEMA_CONTRACT.json
SHA-256 595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b

profile provenance parquet reference =
b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2

current bounded runtime content authority =
bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68
```

The provenance and current runtime hashes are not interchangeable. The
machine-readable authority is:

```text
09_STATE_CONSUMPTION_BOUNDARY/
market_state_core_four_scale_validation_physical_schema_binding_v0_1.json
```

## Mandatory Reading Route

After the root TSIS mandatory reading order:

```text
1. 00_CTO_APPLIED_ARCHITECTURE/LOCAL_RULES.md
2. 03_TABLES_feature_engineering/LOCAL_RULES.md
3. 03_TABLES_feature_engineering/STATE_PROVIDER_CONSUMER_RECOVERY.md
4. 03_TABLES_feature_engineering/AGENT.md
   - only the first handoff block is current
5. 03_TABLES_feature_engineering/99_ruta_de_trabajo.md
   - newest block first
6. 03_TABLES_feature_engineering/09_STATE_CONSUMPTION_BOUNDARY/README.md
7. 09_STATE_CONSUMPTION_BOUNDARY/market_state_pit_bt_gate_014_handoff_v0_1.md
```

For evidence-level verification, continue with:

```text
8. market_state_restriction_domain_binding_clarification_v0_1.json
9. market_state_restriction_domain_binding_clarification_readout_v0_1.md
10. market_state_core_four_scale_validation_physical_schema_binding_v0_1.json
11. market_state_core_four_scale_validation_physical_schema_binding_readout_v0_1.md
12. bounded_state_bundle_read_and_replay_review_readout_v0_1.md
13. bounded_state_bundle_read_and_replay_review_matrix_v0_1.json
14. 09_STATE_CONSUMPTION_BOUNDARY/runs/
    bounded_state_bundle_read_and_replay_execution_v0_1_20260730T075225Z/
    final_manifest.json
15. the same run directory / bounded_replay_report.json
```

`00_TABLES_MARKET_STATE_EVENT_STATE.md` is foundational conceptual
architecture. Its authority banner and section labels must be respected; it is
not the single executable contract.

## Next Owner and Work

The next owner is the BT-GATE-014 backtester agent. Its immediate work is:

```text
adopt market_state_restriction_domain_binding_clarification_v0_1;
separate physical provenance restrictions from replay-consumption restrictions;
preserve the physical raw restriction JSON and 26-code lineage;
use the four bounded restrictions for executable replay-consumption policy;
preserve component restrictions under their labeled domain;
add negative tests against domain loss, substitution and unlabeled union;
propose a new single-use authorization only after external pre-execution review.
```

This list records the handoff scope; it is not the current backtester gate.

Required equal-timestamp precedence:

```text
source bar closed and incorporated
-> Market State becomes eligible
-> Market State stored
-> bounded consumer probe may observe it
```

The provider handoff is complete. The backtester may advance independently
under its own governance. Read `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/AGENTS.md`
for its current gate, authorizations, execution counters and next permitted
operation. Do not copy that mutable state into this provider recovery file.

## Closed Work

Unless a new material defect is demonstrated, do not reopen:

```text
provider contract schema hardening v0.1.2;
provider-consumer control-plane compatibility regression;
Market State replay availability timestamp contract;
scale-validation replay sidecar;
physical evidence alignment v0.2;
provider/shared-boundary bounded authorization;
provider/shared-boundary bounded physical execution and review;
schema provenance/runtime content binding clarification.
```

## Still Prohibited

```text
reuse of the consumed provider authorization;
reuse of provider-side physical authority by any consumer;
general StateReplayFeed or general backtest State consumption;
Event State consumption;
strategy callbacks, orders, fills or PnL;
Market State used as an execution price;
official dataset promotion;
production or general downstream use.
```

## Recovery Test

A new agent is correctly oriented only if it can state:

```text
provider v0.1.2 is accepted and frozen with restrictions;
the provider PIT probe read two exact ACIU rows;
the provider authorization is consumed and cannot be reused;
the probe emitted temporal envelopes, not a typed 17-value consumer payload;
BT-GATE-014 provider evidence handoff is complete;
the backtester owns its current gate and reports it in its own AGENTS.md;
Event State handoff was not opened by this provider work;
the next owner is the backtester;
active provider gate = none.
```

If any answer differs, stop and reconcile it against accepted evidence before
changing code or requesting physical data.
