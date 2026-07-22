# Event Windows Table Dataset Contract `v0_1`

## 1. Dataset Identity

```yaml
dataset_id: event_windows_table_v0_1
logical_version: v0_1
domain: data_foundation_outputs
state_component_type: governed_event_window_input
source_event_dataset_id: halts_table_v0_1
materialization_scope: halts_intraday_lt1b_calendar_covered
promotion_state: provisional_validated_for_declared_scope
full_universe_claim: false
```

Physical target:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
```

## 2. Purpose

`event_windows_table_v0_1` gives TSIS a governed table of event boundaries.

It answers:

```text
For this governed source event, what windows are legal to use for pre-event
features, event response, same-session context and post-event outcomes?
```

It exists before broad microstructure/outcome/state materialization because
heavy tables must not invent their own event boundaries.

## 3. Source Lineage

Upstream governed outputs:

```text
halts_table_v0_1
instrument_master_v0_1
market_calendar_v0_1
```

Current source event filter:

```text
halts_table.valid_for_intraday_mask = true
and ticker has temporal instrument_master match
and halt_date is covered by market_calendar
```

Rows excluded from v0.1 must remain visible in the manifest as counts. They are
not deleted from upstream sources.

## 4. Scientific And Institutional Justification

Decision TSIS:

```text
Define event windows as a separate governed state component before building
features, labels, outcomes or ML/RL datasets.
```

Direct evidence:

- Offline RL datasets require clear state/action/reward transitions; mixing
  features and labels without explicit temporal boundaries creates leakage.
- Conservative Q-Learning and related offline RL work assume the dataset
  encodes historical transitions rather than retrospective feature shortcuts.
- Lopez de Prado's financial ML methodology requires event labeling and
  sampling to avoid leakage and overlapping-window distortions.
- DeepLOB and LOBFrame show that microstructure modeling is temporal; quote and
  trade features must be tied to explicit windows rather than arbitrary table
  joins.

Technical obligation:

```text
event_windows_table must separate pre-event feature windows from post-event
outcome windows and preserve source event lineage, calendar boundaries and
quality gates.
```

Open limitation:

```text
v0.1 covers halt-derived event windows only. It does not define news, offering,
filing, gap, momentum, short, regime or live-alert event windows.
```

## 5. Current Materialization

Expected output layout:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/
  event_windows_table_v0_1.parquet
  _event_windows_table_summary_v0_1.csv
  _event_windows_table_manifest_v0_1.json
```

Window roles:

- `prior_session_regular`
- `pre_event_30m`
- `event_to_resume_or_30m`
- `same_session_regular`
- `next_session_regular`

## 6. Allowed Consumers

Allowed:

- `event_engine`
- `microstructure_feature_builder`
- `outcome_builder`
- `data_quality_report`
- `forensic_review`
- `research_only`

Conditionally allowed:

- `backtest_extended`, with `valid_for_backtest_event_window_candidate`;
- `ml_flagged`, using only rows where
  `valid_for_ml_feature_candidate = true` as features;
- `outcome_research`, using only rows where
  `valid_for_outcome_window_candidate = true` as labels/outcomes.

Prohibited:

- `strategy_alpha`;
- `ml_primary` as a standalone training dataset;
- `rl_allowed` as a standalone RL dataset;
- `execution_simulator` as execution truth;
- treating v0.1 as all event families.

## 7. Leakage Policy

`valid_for_ml_feature_candidate = true` is allowed only when:

```text
leakage_safe_as_pre_event_feature = true
```

Post-event windows may be used for labels/outcomes, not pre-event features.

Consumers must not use `event_to_resume_or_30m` or `next_session_regular` as
pre-event model input.

## 8. Known Limitations

- Source family is halts only.
- Event source timestamps are historical source timestamps, not live
  `received_utc` timestamps.
- `event_to_resume_or_30m` may use a fixed fallback when no resume timestamp
  exists.
- Calendar coverage currently ends at the calendar materialization frontier.
- v0.1 is not an institutional `market_state` table.

## 9. Promotion Requirements

Before stronger promotion:

- add non-halt event sources;
- define source-specific arrival/as-of semantics;
- connect outcome labels in a separate table;
- connect broader microstructure features using this table as input;
- add visual/forensic examples for good/review/bad windows;
- run integrated tests with all Data Foundation outputs.

## 10. Change Policy

Version bump required when:

- window roles change;
- source event families expand;
- eligibility filters change;
- leakage gates change;
- calendar source changes;
- this table becomes an input to primary ML/RL datasets.
