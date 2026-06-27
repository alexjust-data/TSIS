# OHLCV 1m Quote-Guarded Single Reading v0.1

## 1. Nature Of This Document

This document is a consolidated single reading for the
`ohlcv_1m_quote_guarded_v0_1` workstream.

It is a module contract / state-and-design document. It does not replace the
future dataset contract, schema contract, consumption policy, registry entry,
validators or inspection dossier.

Its role is to let a human inspector understand the whole topic before opening
the lower-level documents.

## 2. Problem

Some raw one-minute OHLCV bars under:

```text
E:/TSIS/data/ohlcv_1m
```

show minute candles whose `open`, `high`, `low` or `close` are incompatible
with the observed quote book during the same minute.

The initial motivating cases were:

```text
TWG   2026-01-20  premarket
TIRX  2026-01-28  premarket
RVYL  2026-01-23  premarket
SHPH  2026-01-20  premarket
```

The defect appears as extreme false wicks, impossible low/high prints or
open/close values outside the quote envelope. These bars can distort:

- visual chart inspection;
- premarket first-push detection;
- dip/rebreak event detection;
- DAS candidate generation;
- event research;
- flagged backtests;
- ML/event feature generation if flags are not preserved.

## 3. Existing Institutional Context

The workstream depends on these existing foundations:

- `ohlcv_1m_raw_v0_1`
  - raw one-minute OHLCV layer;
  - institutionally understood;
  - not globally clean;
  - governed by `ohlcv_1m_raw_dataset_contract_v0_1.md`.

- `quotes_core_v0_1`
  - observed quote book;
  - target session scope `04:00-20:00 America/New_York`;
  - institutional dataset for local book evidence;
  - governed by `quotes_dataset_contract_v0_1.md`.

- `market_session_scope.md`
  - declares extended hours as institutional target scope for market data;
  - notes that `trades` session coverage remains an open limitation.

- `price_semantics_and_adjustment_policy.md`
  - requires explicit price views;
  - rejects a single undifferentiated "price" truth.

## 4. Important Source Finding

For the four motivating cases:

- `D:/quotes` contains premarket quote observations.
- `E:/TSIS/data/trades_ticks_prod_2005_2026` and
  `C:/TSIS_Data/data/trades_ticks_prod_2005_2026` begin at regular session
  for those ticker-days.

Therefore, the currently available local source can:

- detect and bound impossible OHLC bars with quotes;
- support a provisional quote-guarded price view;
- preserve evidence for future trade-tape rebuild.

It cannot:

- reconstruct exact executed premarket OHLCV;
- reconstruct real minute VWAP;
- prove execution quality;
- replace a future extended-hours Polygon trades rebuild.

## 5. Terminology

### Quote Envelope

The quote envelope is a minute-level range derived from valid quote
observations for the same ticker and minute.

The initial conservative form should use robust quote statistics, for example:

```text
bid_floor = robust lower bid bound
ask_cap   = robust upper ask bound
```

The exact percentiles and spread filters must be fixed in the validator and
audit run configuration.

### NBBO

NBBO means National Best Bid and Offer: the best displayed bid and offer across
eligible venues at a moment in time.

This workstream should not claim `NBBO` in the dataset name until the project
proves that the available `D:/quotes` source is already NBBO-consolidated or
that the builder constructs a valid NBBO-equivalent envelope.

For now, the safer institutional term is:

```text
quote envelope
```

## 6. Proposed Dataset Identity

Recommended identity:

```text
ohlcv_1m_quote_guarded_v0_1
```

Dataset family:

```text
ohlcv_1m
```

Layer type:

```text
derived_price_view
```

Price view:

```text
quote_guarded_raw_ohlc
```

Promotion state at creation:

```text
provisional_governance_defined
```

The state can only move toward `validated` after pilot evidence, negative
controls, visual inspector evidence and reproducible manifests exist.

## 7. What This Layer Represents

`ohlcv_1m_quote_guarded_v0_1` represents raw one-minute OHLC bars after applying
a quote-book guardrail to components that violate the observed quote envelope.

It is a provisional derived view for:

- charting;
- event detection;
- DAS scanner research;
- backtest sensitivity;
- data-quality overlays;
- future repair manifests.

It preserves the raw bar lineage and must keep flags for every repaired or
unverified component.

## 8. What This Layer Does Not Represent

This layer is not:

- raw source data;
- exact trade-derived OHLCV;
- exact VWAP;
- execution truth;
- adjusted economics;
- split normalization;
- proof that the underlying raw file is clean;
- proof that the quote source is clean for every minute;
- a permanent substitute for extended-hours trades.

## 9. Core Repair Principle

Raw data must remain immutable.

The repair must be expressed as:

```text
raw ohlcv_1m + quote-derived repair manifest -> quote_guarded view
```

The preferred first implementation is:

```text
global audit manifest + official loader overlay
```

not local chart-specific fixes.

## 10. Why Not Delete Bad Minutes

Deleting the minute is not the preferred default because it can:

- break one-minute continuity;
- distort event duration;
- erase volume timing;
- damage first-push / dip / rebreak segmentation;
- make different consumers see different timelines.

Quote-guarding preserves the minute while marking that price components were
bounded by quote evidence.

Deletion or exclusion remains valid only for states such as:

```text
quote_insufficient_review
quote_unusable
hard_invalid_unrepairable
```

## 11. Provisional Repair Logic

For a minute with sufficient valid quote evidence:

```text
h_qg = min(h_raw, quote_ask_cap)
l_qg = max(l_raw, quote_bid_floor)
o_qg = clamp(o_raw, quote_bid_floor, quote_ask_cap)
c_qg = clamp(c_raw, quote_bid_floor, quote_ask_cap)
```

Then enforce OHLC consistency:

```text
h_qg >= max(o_qg, c_qg, l_qg)
l_qg <= min(o_qg, c_qg, h_qg)
```

`v` can be preserved only as raw volume with `volume_unverified` when the price
bar was repaired.

`vw` must not be silently repaired from quotes. It should be:

- preserved as `vw_raw`;
- marked invalid when outside the quote-guarded OHLC range;
- optionally set to null in the clean consumer columns;
- marked `needs_future_trade_rebuild`.

## 12. Required State Vocabulary

Minimum minute-level states:

```text
clean_no_repair
quote_repairable_ohlc
quote_repairable_ohlc_vw_invalid
vw_invalid_only
quote_insufficient_review
quote_unusable
needs_future_trade_rebuild
```

These states are not final until validator and policy documents freeze them.

## 13. Required Manifest Concept

The audit should produce a global repair manifest with one row per affected
ticker-minute.

Minimum fields:

```text
dataset_id
repair_version
run_id
ticker
ts_utc
session_date
session_segment
source_ohlcv_file
source_quotes_file
raw_o
raw_h
raw_l
raw_c
raw_v
raw_vw
quote_rows
quote_bid_floor
quote_ask_cap
quote_spread_pct
o_qg
h_qg
l_qg
c_qg
repair_action
repair_flags
quote_quality_state
volume_policy
vw_policy
needs_future_trade_rebuild
```

## 14. Loader Semantics

Consumers must not patch bars locally.

They should call an official loader, conceptually:

```python
load_ohlcv_1m(..., layer="quote_guarded")
```

The loader should:

1. load the raw ticker-month parquet;
2. load manifest rows for the requested ticker/time range;
3. apply replacements in memory;
4. attach flags and provenance columns;
5. return a single consistent quote-guarded view.

If runtime cost is high, selected clean partitions may be materialized from the
same manifest. The manifest remains the source of truth for the repair.

## 15. Documentation Surfaces Required

This workstream needs the full foundation chain:

```text
canonical schema
-> dataset contract
-> consumption policy
-> dataset registry entry
-> validators
-> inspection dossier
-> evidence assets
-> data quality report
-> changelog
```

### Module Contract Folder

Current folder:

```text
01_foundations/module_contracts/ohlcv_1m_quote_guarded/
```

Purpose:

- consolidate the workstream;
- explain the protocol;
- provide a single reading.

### Dataset Contract

Planned:

```text
01_foundations/contract_registry/dataset_contracts/ohlcv_1m_quote_guarded_dataset_contract_v0_1.md
```

Must define:

- dataset identity;
- status;
- semantic scope;
- source lineage;
- quote-envelope repair semantics;
- consumers;
- limitations;
- change policy.

### Canonical Schema

Planned:

```text
01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_quote_guarded_schema_contract.md
```

Must define:

- raw columns preserved;
- quote envelope fields;
- quote-guarded OHLC fields;
- flags;
- provenance;
- key `ticker + ts_utc`.

### Consumption Policy

Planned:

```text
01_foundations/data_consumption_policies/ohlcv_1m_quote_guarded_consumption_policy.md
```

Must define allowed and prohibited use by consumer class.

### Registry Entry

Planned:

```text
01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_quote_guarded_registry_entry.yaml
```

Must locate:

- manifest root;
- optional materialized root;
- source roots;
- builder;
- evidence;
- status.

### Validators

Planned:

```text
01_foundations/validators/ohlcv_1m/ohlcv_1m_quote_guarded_validators.md
```

Must define:

- quote coverage checks;
- quote validity checks;
- OHLC outside-envelope checks;
- spread sanity;
- repair invariants;
- VW invalidation;
- manifest schema checks;
- consumer flag preservation checks.

### Inspection Dossier

Planned:

```text
01_foundations/inspection_dossiers/1m_quote_guarded/
```

Must include:

- README;
- pilot readout;
- full audit readout;
- population summary;
- before/after visual inspector pack;
- case manifests;
- evidence assets;
- asset audit.

### Data Quality Report

Planned:

```text
01_foundations/data_quality_report/families/ohlcv_1m_quote_guarded_quality_report_v0_1.md
```

Must summarize:

- population scanned;
- affected minutes;
- repaired minutes;
- quote-insufficient minutes;
- residual debt;
- consumer matrix;
- final verdict.

## 16. Operational File Structure

Audit runs:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/ohlcv_1m_quote_guard_audit/<run_id>/
  run_manifest.json
  task_inventory.parquet
  progress/
  repair_shards/
  summaries/
  visual_samples/
```

Promoted output root, if materialized:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/
  ohlcv_1m_quote_guarded_v0_1/
  _repair_manifest_v0_1.parquet
  _quality_summary_v0_1.parquet
  _quote_coverage_summary_v0_1.parquet
  _run_manifest_v0_1.json
```

Raw `E:/TSIS/data/ohlcv_1m` must not be modified.

## 17. Parallel Audit Strategy

The full universe is large. The audit should be parallel and resumable.

Recommended work unit:

```text
ticker-month ohlcv parquet
```

Each worker should:

1. read one raw ticker-month;
2. group bars by session date;
3. load only the required `D:/quotes/<ticker>/year=YYYY/month=MM/day=DD/quotes.parquet` files;
4. build minute quote envelopes;
5. detect affected minutes;
6. write only affected rows to a shard;
7. write task status atomically.

The full run should consolidate shards only after all task manifests pass
integrity checks.

## 18. Pilot Sequence

Recommended sequence:

### Phase 0 - Governance Definition

Create this folder and the initial contract stack.

### Phase 1 - Four-Case Pilot

Use:

```text
TWG 2026-01-20
TIRX 2026-01-28
RVYL 2026-01-23
SHPH 2026-01-20
```

Expected outputs:

- repair manifest shard;
- before/after charts;
- quote envelope tables;
- validator summary;
- pilot readout.

### Phase 2 - Recent-Year Pilot

Run a broader pilot such as:

```text
2025-2026
```

Purpose:

- estimate defect rate;
- tune quote sufficiency and spread thresholds;
- find false positives;
- measure runtime and I/O.

### Phase 3 - Full Audit

Run the full 2005-2026 audit with workers and resume.

### Phase 4 - Consumer Integration

Make DAS/event scripts consume the official loader or manifest-backed
materialization.

## 19. Consumer Matrix Draft

Draft policy before formal consumption document:

| Consumer | Draft status | Requirement |
| --- | --- | --- |
| `event_engine` | allowed with flags | must preserve repair flags |
| `backtest_extended` | allowed with flags | must report repaired-minute exposure |
| `research_only` | allowed | must cite manifest version |
| `ml_flagged` | possible later | repair flags must be features or masks |
| `backtest_core` | not allowed initially | needs full audit and sensitivity |
| `ml_primary` | not allowed | quote-guarded is provisional |
| `execution_simulator` | prohibited | not executed trade truth |
| `rl_allowed` | prohibited | needs separate downstream contract |
| `live_downstream_candidate` | prohibited | historical repair only |
| `forensic_only` | allowed | raw and repaired views both visible |

## 20. Open Gates Before Work Can Be Called Complete

The workstream cannot be called `human_inspector_ready` until it has:

- contract stack;
- reproducible builder;
- pilot evidence;
- full or scoped audit evidence;
- visual inspector pack or explicit waiver;
- asset audit;
- data quality report;
- consumer integration proof or declared non-consumption state;
- changelog entry.

The data-quality verdict and foundations-completion status must stay separate.

Initial likely states:

```text
data_quality_verdict = provisional
foundations_completion_status = governance_pack_started
```

## 21. Future Supersession By Trades

When extended-hours trades become available, this layer should not be silently
overwritten.

Expected future path:

```text
ohlcv_1m_quote_guarded_v0_1
-> ohlcv_1m_trade_rebuilt_v0_1
```

The trade-rebuilt layer would have a different contract because it can
reconstruct executed OHLCV and VWAP under sale-condition policy.

Until then, quote-guarded remains a provisional price guardrail for research and
event detection, not execution truth.

## 22. Final Rule

The correct institutional reading is:

```text
Use quotes to guard impossible raw 1m OHLC bars now.
Preserve raw data unchanged.
Preserve repair flags downstream.
Do not claim exact executed OHLCV or VWAP until extended-hours trades exist.
Document every decision before the full audit runs.
```

