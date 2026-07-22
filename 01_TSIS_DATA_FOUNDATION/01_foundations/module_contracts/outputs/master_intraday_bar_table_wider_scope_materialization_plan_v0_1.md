## 2026-07-07 Quotes Root Supersession

`D:/quotes -> E:/TSIS/data/quotes_` is closed and approved. The official quotes E-root for new downstream work is `E:/TSIS/data/quotes_`, backed by Phase A structural parity and Phase B SHA256 retry evidence. Historical artifacts built from `D:/quotes` remain pre-approval/provenance evidence and must be rebuilt against the approved E-root before promotion to an official downstream table. The legacy `E:/TSIS/data/quotes` tree remains incomplete for this decision.

﻿# Master Intraday Bar Table Wider-Scope Materialization Plan `v0_1`

## 1. Purpose

This document defines the next governed work loop for expanding
`master_intraday_bar_table` beyond its current v0.1 scoped pilot.

It is a plan and promotion contract. It does not create, certify or promote a
new parquet dataset.

Current official table:

```text
dataset_id: master_intraday_bar_table_v0_1
scope: scoped_split_normalized_event_cases
full_universe_claim: false
backtest_core_bar_candidate_rows: 0
```

The existing v0.1 table remains valid only for its declared scope. It must not
be reinterpreted as a full intraday universe.

## 2. Why This Loop Exists

`market_state_table` and `event_state_table` are downstream state
compositions. They require stronger intraday coverage before they can be
promoted beyond deterministic fixtures or controlled samples.

Therefore the next institutional loop is:

```text
1. strengthen master_intraday_bar_table coverage
2. strengthen microstructure_features_table coverage
3. build controlled real market_state/event_state samples
4. only then consider broader state materialization
```

The reason is technical:

- intraday bars define the time-local price path around events;
- split-normalized minute bars are required for cross-session and ML/RL
  comparable states;
- raw minute bars remain closer to observed price scale but are not enough for
  split-safe multi-day context;
- quote/trade microstructure is still separate and must not be inferred from
  1m OHLCV.

## 3. Non-Negotiable Boundary

The following rule is binding:

```text
No se lanza full-universe ciego.
```

A wider or full-scope table cannot be created by just pointing the current
builder at a larger folder.

Before any broad materialization, the run must define:

- source root;
- declared denominator;
- materialization scope;
- price-view strategy;
- expected row/file reconciliation;
- manifest policy;
- quality gates;
- recomputation tests;
- output path;
- version id;
- Graphify/changelog/registry updates.

## 4. What "Full Universe" Means Here

For this table, `full_universe` does not mean every possible historical ticker
or every theoretical minute.

It must mean a declared denominator such as:

```text
universe_policy: <1B> official ticker universe / PTI scope
date_range: explicit start/end
raw_availability_root: E:/TSIS/data/ohlcv_1m
calendar_policy: official market calendar/session policy
corporate_action_policy: governed split adjustment source
quality_policy: declared raw 1m quality manifest inheritance
```

The denominator must be materialized or referenced in a manifest before any
claim can be made.

Allowed examples:

```text
master_intraday_bar_table_v0_2_candidate
scope = split_affected_full_universe_logical_view_candidate
full_universe_claim = false until validation gates pass
```

```text
master_intraday_bar_table_v0_3_candidate
scope = physical_full_universe_1m_split_normalized_candidate
full_universe_claim = false until validation gates pass
```

Forbidden examples:

```text
reuse master_intraday_bar_table_v0_1 with a larger source root
claim full_universe=true without denominator manifest
mix smoke outputs with official outputs
promote a test run because parquet files exist
```

## 5. Source Dependencies

Current required source roots:

```text
raw_1m_root = E:/TSIS/data/ohlcv_1m
split_actions_root = E:/TSIS/data/additional/corporate_actions/splits
current_pilot_split_normalized_root = E:/TSIS/data/ohlcv_1m_split_normalized
candidate_split_affected_root = E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate
candidate_physical_full_root = E:/TSIS/data/ohlcv_1m_split_normalized_physical_full_candidate
output_root = E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table
```

Do not use historical `D:/` or `C:/TSIS_Data/data/...` roots for the official
path unless a separate parity/audit document explicitly authorizes it.

Quote-guarded candidate dependency:

```text
quote_guarded_repair_run_root = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
quote_guarded_official_root = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
quote_guarded_manifest = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
quote_guarded_current_quotes_root = D:/quotes
quote_guarded_current_quotes_root_state = pre_approval_d_recovery_lineage_requires_rebuild
quote_guarded_final_state = promoted_lt1b_manifest_available
```

The quote-guarded route is governed by:

```text
01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
```

This route is now allowed to proceed to builder preflight and candidate
materialization attempts against the promoted LT1B manifest. It still cannot be
promoted until candidate output evidence, tests and review pass.

## 6. Recommended Path

The preferred first institutional path is not the physical full copy.

Recommended path:

```text
Path A1: logical split-safe full-universe candidate
```

Meaning:

- materialize ticker-months where a future split changes price scale;
- treat factor-1 ticker-months as logically equivalent for split-normalized
  price scale when the manifest proves no future split adjustment is needed;
- avoid duplicating every raw 1m parquet where no price scale changes;
- preserve raw 1m as observed-price context.

Only use the physical full copy path if downstream readers require one root
containing every minute parquet:

```text
Path A2: physical full copy candidate
```

Parallel dependency path:

```text
Path B1: quote-guarded raw-scale candidate
```

Meaning:

- preserve raw 1m as observed;
- apply the quote-guarded repair manifest as an overlay price view;
- do not modify `E:/TSIS/data/ohlcv_1m`;
- do not reconstruct VWAP from quotes;
- mark VWAP-invalid rows as blocked for direct VWAP consumption;
- keep `full_universe_claim=false` until the final denominator and validation
  gates pass.

Path B1 is no longer blocked on the quote-guarded repair manifest. It is now
blocked on builder/preflight/materialization evidence. The current `D:/quotes`
dependency is accepted only as provisional candidate lineage and must carry
rebuild flags.

## 7. Current Builder Gap

The current builder is not sufficient for a wider/full-scope official claim.

Current builder:

```text
scripts/materialize_master_intraday_bar_table.py
```

Current hardcoded semantics:

```text
dataset_id = master_intraday_bar_table_v0_1
materialization_scope = scoped_split_normalized_event_cases
full_universe_claim = false
price_views = 1m_raw, 1m_split_normalized
default split root = E:/TSIS/data/ohlcv_1m_split_normalized
```

Required builder changes before a wider run:

- config-driven dataset id;
- config-driven schema/policy version;
- config-driven source root;
- config-driven output root;
- config-driven materialization scope;
- explicit candidate status;
- denominator manifest input;
- no overwrite of v0.1 output;
- manifest/tree hash generation;
- partition-level reconciliation;
- row-level `full_universe_claim` defaulting to false;
- backtest-core eligibility computed only after quality gates pass.

Additional quote-guarded builder requirements:

- consume a quote-guarded manifest or partition list, not a blind recursive
  scan over millions of files;
- keep `master_intraday_bar_table_v0_1` immutable;
- write quote-guarded candidates only to a new candidate path;
- include repair lineage columns from the quote-guarded contract;
- support `1m_raw` and `1m_quote_guarded_raw` as the first candidate price
  views;
- block `1m_quote_guarded_split_normalized` until split normalization over
  quote-guarded OHLC is separately tested.

## 8. Execution Sequence

### Step 1 - Smoke the 1m split-safe manifest

Run first:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_1m_split_normalized_materialization.ps1" `
  -SmokeOnly `
  -SmokeLimit 100 `
  -Mode split-affected
```

Expected output:

```text
manifest_smoke.csv
manifest_smoke.summary.json
```

Smoke outputs are never promoted.

### Step 2 - Run split-affected candidate materialization

Preferred overnight command:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_1m_split_normalized_materialization.ps1" `
  -Mode split-affected `
  -RunAudit
```

Expected candidate root:

```text
E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate
```

Expected audit outputs are defined in:

```text
01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
```

### Step 3 - Review candidate evidence

Do not continue until the run has:

- manifest summary;
- manifest row count;
- materialized file count;
- skipped/existing file accounting;
- split-event audit outputs;
- error log review;
- output root size and file count summary;
- explicit candidate status.

### Step 4 - Build `master_intraday_bar_table` candidate

Only after Step 3, modify or wrap the builder to create a new candidate:

```text
dataset_id = master_intraday_bar_table_v0_2_candidate
scope = split_affected_full_universe_logical_view_candidate
full_universe_claim = false
```

This candidate must write to a new path:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate/
```

It must not modify:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_1/
```

### Step 5 - Test before promotion

The candidate is not institutional until tests pass and evidence is recorded.

Required tests:

- source denominator reconciliation;
- parquet file count reconciliation;
- row count reconciliation by price view;
- no duplicate `ticker + ts_utc + bar_size + price_view`;
- selected OHLC integrity;
- non-negative volume;
- split formula integrity for affected months;
- factor-1 logical equivalence where applicable;
- raw 1m quality manifest inheritance;
- no direct execution truth claim;
- no `full_universe_claim=true` unless denominator/audit pass;
- no ML/RL direct consumption unless state builder and labels remain separate.

## 9. Promotion Gate

Promotion requires all of the following:

- new schema or schema addendum;
- new dataset contract or v0.2 contract;
- updated consumption policy;
- updated dataset registry entry;
- updated validator document;
- updated builder/config manifest;
- test-run evidence under `C:/TSIS_Data/tests/test_runs/...`;
- changelog entry;
- Graphify refresh queue entry;
- human review of manifest/audit summaries.

Until then, status remains:

```text
candidate_only
```

## 10. Consumer Semantics

Even after wider materialization, this table is still an intraday bar table.

It can support:

- event-window reconstruction;
- premarket/opening-drive context;
- cross-session state features when split-safe;
- controlled backtest context after quality gates;
- ML/RL state feature inputs only through governed state builders.

It does not replace:

- trades tick data;
- quotes/order-book data;
- execution fill model;
- live corporate event alert feeds;
- short-sale constraints;
- market-state composition contracts.

## 11. Stop Conditions

Stop and do not promote if any of the following occur:

- source roots are mixed across `D:/`, `C:/TSIS_Data/data` and `E:/TSIS/data`
  without a parity contract;
- manifest denominator is missing;
- output row counts cannot be reconciled;
- split formula tests fail;
- factor-1 logical equivalence cannot be proven;
- raw quality inheritance is missing;
- logs show unreviewed errors;
- the builder writes into v0.1 paths;
- tests only prove a smoke sample but documentation claims broad coverage.

## 12. Next Agent Checklist

The next agent should execute in this order:

1. Read this document.
2. Read
   `01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md`.
3. Review the latest successful smoke command evidence.
4. If smoke must be rerun, verify it uses `scan_strategy =
   split_tickers_then_partition_direct`.
5. If smoke is clean, ask the human whether to launch the overnight
   `split-affected -RunAudit` command or provide it for manual execution.
6. After candidate split-safe output exists, implement the config-driven
   `master_intraday_bar_table_v0_2_candidate` builder path.
7. Add candidate tests.
8. Only then discuss promotion.

## 13. Current Status

```text
status: split_safe_smoke_manifest_passed
official_new_dataset_created: false
heavy_materialization_started: false
full_universe_claim_granted: false
quote_guarded_candidate_contract_defined: true
quote_guarded_candidate_materialized: false
quote_guarded_final_e_root_ready: true
quote_guarded_manifest: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
next_executable_action: run quote-guarded candidate builder preflight against promoted manifest
```

Latest smoke evidence:

```text
run_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_153012/
rows: 100
tickers: 1
scan_strategy: split_tickers_then_partition_direct
files_seen: 139
files_without_split_effect: 39
split_tickers_seen: 4
official_dataset_created: false
```

Latest regression test evidence:

```text
test_run: C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_1m_split_manifest_builder_v0_1/
tests: 2
passed: 2
failed: 0
skipped: 0
```
