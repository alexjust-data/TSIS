# CURRENT_STATUS_AND_HANDOFF_v0_28

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `CURRENT_HANDOFF` |
| `snapshot_at` | `2026-08-17` |
| `active_workstream` | `d07_wake_up_rth_blind_panel_stratification_repair` |
| `next_gate` | `HUMAN_LAUNCH_FULL_BLIND_PANEL_REBUILD_ONLY` |
| `lineage_authority` | `TRADING_ACTIVITY_HANDOFF_AND_ROADMAP_LINEAGE_CONSOLIDATION_v0_1.md` |
| `supersedes_lineage` | `CURRENT_STATUS_AND_HANDOFF_v0_8 through v0_27` |

## 1. Exact position

```text
Daily Eligible Universe ownership             = SCREENER_ONLY_HUMAN_CONFIRMED
restricted consumption gate                   = PASS
candidate rows                                = 7,369,699
eligible candidate rows                       = 1,417,316
development target reconciliation             = 2,400/2,400 PASS_EXACT
development logical symbol-seconds             = 55,866,000 PASS_EXACT
independent gate validation                    = 25/25 PASS
operational/canonical screener                 = NOT_PROMOTED
general conceptual owner                       = 00_CTO/15_SCREENER_ENGINE
general runtime                                = NOT_CREATED_NOT_AUTHORIZED
Binding A evidence/replay                      = PASS_WITH_SCOPE_RESTRICTIONS
Binding B B-01                                 = FROZEN
Binding B B-02                                 = 10/12 RESOLVED NOT_FROZEN
D07 oracle implementation/tests                = COMPLETE
D07 production-equivalent probe D1..D4         = PASS
D07 repair probe validation                    = 25/25 PASS
D07 full preflight                             = PASS 2,400
D07 full candidate run                         = COMPLETE 2,400/2,400; 4,447 candidates
D07 initial blind panel                        = INVALID 240/240 CLOSE_240M_PLUS
D07 full blind-panel repair                    = PENDING_HUMAN_LAUNCH
D07 numeric/label authority                    = NOT_FROZEN
D12 selection/custody authority                = OPEN_HUMAN_DECISIONS
B-03 code                                      = NOT_AUTHORIZED
```

## 2. Selector authority

```text
membership source SHA
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

consumption manifest SHA
= c1ed29f2764e98bef0f4b4c90144cfce4c56db7d3d7d84b33255b50418b355d7

development denominator interval SHA
= 11ea435f69aa43e239b5b926a4788970686dfd7f24fb3a0533de7322e62615d4
```

Binding A and Binding B consume these identities. Neither owns or recalculates
the `[0.50,20.00]` and `<100M proxy` predicates.

This PASS is a controlled experimental bridge for the A/B workstream. It is
not the project-wide Screener Engine, a canonical daily-universe artifact or a
Backtest/live authorization. The general conceptual home is
`C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE`; its future independent runtime and
consumer adapters require separate gates.

## 3. Required next sequence

```text
human launches the hash-bound full blind-panel repair
-> staging and canonical terminal validators PASS
-> two independent blind reviews
-> separate adjudication
-> WUL-D01..D08 evidence readout
-> explicit human D07 freeze
-> materialize development labels and eligible denominator
-> scientific owner resolves D12 target counts/salts/custodian
-> independent custodian generates and seals validation/final-OOS identities
-> bind label and denominator hashes
-> independent B-02 consistency audit
-> explicit human B-02 freeze
-> B-03 implementation and required shard probes
```

## 4. SEC parallel lane

The SEC C01 T01 run is independent of this gate. At the last verified state it
was still running and lacked `final_manifest.json`. Its terminal audit must use
`_DESCAGRA_DATOS_NECESARIA_/SEC_PIT_C01_PRIMARY_T01_POSTDOWNLOAD_AUDIT_AGENT_PROMPT_v0_1.md`.

The `240/240 blocks`, `2,400 sessions`, zero-mismatch log is Binding A replay
evidence and must not be presented as SEC completion.

## 5. Prohibitions

- Do not call the selector candidate canonical or exact historical market cap.
- Do not present the restricted A/B bridge as the general Screener Engine.
- Do not implement membership rules inside A or B.
- Do not create labels or lockbox identities before their human gates.
- Do not open validation/final OOS or implement B-03.

## 6. Wake-up RTH oracle execution authority

Master process:

```text
04_EVENTS/WAKE_UP/03_LABELS/
WAKE_UP_RTH_ORACLE_CALIBRATION_END_TO_END_v0_1.md
```

Implementation/probe authority:

```text
04_EVENTS/WAKE_UP/03_LABELS/
WAKE_UP_RTH_ORACLE_CALIBRATION_IMPLEMENTATION_AND_PROBE_READOUT_v0_1.md
```

The 2,400-session candidate search is complete and remains valid. Its initial
panel is blocked because all 240 sampled cases fell in `CLOSE_240M_PLUS`.
The repair passed a 25/25 bounded probe and rebuilds only panel and gallery.
Authority:

```text
04_EVENTS/WAKE_UP/03_LABELS/
WAKE_UP_RTH_BLIND_PANEL_STRATIFICATION_INCIDENT_AND_REPAIR_READOUT_v0_1.md
```

Human review remains blocked until the repaired full panel passes staging and
canonical validation. This does not authorize B-03 or A/B comparison.
