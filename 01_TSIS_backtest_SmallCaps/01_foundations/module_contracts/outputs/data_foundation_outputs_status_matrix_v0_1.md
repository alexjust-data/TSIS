# Data Foundation Outputs Status Matrix v0.1

Reference date: 2026-06-27

Status: `operational_status_matrix`

Owner: `01_TSIS_backtest_SmallCaps / 01_foundations`

## 1. Role

This document records the current institutional state of the CAPA 1 Data
Foundation output tables.

It does not replace:

- `data_foundation_outputs_target_contract_v0_1.md`
- dataset-specific contracts;
- canonical schemas;
- validators;
- registry entries;
- consumption policies;
- materialization manifests;
- executable test evidence.

Its purpose is narrower:

```text
show what exists today,
show what each table can be used for today,
show what is still blocked,
and prevent agents from treating scoped or provisional outputs as institutional.
```

## 2. Sources Inspected

Filesystem roots:

```text
E:/TSIS/data/data_foundation_outputs/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/
C:/TSIS_Data/tests/test_runs/
```

Contract roots:

```text
01_foundations/module_contracts/outputs/
01_foundations/canonical_schemas/outputs/
01_foundations/contract_registry/dataset_contracts/
01_foundations/dataset_registry/outputs/
01_foundations/data_consumption_policies/
01_foundations/validators/outputs/
```

Mandatory interpretation documents:

```text
01_foundations/module_contracts/data_storage_topology_and_target_state.md
01_foundations/module_contracts/event_families_and_reference_inventory.md
01_foundations/module_contracts/price_semantics_and_adjustment_policy.md
01_foundations/module_contracts/price_views_registry.md
01_foundations/module_contracts/corporate_actions_adjustment_methodology.md
01_foundations/module_contracts/external_price_comparison_caveats.md
```

## 3. Status Vocabulary

`materialized`

The output exists physically under:

```text
E:/TSIS/data/data_foundation_outputs/
```

`validated_for_declared_scope`

The output has contract stack, materializer, manifest/summary and executable
tests that passed for the declared v0.1 scope. This does not automatically mean
full institutional coverage or unrestricted downstream use.

`scoped_pilot`

The output is useful only with explicit scope flags. It must not be presented as
full universe, ML/RL-ready, execution-ready or core-backtest-ready.

`seed_state_sample`

The output proves the computation path and misuse gates on a seed window. It is
not a trainable or institutional state component.

`controlled_candidate_not_promoted`

The output exists physically as a candidate under the governed output root, has
manifest/test evidence for a declared controlled scope, and is useful for
lineage/recompute/missingness diagnostics. It is not an official promoted
replacement and must not be used as primary ML/RL, execution or core-backtest
truth.

`not_materialized`

The target table is conceptually defined or expected, but no governed output
exists under `E:/TSIS/data/data_foundation_outputs/`.

## 4. Current Materialized Outputs

| Output | Rows | Parquet files | Scope | Test evidence | Current status | Primary allowed use today | Main blocker |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `instrument_master_v0_1` | 4,824 | 1 | LT1B universe identity snapshot/window | Seven-table rerun passed | `validated_for_declared_scope` | identity context, event/backtest/materialization scope with flags | not final lifecycle engine; no daily PTI market-cap reconstruction |
| `market_calendar_v0_1` | 5,283 | 1 | XNYS sessions, 2005-01-03 to 2025-12-31 | Seven-table rerun passed | `validated_for_declared_scope` | session calendar for event/backtest/materialization | not venue-specific liquidity calendar; no live future extension |
| `expected_data_calendar_v0_1` | 29,029,152 | 84 | expected rows by dataset family/year | Seven-table rerun passed | `validated_for_declared_scope` | coverage denominator and absence diagnostics | not physical presence; must be joined to actual validators |
| `corporate_actions_table_v0_1` | 104,757 | 1 | splits/dividends/ticker changes from reference/additional | Seven-table rerun passed | `validated_for_declared_scope` | corporate-action context, price-view support, event context | does not solve full economic continuity across ticker changes |
| `dataset_certification_matrix_v0_1` | 13 | 1 | family-level quality gates | Seven-table rerun passed | `validated_for_declared_scope` | family gate/mask for consumers | family-level only; not ticker/date row validation |
| `master_daily_table_v0_1` | 21,771,864 | 63 | daily rows x three price views | Seven-table rerun passed | `validated_for_declared_scope` | daily event context, outcome research, backtest core rows where flags allow | no full row-level audit labels; no execution/microstructure |
| `master_intraday_bar_table_v0_1` | 175,252 | 14 | `scoped_split_normalized_event_cases`; `full_universe_claim=false` | Seven-table rerun passed | `scoped_pilot` | scoped event research and backtest extended with flags | not full-universe 1m; backtest core rows = 0; not execution truth |
| `microstructure_features_table_v0_1` | 1 | 1 | `seed_event_window_smoke`; `full_universe_claim=false` | isolated rerun passed; 6-row candidate visual smoke evidence exists | `seed_state_sample` | schema/lineage/recompute proof for one event window | not ML/RL-ready, not core-backtest-ready, not execution-ready |
| `microstructure_features_table_v0_2_candidate_controlled_25_per_role` | 50 | 1 | halt event-window candidate; 25 rows per selected role; `full_universe_claim=false` | isolated candidate test passed | `controlled_candidate_not_promoted` | controlled candidate diagnostics for quote/trade lineage, missingness, recomputation and market-state design | quotes uses provisional `D:/quotes`; trades present only 24/50; not ML/RL-ready, not core-backtest-ready, not execution-ready |
| `market_state_table_v0_1_candidate_microstructure_halt_controlled` | 50 | 2 | controlled halt event-window state snapshots from microstructure v0.2 candidate; `full_universe_claim=false` | market/event state tests passed 2026-06-29 | `controlled_candidate_not_promoted` | event-context candidate and state-builder integration proof | inherits provisional `D:/quotes` lineage; not ML/RL-ready, not backtest-core, not execution truth, not official `market_state_table_v0_1` |
| `event_state_table_v0_1_candidate_microstructure_halt_controlled` | 50 | 2 | controlled halt event-window event states linked to market-state candidate; 25 pre-event + 25 post-event-review rows; `full_universe_claim=false` | market/event state tests passed 2026-06-29 | `controlled_candidate_not_promoted` | event-state integration proof and pattern-discovery candidate surface | inherits provisional market/microstructure lineage; labels/outcomes/rewards absent; not ML/RL-ready, not backtest-core, not execution truth |
| `halts_table_v0_1` | 133,116 | 1 | Nasdaq/NYSE halts and SEC suspensions from `halts_v0_1` | isolated rerun passed | `validated_for_declared_scope` | event interruption context, halt masks, date/intraday halt state | no decision-time availability model, no live latency contract, review/bad rows preserved |
| `event_windows_table_v0_1` | 214,112 | 1 | halt-derived event windows for LT1B/calendar-covered intraday halt events | isolated rerun passed | `validated_for_declared_scope` | event-window boundaries, pre-event feature windows, outcome-window candidates | halts only; not all event families; not primary ML/RL/execution truth |
| `outcomes_table_v0_1` | 128,388 | 1 | next-session daily outcomes for halt-derived event windows x three daily price views | isolated rerun passed | `validated_for_declared_scope` | daily post-event labels/outcome research with feature/label separation | daily labels only; not intraday execution outcome, not RL reward, not all event families |
| `fundamentals_asof_table_v0_1` | 621,756 | 51 | additional financial statement rows with `filing_date` as `as_of_date`; ratios and standalone `financial_v0_1` excluded | isolated rerun passed | `validated_for_declared_scope` | filing-date-aware fundamental context after explicit as-of join | not a latest-before-event snapshot, not ratios/market-cap/float authority, not direct ML/RL table |
| `news_context_table_v0_1` | 287,138 | 9 | additional news rows with `published_utc` as `as_of_utc`; ticker attribution preserved | isolated rerun passed | `validated_for_declared_scope` | catalyst/news context after explicit as-of join | not proof of causality, not live received-latency alert stream, not direct ML/RL table |
| `short_context_table_v0_1` | 7,145,337 | 32 | source-scoped short interest/short volume from `short` and FINRA `short_review`; no borrow/SSR | isolated rerun passed | `validated_for_declared_scope` | short pressure/crowding/squeeze context after explicit source selection and as-of/lag join | not borrow, not SSR, not intraday tape, not direct ML/RL table |
| `regime_context_table_v0_1` | 154,692 | 25 | session-level regime proxy context from `regime_indicators` minute bars; `day.parquet` blocked | isolated rerun passed | `validated_for_declared_scope` | market/regime context after explicit as-of join | not same-session intraday causal state, not execution truth, not direct ML/RL table |

## 5. Test Evidence State

Latest successful evidence for the first seven tables:

```text
C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
status = passed
tests = 29
failed = 0
skipped = 0
```

Latest successful isolated evidence for `microstructure_features_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
status = passed
tests = 3
failed = 0
skipped = 0
```

Latest candidate manifest/materializer/visual smoke evidence for
`microstructure_features_table_v0_2_candidate`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
status = passed
tests = 5
failed = 0
skipped = 0
candidate_rows = 6
official_dataset_created = false
visual_readout = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_visual_readout_v0_1.md
notebook = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/notebooks/data_foundation_outputs/microstructure_candidate_visual_evidence_v0_1.ipynb
visual_case_count = 6
```

Latest controlled materialized candidate evidence for
`microstructure_features_table_v0_2_candidate`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_v0_2_controlled_candidate/
status = passed
tests = 5
failed = 0
skipped = 0
dataset_id = microstructure_features_table_v0_2_candidate
materialization_scope = halt_event_windows_microstructure_candidate_controlled_25_per_role
rows = 50
tickers = 9
windows = 50
quotes_file_present_rows = 50
trades_file_present_rows = 24
review_partial_source_rows = 26
pass_seed_window_rows = 24
hard_fail_count = 0
duplicate_key_groups = 0
full_universe_claim_rows = 0
execution_sim_candidate_rows = 0
backtest_core_microstructure_candidate_rows = 0
output_tree_sha256 = a3d418b06d8c4bd200d51d8eb9c6d888664c1af86ab3dd37c80d48ff2397d128
source_quotes_root_state = provisional_d_legacy_recovery_root_pending_e_parity
source_trades_root_state = official_e_raw_root
visual_readout = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_controlled_visual_readout_v0_2.md
visual_manifest = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/microstructure_candidate_controlled_visual_manifest_v0_2.json
visual_case_count = 50
visual_cached_quote_files_read = 9
visual_cached_trade_files_read = 5
```

This candidate validates a controlled materialization and sample recomputation
from raw quote/trade files. It does not override the official v0.1 seed table,
does not resolve E-root quotes parity and does not grant ML/RL, execution or
core-backtest readiness.

Latest controlled materialized candidate evidence for
`market_state_table_v0_1_candidate`:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/
manifest = E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
summary = E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv
build_run_id = market_state_table_v0_1_candidate_20260629T194351Z
materialization_scope = halt_event_window_microstructure_controlled_candidate
rows = 50
tickers = 9
event_windows = 50
parquet_files = 2
valid_for_event_context_candidate_rows = 50
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
full_universe_claim_rows = 0
duplicate_state_id_rows = 0
state_quality_counts = {"state_review_microstructure_seed_only":50}
output_tree_sha256 = 05abf763bca2b97bc6d61d8d2c8e99bf7a23ee7ba9ec05aa8fc1c00bdf488abd
```

This candidate composes controlled halt event-window microstructure into
state-snapshot rows. It intentionally preserves the provisional `D:/quotes`
lineage inherited from the microstructure component and does not make the
official `market_state_table_v0_1` institutional.

Latest controlled materialized candidate evidence for
`event_state_table_v0_1_candidate`:

```text
E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/
manifest = E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
summary = E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv
build_run_id = event_state_table_v0_1_candidate_20260629T194750Z
materialization_scope = halt_event_window_event_state_controlled_candidate
rows = 50
tickers = 9
event_windows = 50
parquet_files = 2
pre_event_rows = 25
post_event_review_rows = 25
valid_for_pattern_discovery_rows = 50
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
full_universe_claim_rows = 0
duplicate_state_id_rows = 0
state_quality_counts = {"event_state_review_microstructure_seed_only":50}
output_tree_sha256 = ca19b6d65277be718e09ffa88bd2d5b380ed4ca5c9abf681e0b27624b4e60d37
```

This candidate links the controlled market-state rows to halt event windows.
It carries no inline outcomes, labels, rewards, actions, fills, PnL, strategy
signals or execution truth. Pre-event rows are context candidates only; direct
ML/RL/backtest/execution gates remain false.

Latest successful isolated evidence for `halts_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful isolated evidence for `event_windows_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful isolated evidence for `outcomes_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful isolated evidence for `fundamentals_asof_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_fundamentals_asof_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful isolated evidence for `news_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_news_context_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful isolated evidence for `short_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful isolated evidence for `regime_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful market/event state fixture-loop evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
status = passed
tests = 14
failed = 0
skipped = 0
```

Latest successful 1m split-normalized manifest-builder regression evidence
for the next `master_intraday_bar_table` wider-scope loop:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_1m_split_manifest_builder_v0_1/
status = passed
tests = 2
failed = 0
skipped = 0
```

Latest successful split-affected smoke manifest:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_153012/
rows = 100
tickers = 1
scan_strategy = split_tickers_then_partition_direct
official_dataset_created = false
```

Latest successful earlier contract-skeleton evidence for `market_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_state_table_contract_skeleton_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Latest successful earlier contract-skeleton evidence for `event_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_event_state_table_contract_skeleton_v0_1/
status = passed
tests = 4
failed = 0
skipped = 0
```

Important caveat:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_eight_tables_v0_1/
status = timeout_aborted
exit_status = 124
timeout_seconds = 304
```

The eight-table full suite did not finish within the command timeout. No failed
assertion was captured before timeout, but this run cannot be cited as a passed
integrated suite.

Required next test action:

```text
rerun the fifteen-table suite with longer timeout or split by table groups,
then store evidence under C:/TSIS_Data/tests/test_runs/YYYY-MM-DD/<run_id>/
```

## 6. Contract Stack Coverage

All fifteen materialized outputs currently have:

- dataset contract under `contract_registry/dataset_contracts/`;
- canonical schema under `canonical_schemas/outputs/`;
- registry entry under `dataset_registry/outputs/`;
- consumption policy under `data_consumption_policies/`;
- validator document under `validators/outputs/`;
- materializer under `scripts/`;
- pytest contract test under `tests/data_foundation_outputs/`.

Known exception in interpretation:

`microstructure_features_table_v0_1` has the full contract stack, but its
contract stack explicitly blocks primary ML/RL training, core backtesting and
execution simulation because its current materialization is one seed window.

`market_state_table_v0_1` and `event_state_table_v0_1` have contract stack
skeletons, deterministic fixtures, fixture-only builder configs, executable
fixture builders and adversarial leakage tests. They still have no official
parquet, official manifest or official summary. Their registry entries are
intentionally marked `contract_defined_not_materialized`.

`daily_scanner_candidates_table_v0_1` now has its target contract stack,
scanner-framework contract, two versioned scanner configs, historical replay
builder, deterministic fixture test and a controlled replay evidence pack. It
still has no official E-root parquet, official manifest or official summary. It
is the candidate-generation layer for in-play discovery, not a replacement for
`market_state_table`.

The forward `v0.2` scanner model is also implemented as a controlled builder
and deterministic fixture test. It replaces the idea of two independent scanner
universes with one base denominator plus profile flags:

```text
base_in_play_universe_scanner_v0_2
trade_station_like_profile_v0_2
relative_volume_profile_v0_2
percent_change_profile_v0_2
dollar_volume_tradability_profile_v0_2
das_research_profile_v0_2
```

`v0.2` is not an official E-root materialization. It is the current
implementation path for future wider scanner replays.

Latest controlled replay evidence:

```text
run_id: daily_scanner_candidates_replay_20250102_20250110_v0_2
root: C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2/
rows: 15323
selected_any_profile_rows: 4023
selected_trade_station_like_profile_rows: 150
selected_das_research_profile_rows: 2472
selected_below_500k_volume_rows: 3177
duplicate_key_groups: 0
float_filter_used_rows: 0
ml_feature_candidate_rows: 0
rl_state_candidate_rows: 0
```

Governed historical v0.1 scanner definitions:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

## 7. Non-Materialized Target Outputs

The following target outputs are still not governed materializations under
`E:/TSIS/data/data_foundation_outputs/`:

| Target output | Current state | Required before materialization |
| --- | --- | --- |
| `data_quality_report` | documentation/evidence exists under `01_foundations/data_quality_report/`, but no governed E-root output table exists | decide if it is a report folder, a table, or both; define schema/manifest if table |
| `daily_scanner_candidates_table` | v0.1 builder/replay evidence exists under `C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/`; v0.2 base-universe-plus-profiles builder and fixture test exist; official E-root materialization does not exist | implement full validator suite, decide wider replay/promotion policy, preserve scanner rows as candidate lineage only, obey `market_state_coverage_and_lookback_policy_v0_1`; cannot be treated as complete universe, final market state, ML/RL feature table or strategy signal |
| `master_intraday_bar_table_v0_2_candidate_quote_guarded` | candidate contract and config defined; no parquet materialization exists | wait for final `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/` repair manifest and validation report; storage model is raw `ohlcv_1m` plus repair-manifest overlay, not a full corrected parquet tree; keep `D:/quotes` only as provisional candidate lineage; builder must consume a manifest/partition list, not blind recursive file discovery |
| `real_time_corporate_event_alerts_table` | not materialized | define vendor/source model, latency semantics, SEC/newswire/DAS/vendor lineage, and live-vs-backfill contract |
| `short_sale_constraints_table` | target contract and acquisition runbook defined, not materialized | derive/validate SSR proxy or acquire official SSR; connect DAS/SageTrader or broker/vendor feed for forward capture; acquire broker/vendor historical borrow/locate/availability if 20-year historical execution feasibility is required; define account/broker scope and as-of/latency semantics |
| `market_state_table` / `event_state_table` | contract stack plus deterministic fixture loop passed, not materialized | expand to controlled multi-component sample; obey `market_state_coverage_and_lookback_policy_v0_1`; `D:/quotes` may be used only as provisional candidate lineage with `quotes_root_state=provisional_d_legacy_recovery_root_pending_e_parity`; add recomputation/manifest/coverage/lookback gates; promote only after leakage/adversarial tests and E-root parity/rebuild requirements pass |

## 8. Current Readiness By Consumer

| Consumer | Ready outputs | Not ready / restricted |
| --- | --- | --- |
| `event_engine` | instrument, calendar, expected calendar, corporate actions, dataset gates, daily context, halt context/masks, halt-derived event windows, filing-date-aware fundamentals, published-utc-aware news, short context, regime context and controlled daily scanner candidate replay after explicit source/as-of/lag selection | official daily scanner candidates materialization, final market state composition, live alerts, non-halt event families and short-sale constraints still missing |
| `backtest_core` | `master_daily_table_v0_1` where row flags allow; instrument/calendar/context tables, halt exclusions/interruptions and halt-derived event windows where timestamp legality allows | `master_intraday_bar_table_v0_1` has core candidate rows = 0; microstructure seed is prohibited |
| `backtest_extended` | daily table, scoped intraday table, halts, event windows, next-session daily outcomes, fundamentals/news/short/regime context with flags and legal cutoffs | microstructure table is only seed proof; no intraday execution outcomes; short-sale feasibility is not institutional until `short_sale_constraints_table` exists |
| `ml_primary` | daily table where price view/flags and leakage policy allow; `outcomes_table_v0_1` only as labels where `valid_for_ml_label_candidate=true` | event windows are boundaries only; microstructure, intraday scoped pilot and halts context are not primary features; fundamentals/news/short/regime still require external as-of/state builder; short-sale constraints missing |
| `ml_flagged` | instrument/corporate/dataset gates/daily/scoped intraday/halts/event windows/outcomes/fundamentals/news/short/regime with explicit flags and as-of selection | no final event-state dataset; outcome table is daily halt-derived labels only; context rows are not state snapshots; no borrow/locate/SSR state yet |
| `rl_allowed` | none from current output set as primary RL dataset | needs state/action/reward schema, simulator/replay and OOD guards |
| `execution_simulator` | none as execution truth; calendar/instrument only as context | needs quotes/trades/replay-grade microstructure, execution policies and short-sale constraints for short strategies |
| `live_downstream_candidate` | none as live authority | needs live contracts, latency, logging and vendor lineage |

## 9. Scientific Justification Gate

Every future promotion must satisfy the root TSIS rule:

```text
Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta
```

For Data Foundation outputs, this means:

- a table is not enough because it exists physically;
- a test is not enough because it passes locally;
- a model is not ready because columns exist;
- ML/RL readiness requires declared coverage, legal cutoffs, OOD guards,
  recomputation tests, labels separated from features, and evaluator boundaries;
- execution readiness requires raw microstructure/replay semantics, not adjusted
  or aggregated price views.

The current scientific basis for the table/state architecture lives in:

```text
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
C:/TSIS_Data/PROJECT_RULES.md
C:/TSIS_Data/RESEARCH_PHILOSOPHY.md
```

## 10. Immediate Next Actions

1. Rerun or split the fifteen-table test suite so an integrated pass exists for
   all current outputs.
2. Keep `short_sale_constraints_table` blocked until SSR and borrow/locate/
   availability sources are acquired or explicitly derived with validation.
   Use
   `01_foundations/module_contracts/outputs/short_sale_constraints_data_acquisition_runbook_v0_1.md`
   for DAS/live capture and historical broker/vendor intake.
3. Decide the next table by dependency, not convenience.
4. Expand the scoped intraday and microstructure foundations before promoting
   official state tables.
   For `master_intraday_bar_table`, the next quote-guarded path is now:
   `master_intraday_bar_table_v0_2_candidate_quote_guarded`. It is contract-
   defined only and must remain blocked until the final quote-guarded repair
   manifest and validation report exist under
   `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/`.
5. For the controlled state-table loop, `D:/quotes` is accepted only as
   provisional quote lineage while target official
   `E:/TSIS/data/quotes_` parity/audit remains incomplete.
   `E:/TSIS/data/quotes` is treated as incomplete/legacy E-root, not the
   official target. Any candidate inheriting this source must carry
   `requires_rebuild_after_e_quotes_parity=true` and must not be marked ready
   for ML/RL primary training, backtest core or execution simulation.
6. Do not build state tables as ticker-day-only snapshots. Future state-table
   candidates must obey
   `01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md`:
   full-history compact context, daily in-play candidates, governed event
   windows and explicit lookback policies.
7. Use `daily_scanner_candidates_table` as candidate evidence only. The v0.1
   replay compared `trade_station_like_scanner_v0_1` against
   `broad_in_play_discovery_scanner_v0_1`. The v0.2 implementation replaces
   that forward model with `base_in_play_universe_scanner_v0_2` plus governed
   profile flags. Neither version is official E-root materialization, live
   authority or a direct ML/RL table.

Dependency order:

```text
1. daily_scanner_candidates_table v0.2 wider replay / validator promotion decision
2. master_intraday_bar_table wider/full-scope materialization plan
   - quote-guarded subpath:
     `01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md`
3. microstructure_features_table multi-window/multi-event materialization plan
4. market_state_table controlled real sample
5. event_state_table controlled real sample
6. short_sale_constraints_table when SSR/borrow/locate sources exist
7. real_time_corporate_event_alerts_table when live/vendor latency semantics exist
```

The executable builder and evidence for item 1 are now:

```text
scripts/materialize_daily_scanner_candidates_table_v0_2.py
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
scripts/materialize_daily_scanner_candidates_table.py
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

The executable plan for item 2 is now:

```text
01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md
```

The executable plan for item 3 is now:

```text
01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md
```

Rationale:

```text
market_state_table and event_state_table must not be promoted on top of weak
intraday/microstructure components.
```

Do not start full-universe materialization for all tables at once. Each table
must first have:

- official source root or documented parity;
- declared scope and denominator;
- manifest policy;
- recomputation test from raw/source files;
- quality gates;
- explicit `full_universe_claim`;
- executable test evidence;
- changelog, registry and Graphify queue updates.

5. Recommended next implementation work:

```text
master_intraday_bar_table wider/full-scope materialization plan, then
microstructure_features_table multi-window/multi-event materialization plan
```

Reason:

- `master_intraday_bar_table_v0_1` is scoped and
  `microstructure_features_table_v0_1` is seed-only;
- the `master_intraday_bar_table` expansion loop now has a dedicated plan
  requiring split-safe 1m smoke, denominator manifest, candidate-only output,
  builder parameterization, tests and promotion gates before any full-universe
  claim;
- the `microstructure_features_table` expansion loop now has a dedicated plan
  requiring governed event-window denominator, explicit quotes root state,
  candidate-only output, builder parameterization, recomputation tests and
  visual/forensic evidence before any broader state claim;
- the first microstructure expansion substep now has executable evidence:
  `scripts/build_microstructure_candidate_window_manifest.py` builds a
  candidate window manifest from `event_windows_table_v0_1`; the existing
  materializer also supports a candidate path and produced a 6-row test
  artifact with raw quote/trade reconciliation; tests passed
  under
  `C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/`;
- fundamentals, historical news, source-scoped short context and session-level
  regime context exist as as-of/lag-aware context rows;
- `01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md`
  now defines what state composition means and what is prohibited;
- schema contracts, dataset contracts, consumption policies, validators,
  registry target entries, builder skeletons, deterministic fixture configs,
  fixture-only sample builders and adversarial tests now define the pre-
  materialization stack;
- `short_sale_constraints_table` is contract-defined with an acquisition
  runbook, but remains blocked by SSR/broker/vendor source acquisition;
- `real_time_corporate_event_alerts_table` remains a separate live-ingestion
  dependency blocked by vendor/feed/latency semantics;
- the next architectural need is stronger intraday/microstructure component
  coverage before official state materialization.

## 11. Final Status

Current state:

```text
15 official v0.1 outputs materialized.
1 controlled v0.2 candidate microstructure output materialized but not promoted.
7 outputs have integrated passed evidence as a group.
8 outputs have isolated passed evidence.
0 outputs should be called final institutional market_state.
1 market/event state contract stack plus deterministic fixture loop defines the future boundary.
2 official outputs are explicitly scoped/seed and must not be overpromoted.
1 candidate output is explicitly controlled/not-promoted and must not be overpromoted.
several target context/state outputs remain unmaterialized.
```

Therefore:

```text
Data Foundation outputs are progressing correctly,
but the CAPA 1 output layer is not complete and must not be described as fully
institutionalized end-to-end.
```
