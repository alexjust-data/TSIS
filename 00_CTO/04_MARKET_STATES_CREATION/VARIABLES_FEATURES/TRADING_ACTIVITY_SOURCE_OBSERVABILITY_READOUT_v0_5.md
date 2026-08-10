# TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_source_observability_readout` |
| `document_version` | `v0_5` |
| `document_role` | `SOURCE_GATE_EXECUTION_AND_TA_3_DEPENDENCY_READOUT` |
| `document_status` | `EXECUTED_WITH_NEW_UPSTREAM_DEPENDENCY` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `full_legacy_trade_source_gate` | `PASS_WITH_RESTRICTIONS` |
| `population_target_pit_selector_gate` | `PENDING` |
| `ta_3_design` | `PREREGISTERED` |
| `ta_3_broad_execution` | `BLOCKED_PENDING_PIT_SELECTOR_AND_SAMPLE_MANIFEST` |
| `oos_comparison` | `NOT_AUTHORIZED` |
| `canonical_feature_promotion` | `NOT_AUTHORIZED` |
| `supersedes` | `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_4.md` |
| `created_at` | `2026-08-07` |

---

## 1. What remains closed

The AACT pilot evidence and the legacy RTH trade-source verdict do not change:

```text
FULL LEGACY TRADE SOURCE GATE
= PASS_WITH_RESTRICTIONS

VALID SEMANTIC INTERPRETATION
= first observable transition during RTH

INVALID SEMANTIC INTERPRETATION
= first Wake-up of the complete episode
```

All row, grain, hash, temporal, coverage, trade-eligibility and baseline
evidence recorded by `v0_4` remains incorporated by reference.

---

## 2. New TA-3 dependency

The stratified sample requires proof that every selected historical
instrument-session satisfied:

```text
common stock eligibility as-of session
market cap at session start < $100M
$0.50 <= prior eligible close <= $20
```

`lt1b_universe_v0_1` and `instrument_master.lt1b_market_cap_t` do not provide
daily `<$100M` membership. They cannot be used as a silent replacement.

Current reusable physical sources exist:

```text
master_daily_table_v0_1
fundamentals_asof_table_v0_1
instrument_master_v0_1
market_calendar_v0_1
corporate_actions_table_v0_1
```

But their governed session-start join has not been executed or admitted.

---

## 3. Correct authorization split

```text
TRADING ACTIVITY TRADE-SOURCE RESEARCH
= AUTHORIZED_WITH_RESTRICTIONS

TA-3 SAMPLE DESIGN
= PREREGISTERED

PIT SELECTOR INVENTORY AND SOURCE AUDIT
= AUTHORIZED

TA-3 RUNNER GENERALIZATION AND TESTS
= AUTHORIZED

FINAL TA-3 SAMPLE MANIFEST
= PENDING PIT SELECTOR GATE

BROAD TA-3 MATERIALIZATION
= BLOCKED_PENDING_PIT_SELECTOR_AND_SAMPLE_MANIFEST

OOS
= NOT_AUTHORIZED
```

`v0_4` authorization for stratified development must be read as trade-source
authorization, not as permission to select historical contexts with an
unvalidated market-cap source.

---

## 4. Float boundary

Float is not required to calculate Binding A and does not block its source
gate. Ungoverned float is prohibited as a TA-3 selection filter.

```text
FLOAT SOURCE GATE
= NOT_EXECUTED

CANONICAL SCANNER FLOAT FILTER
= NOT_AUTHORIZED
```

Float may be joined later to the frozen sample only after an as-of source gate
passes.

---

## 5. Next source verdict

Authority:

```text
POPULATION_TARGET_PIT_RECOVERY_AND_GOVERNANCE_PLAN_v0_1.md
```

Required outcome:

```text
POPULATION_TARGET_PIT_SELECTOR_GATE
= PASS
  PASS_WITH_RESTRICTIONS
  or FAIL
```

Only then may the deterministic TA-3 sample manifest be frozen and broad-run
authorization reconsidered.

