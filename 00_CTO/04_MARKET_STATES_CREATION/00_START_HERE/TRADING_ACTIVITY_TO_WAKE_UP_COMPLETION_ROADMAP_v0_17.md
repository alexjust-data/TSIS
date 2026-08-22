# Trading Activity to Wake-up completion roadmap v0.17

## 0. Artifact control

| Field | Value |
|---|---|
| `document_version` | `v0_17` |
| `document_role` | `WORKSTREAM_COMPLETION_ROADMAP` |
| `document_status` | `CURRENT_PLANNING_SEQUENCE` |
| `current_stage` | `D07_FULL_CANDIDATES_COMPLETE_BLIND_PANEL_REPAIR_PROBE_PASS` |
| `current_next_gate` | `HUMAN_LAUNCH_FULL_BLIND_PANEL_REBUILD_ONLY` |
| `lineage_authority` | `TRADING_ACTIVITY_HANDOFF_AND_ROADMAP_LINEAGE_CONSOLIDATION_v0_1.md` |
| `supersedes_lineage` | `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_3 through v0_16` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-15` |

## 1. Closed dependency

```text
Daily Eligible Universe candidate               VALIDATED_EXPERIMENTAL
selector ownership                              SCREENER_ONLY
restricted consumption binding                  PASS
restricted binding role                         CONTROLLED_A_B_BRIDGE_ONLY
general Screener conceptual home                00_CTO/15_SCREENER_ENGINE
general Screener runtime                        NOT_CREATED_NOT_AUTHORIZED
development membership                          2,400/2,400 PASS_EXACT
development denominator                         55,866,000 PASS_EXACT
independent validation                          25/25 PASS
```

## 2. Current dependency order

```text
D07 candidate/control run on 2,400 development sessions COMPLETE
-> rebuild temporally balanced blind panel and gallery
-> staging and canonical terminal validation
-> two independent reviews and separate adjudication
-> WUL-D01..D08 evidence readout
-> explicit human D07 freeze
-> D07 development label and denominator materialization
-> D12 human target counts, salts and custodian
-> sealed temporal-validation membership/labels
-> sealed final-OOS membership/labels
-> D12 exact lockbox identity
-> independent B-02 audit and human freeze
-> B-03 implementation
-> variable-by-variable tests and one production-equivalent probe per shard
-> Binding B materialization on identical membership
-> A/B comparison on temporal validation at fixed false-alarm budget
-> selected candidate only opens final OOS
```

## 3. Boundary

The full candidate pools for temporal validation and final OOS are measured,
but target identities are not selected and no labels, metrics or outcomes are
exposed. The current PASS is restricted experimental consumption, not canonical
screener or Representation Model promotion. It lets A/B continue against one
hash-bound membership authority while the general project-wide Screener Engine
is governed separately under `C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE`.

## 4. D07 preparation closed

```text
implementation and unit tests       = COMPLETE
production-equivalent probe D1..D4  = PASS
repair probe validator              = 25/25 PASS
full preflight                      = PASS, 2,400 targets
full candidate run                  = COMPLETE, 2,400/2,400 and 4,447 candidates
initial blind panel                 = INVALID, 240/240 CLOSE_240M_PLUS
full blind-panel repair             = PENDING HUMAN LAUNCH
D07 freeze                          = NOT AUTHORIZED YET
```

Execution and recovery are governed by:

```text
04_EVENTS/WAKE_UP/03_LABELS/
WAKE_UP_RTH_ORACLE_CALIBRATION_IMPLEMENTATION_AND_PROBE_READOUT_v0_1.md
```

Incident and repair authority:

```text
04_EVENTS/WAKE_UP/03_LABELS/
WAKE_UP_RTH_BLIND_PANEL_STRATIFICATION_INCIDENT_AND_REPAIR_READOUT_v0_1.md
```
