# Changelog del Modulo 01

Este changelog registra cambios institucionales y semanticamente relevantes para:

- `01_TSIS_backtest_SmallCaps`

No duplica el historial de Git.
Existe para preservar memoria arquitectonica y metodologica del modulo.

## v0.4.78 - Master daily table initial materialization

### Added

- `01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/master_daily_table_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/master_daily_table_registry_entry.yaml`
- `01_foundations/validators/outputs/master_daily_table_validators.md`
- `scripts/materialize_master_daily_table.py`
- `tests/data_foundation_outputs/test_master_daily_table_contract.py`

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/validators/README.md`

### Materialized

```text
dataset_id = master_daily_table_v0_1
path = E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
layout = partitioned parquet dataset by year/price_view
rows = 21771864
expected_daily_rows = 7257288
price_views = daily_raw, split_normalized, adjusted
rows_per_price_view = 7257288
data_present_rows = 19782153
missing_expected_data_rows = 1989711
selected_price_hard_invalid_rows = 0
negative_volume_rows = 0
backtest_core_row_candidate_rows = 19782153
rows_with_corporate_action = 92979
parquet_file_count = 63
output_tree_sha256 = 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e
build_run_id = master_daily_table_v0_1_20260622T161747Z
hard_fail_count = 0
```

### Test Evidence

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_six_tables_v0_1/
tests = 24
passed = 24
failed = 0
skipped = 0
```

### Notes

`master_daily_table_v0_1` is materialized at
`instrument_id + ticker + session_date + price_view` grain. It preserves three
explicit price views: `daily_raw`, `split_normalized` and `adjusted`. v0.1
keeps missing expected rows for coverage accounting, exposes daily context
metrics and corporate-action flags, and does not yet join fundamentals, news,
short, halts or regime context.

## v0.4.77 - Dataset certification matrix initial materialization

### Added

- `01_foundations/canonical_schemas/outputs/dataset_certification_matrix_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/dataset_certification_matrix_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/dataset_certification_matrix_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/dataset_certification_matrix_registry_entry.yaml`
- `01_foundations/validators/outputs/dataset_certification_matrix_validators.md`
- `01_foundations/validators/daily/daily_adjusted_validators.md`
- `01_foundations/validators/ohlcv_1m/ohlcv_1m_split_normalized_validators.md`
- `scripts/materialize_dataset_certification_matrix.py`
- `tests/data_foundation_outputs/test_dataset_certification_matrix_contract.py`

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/validators/README.md`

### Materialized

```text
dataset_id = dataset_certification_matrix_v0_1
path = E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
rows = 13
family_count = 13
human_inspector_ready_count = 13
visual_casepack_complete_count = 13
blocked_from_backtest_core_count = 2
scoped_only_count = 5
data_quality_verdict_counts = blocked_by_data_defect: 2, complete_scoped: 5, usable_for_declared_scope: 6
foundations_completion_status_counts = human_inspector_ready: 9, human_inspector_ready_scoped: 4
visual_inspection_status_counts = visual_complete: 10, visual_complete_scoped: 3
build_run_id = dataset_certification_matrix_v0_1_20260622T154116Z
output_sha256 = e7803e3ec58cfb92c1313efc09bdd3a015800c4680437e4567a0174b257f1fb0
source_family_status_matrix_sha256 = c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35
hard_fail_count = 0
```

### Test Evidence

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_five_tables_v0_1/
tests = 20
passed = 20
failed = 0
skipped = 0
```

### Notes

`dataset_certification_matrix_v0_1` materializes the family-level gates from
`family_status_matrix_v0_1.md`. It verifies physical roots, quality reports,
inspection dossiers, schemas, contracts, registries, policies, validators and
visual evidence. It is a gate/evidence table, not market data and not a
row-level validator.

## v0.4.76 - Corporate actions table initial materialization

### Added

- `01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/corporate_actions_table_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/corporate_actions_table_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/corporate_actions_table_registry_entry.yaml`
- `01_foundations/validators/outputs/corporate_actions_table_validators.md`
- `scripts/materialize_corporate_actions_table.py`
- `tests/data_foundation_outputs/test_corporate_actions_table_contract.py`

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/validators/README.md`

### Materialized

```text
dataset_id = corporate_actions_table_v0_1
path = E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
rows = 104757
tickers = 3621
instrument_ids = 3497
action_type_counts = dividend: 92033, split: 6630, ticker_change: 6094
source_system_counts = additional: 52490, reference: 52267
first_action_date = 1969-12-31
last_action_date = 2027-06-15
build_run_id = corporate_actions_table_v0_1_20260622T144845Z
output_sha256 = 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
hard_fail_count = 0
duplicate_corporate_action_id_count = 0
invalid_split_terms_count = 0
negative_dividend_amount_count = 0
within_instrument_valid_window_false_count = 39525
cross_source_overlap_groups = 51336
```

### Test Evidence

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_four_tables_v0_1/
tests = 16
passed = 16
failed = 0
skipped = 0
```

### Notes

`corporate_actions_table_v0_1` preserves `reference` as primary source and
`additional` as secondary/reconciliation source. Empty placeholder source rows
are excluded. The table provides corporate-action context and adjustment
lineage; it does not solve full economic continuity across ticker changes and
does not output adjusted prices.

## v0.4.75 - Expected data calendar initial materialization

### Added

- `01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/expected_data_calendar_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/expected_data_calendar_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml`
- `01_foundations/validators/outputs/expected_data_calendar_validators.md`
- `scripts/materialize_expected_data_calendar.py`
- `tests/data_foundation_outputs/test_expected_data_calendar_contract.py`

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/validators/README.md`

### Materialized

```text
dataset_id = expected_data_calendar_v0_1
path = E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1
layout = partitioned parquet dataset by dataset_family/year
rows = 29029152
dataset_families = daily_raw, ohlcv_1m_raw, quotes_raw, trades_raw
rows_per_family = 7257288
tickers = 4824
first_session = 2005-01-03
last_session = 2025-12-31
parquet_file_count = 84
tree_sha256 = 1c7571cdcefc1ffd3f0f6cda921d32d64dee33cc41c3676809686c1bc575a57f
build_run_id = expected_data_calendar_v0_1_20260622T141019Z
hard_fail_count = 0
duplicate_key_groups = 0
invalid_window_count = 0
```

### Test Evidence

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_expected_data_calendar_v0_1/
tests = 12
passed = 12
failed = 0
skipped = 0
```

### Notes

`expected_data_calendar_v0_1` is a coverage expectation denominator. It
declares expected family/ticker/session rows from `instrument_master_v0_1` and
`market_calendar_v0_1`; it does not measure physical presence or data quality.

## v0.4.74 - Test runtime ignore protections

### Changed

- `C:/TSIS_Data/.gitignore`
- `C:/TSIS_Data/.graphifyignore`

### Notes

Git and Graphify now exclude dated test runtime evidence under
`C:/TSIS_Data/tests/test_runs/*/`, generated test `artifacts/`, junit XML files,
pytest logs and captured pytest output.

README contracts and executable test code remain visible for Git and Graphify.

## v0.4.73 - Data Foundation output contract tests

### Added

- `tests/conftest.py`
- `tests/_helpers/__init__.py`
- `tests/_helpers/data_foundation.py`
- `tests/data_foundation_outputs/test_instrument_master_contract.py`
- `tests/data_foundation_outputs/test_market_calendar_contract.py`

### Test Evidence

```text
C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_v0_1/
```

Generated artifacts:

- `metadata.json`
- `summary.md`
- `pytest_output.txt`
- `junit.xml`
- `artifacts/instrument_master_manifest_check.json`
- `artifacts/instrument_master_source_reconciliation.json`
- `artifacts/market_calendar_manifest_check.json`
- `artifacts/market_calendar_source_reconciliation.json`

### Result

```text
tests = 8
passed = 8
failed = 0
skipped = 0
```

### Notes

The pytest harness now creates dated institutional test-run evidence under
`C:/TSIS_Data/tests/test_runs/`. The first executable Data Foundation output
tests validate manifest/hash integrity, contract links, schema/lineage,
contractual hard gates and basic source reconciliation for
`instrument_master_v0_1` and `market_calendar_v0_1`.

## v0.4.72 - Data root and test artifact topology clarification

### Added

- Root test artifact folders:
  - `C:/TSIS_Data/tests/test_runs/`
  - `C:/TSIS_Data/tests/fixtures/`
  - `C:/TSIS_Data/tests/third_party_evidence/`

### Changed

- `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
- `C:/TSIS_Data/tests/README.md`

### Notes

The storage topology now distinguishes:

- `E:/TSIS/data/` as the active preferred data plane;
- `E:/TSIS/data/data_foundation_outputs/` as the governed CAPA 1 table output
  root;
- `C:/TSIS_Data/tests/test_runs/` as the root for dated test execution outputs;
- `C:/TSIS_Data/tests/fixtures/` as the root for small deterministic fixtures;
- `C:/TSIS_Data/tests/third_party_evidence/` as the root for cached external
  evidence;
- `C:/TSIS_Data/data/` as legacy/quarantine until a migration audit proves what
  can be removed.

No deletion of legacy data was performed.

## v0.4.71 - SmallCaps test topology scaffold

### Added

- `tests/README.md`
- `tests/data_foundation_outputs/README.md`
- `tests/foundations/README.md`
- `tests/pipelines/README.md`
- `tests/research/README.md`
- `tests/event_engine/README.md`
- `tests/strategy_engine/README.md`
- `tests/execution/README.md`
- `tests/rl_preparation/README.md`

### Notes

The module now has an explicit test topology for Data Foundation outputs,
foundations governance, pipelines, research promotion, event semantics,
strategy boundaries, execution realism and offline RL preparation.

No executable validators were added in this entry. The scaffold defines where
future tests must live and the minimum evidence expected for institutional
table validation: schema contract, manifest/hash, source reconciliation,
third-party evidence and adversarial/mutation checks.

## v0.4.70 - Market calendar initial materialization

### Added

- `01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/market_calendar_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml`
- `01_foundations/validators/outputs/market_calendar_validators.md`
- `scripts/materialize_market_calendar.py`

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/validators/README.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Materialized

```text
dataset_id = market_calendar_v0_1
path = E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
rows = 5283
calendar = XNYS
timezone = America/New_York
first_session = 2005-01-03
last_session = 2025-12-31
early_close_sessions = 45
build_run_id = market_calendar_v0_1_20260622T072422Z
source_parquet_sha256 = 8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228
output_sha256 = 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5
hard_fail_count = 0
duplicate_session_count = 0
```

### Notes

This is the second compact CAPA 1 output table materialized under the common
landing root. It derives from the local TSIS official calendar candidate built
with `exchange_calendars` (`XNYS`, `America/New_York`) and normalizes types plus
lineage for downstream consumption.

## v0.4.69 - Instrument master initial materialization

### Added

- `01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/instrument_master_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml`
- `01_foundations/validators/outputs/instrument_master_validators.md`
- `scripts/materialize_instrument_master.py`

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/validators/README.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Materialized

```text
dataset_id = instrument_master_v0_1
path = E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
rows = 4824
tickers = 4824
build_run_id = instrument_master_v0_1_20260621T145725Z
sha256 = 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
hard_fail_count = 0
duplicate_ticker_count = 0
```

### Notes

This is the first compact CAPA 1 output table materialized under the common
landing root.

It is derived from `reference_v0_1` and `lt1b_universe_v0_1`. Its current
grain is one row per ticker in the `<1B>` operational universe. It flags ticker
change risk but does not resolve final economic continuity or daily fully
point-in-time market-cap membership.

## v0.4.68 - Data Foundation outputs landing root

### Changed

- `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml`
- `01_foundations/validators/outputs/instrument_master_validators.md`
- `scripts/materialize_instrument_master.py`

### Notes

Defined the common physical landing root for governed CAPA 1 outputs:

```text
E:/TSIS/data/data_foundation_outputs/
```

Future Data Foundation output tables must be materialized below this root
instead of being created as loose siblings of raw/source folders such as
`reference`, `ohlcv_daily`, `quotes` or `trades`.

`raw_alert_log` and comparable append-only live ingestion logs are explicitly
excluded from this clean-output root and should live under a separate ingestion
root, for example:

```text
E:/TSIS/data/live_ingestion/raw_alert_log/
```

## v0.4.67 - Real-time corporate event alerts contract gap

### Changed

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/module_contracts/README.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

Added `real_time_corporate_event_alerts_table` to the CAPA 1 outputs contract.

This records that TSIS currently has historical/contextual news, but does not
yet have a governed low-latency alert stream for offerings, private placements,
warrants, 424B filings, 8-K/6-K filings, reverse splits or similar corporate
events that can move smallcaps within seconds.

The contract now distinguishes:

```text
historical/contextual news
SEC filing/submissions monitoring
low-latency newswire/vendor alerts
received_utc latency measurement
```

It also records the DAS Trader / NewsWare investigation note: DAS publicly
advertises real-time streaming news from NewsWare, but public DAS API
documentation is not sufficient evidence that DAS Trader Pro API exposes that
news stream for governed ingestion. Direct NewsWare API evaluation is the
preferred institutional route unless DAS provides certified API documentation.

and requires this table to be consumed by Event Engine and Strategy Research as
a risk/event input, not as a price source.

## v0.4.66 - Data Foundation outputs target contract

### Added

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`

### Changed

- `01_foundations/module_contracts/README.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

Formalized the CAPA 1 output target contract for future agents.

The contract explains how `instrument_master`, `market_calendar`,
`corporate_actions_table`, `master_daily_table`,
`master_intraday_bar_table`, microstructure/context sidecars,
`dataset_certification_matrix`, and `data_quality_report` work together when an
event is evaluated.

It also records that the local `market_calendar_official_XNYS_20050101_20251231`
artifact is reproducible byte-for-byte with:

```text
scripts/agent05_build_market_calendar_official.py
exchange_calendars 4.13.1
calendar = XNYS
timezone = America/New_York
sha256 = 8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228
```

External contrast sources documented in the contract:

```text
NYSE Holidays & Trading Hours
Nasdaq Stock Market Holiday Schedule
exchange_calendars project source
```

## v0.4.65 - Aggregated visual inspection dossiers

### Added

- `01_foundations/data_quality_report/inspection_visual_dossier/quotes_inspection_visual_dossier_v0_1.md`
- `01_foundations/data_quality_report/inspection_visual_dossier/trades_inspection_visual_dossier_v0_1.md`

### Changed

- `01_foundations/data_quality_report/README.md`

### Notes

Created one consolidated visual-inspection dossier per family for `quotes` and
`trades`.

Each dossier preserves the source report text and source image content, places a
collapsible navigation menu below `Documentos fuente`, groups that menu by
source document and parent heading hierarchy, uses each source document's
original title as the parent menu label, preserves that same original title as
the visible section heading in the body, adds the source path directly below
that title, and rebases only local relative paths inside the generated
aggregate files so the original images render from the new
`data_quality_report/inspection_visual_dossier/` location.

Validation:

```text
quotes images = 611
quotes missing_images = 0
trades images = 495
trades missing_images = 0
```

## v0.4.64 - Graphify homogeneous extraction remediation registered

### Changed

- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

The limitation in `foundations_authority_20260620` is now registered as explicit
pending work, not only as a caveat in the manifest.

Current state:

```text
graph materialized = yes
graph valid JSON / consultable = yes
root graph = no, by protocol
fully homogeneous Graphify semantic extraction = no
institutional final without caveat = no
```

Required remediation:

```text
Re-extract chunks 13-16 using the same worker semantic-extraction standard as
chunks 01-12, splitting them into smaller chunks if needed.
Regenerate foundations_authority_graph as a new dated leaf.
Update BUILD_MANIFEST.md, GRAPHIFY_REFRESH_QUEUE.md, README.md and CHANGELOG.md.
Remove the limitation only after all chunks have homogeneous semantic extraction
evidence.
```

The remediation is tracked as `GFQ-20260621-001` with status
`pending_leaf_build`.

## v0.4.63 - Foundations Graphify authority leaf refresh

### Added

- `01_foundations/graphify-out/leaf_slices/foundations_authority_20260620/`

### Changed

- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

The `foundations_authority_graph` leaf was refreshed for the foundation
institutionalization and visual-inspection completion work.

Build summary:

```text
detected_files = 341
detected_words = 476827
nodes = 1002
edges = 1381
communities = 93
root graph = not created
```

The build satisfies queue entries `GFQ-20260619-002`,
`GFQ-20260619-003`, `GFQ-20260619-004`, `GFQ-20260620-001` and
`GFQ-20260620-002`.

Operational limitation: chunks `13-16` were generated through deterministic
bounded structural extraction after worker subagents failed to write chunk
files within the operational window. This is recorded in the leaf
`BUILD_MANIFEST.md` and does not claim equivalence to full worker semantic
extraction for those chunks.

## v0.4.62 - Visual inspector pack completion gate

### Added

- `01_foundations/VISUAL_INSPECTION_PACK_REQUIREMENTS.md`
- `01_foundations/inspection_dossiers/financial/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/regime_indicators/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/short_review/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/additional/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/intraday_regime_features/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/halts/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/reference/visual_inspector_pack/`
- `01_foundations/inspection_dossiers/daily_adjusted/`

### Changed

- `01_foundations/FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md`
- `01_foundations/DATA_AUDIT_QUALITY_STANDARD.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`
- `01_foundations/README.md`
- `01_foundations/inspection_dossiers/financial/README.md`
- `01_foundations/inspection_dossiers/financial/financial_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/financial_quality_report_v0_1.md`
- `01_foundations/inspection_dossiers/regime_indicators/README.md`
- `01_foundations/inspection_dossiers/regime_indicators/regime_indicators_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md`
- `01_foundations/inspection_dossiers/short_review/README.md`
- `01_foundations/inspection_dossiers/short_review/short_review_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/short_review_quality_report_v0_1.md`
- `01_foundations/inspection_dossiers/additional/README.md`
- `01_foundations/inspection_dossiers/additional/additional_inspection_readout_v0_2.md`
- `01_foundations/data_quality_report/families/additional_quality_report_v0_1.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/README.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`
- `01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`
- `01_foundations/inspection_dossiers/halts/README.md`
- `01_foundations/inspection_dossiers/halts/halts_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/halts_quality_report_v0_1.md`
- `01_foundations/inspection_dossiers/reference/README.md`
- `01_foundations/inspection_dossiers/reference/reference_inspection_readout_v0_2.md`
- `01_foundations/data_quality_report/families/reference_quality_report_v0_1.md`
- `01_foundations/README.md`
- `01_foundations/data_quality_report/families/daily_adjusted_quality_report_v0_1.md`

### Notes

The foundation completion standard now requires a third axis:

```text
visual_inspection_status
```

Families without a benchmark-level visual inspector pack or an explicit visual
waiver can no longer be marked `human_inspector_ready`, even when their schemas,
contracts, registries, validators, readouts and tabular evidence exist.

This corrects completion semantics only. It does not change the underlying
data-quality verdicts. The first visual closure loop is:

```text
financial -> regime_indicators -> short_review -> additional ->
intraday_regime_features -> Halts -> reference -> ohlcv_daily_adjusted
```

The benchmark families remain `daily`, `quotes`, `trades`, `ohlcv_1m_raw` and
`ohlcv_1m_split_normalized`, each within its declared scope.

`financial_v0_1` was the first family closed under the corrected visual gate.
It now has six visual assets, a visual case manifest, an asset audit and a
reproducible visual builder. Its completion state is again:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Its data-quality verdict remains:

```text
blocked_by_data_defect
```

`regime_indicators_v0_1` was also closed under the corrected visual gate. It
now has six visual assets, a visual case manifest, an asset audit and a
reproducible visual builder. Its completion state is:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Its data-quality state remains:

```text
daily_bars_blocked_minute_bars_review_only
```

`short_review_finra_v0_1` was also closed under the corrected visual gate. It
now has six visual assets, a visual case manifest, an asset audit and a
reproducible visual builder. Its completion state is:

```text
foundations_completion_status = human_inspector_ready_scoped
visual_inspection_status = visual_complete
```

Its scoped verdict remains:

```text
official_free_baseline_provenance_not_short_replacement_with_short_volume_key_flags
```

`additional_v0_1` was also closed under the corrected visual gate. It now has
six generated visual assets, a visual case manifest, an asset audit and a
reproducible visual builder. Its completion state is:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Its scoped role remains:

```text
subfamily-governed RAW vendor context block
```

`intraday_regime_features_v0_1` was also closed under the corrected visual
gate. It now has five generated aggregate panels, ten governed semantic case
images, a visual case manifest, an asset audit and a reproducible visual
builder. Its completion state is:

```text
foundations_completion_status = human_inspector_ready_scoped
visual_inspection_status = visual_complete_scoped
```

Its scoped role remains:

```text
semantic pilot consumer of ohlcv_1m_split_normalized, not a production feature store
```

`halts_v0_1` was also closed under the corrected visual gate. It now has five
generated aggregate panels, five governed population visuals, a visual case
manifest, an asset audit and a reproducible visual builder. Its completion
state is:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Its scoped role remains:

```text
official halt/event context layer, not alpha or execution input
```

`reference_v0_1` was also closed under the corrected visual gate. It now has
six generated aggregate panels, five governed population visuals, a visual case
manifest, an asset audit and a reproducible visual builder. Its completion
state is:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Its scoped role remains:

```text
identity/lifecycle/corporate-action support, not final universe membership or alpha input
```

`daily_adjusted_v0_1` was also closed under the corrected visual gate by
creating a dedicated wrapper dossier and visual inspector pack while preserving
the source evidence under `inspection_dossiers/daily/`. It now has seven
generated visual panels, a visual case manifest, an asset audit and a
reproducible visual builder. Its completion state is:

```text
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

Its scoped role remains:

```text
full-universe derived economic daily price view, not raw or execution authority
```

## v0.4.61 - LT1B universe source-of-truth research certification

### Added

- `01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md`

### Changed

- `01_research/README.md`

### Notes

`01_research` now has an explicit consumption certificate for the `<1B>`
research universe used by Event Discovery, strategy preparation, research
backtests and derived labels.

The certificate does not redefine the universe. It anchors research consumption
to the governed `lt1b_universe_v0_1` source of truth:

```text
runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet
```

The certified rule is:

```text
ticker + PTI window [first_seen_date, last_observed_date]
```

The document records the verified 4,824 ticker count, the eligible
`classification_1b` classes, the lineage through `population_target_pti`, the
relationship with `E:\TSIS\data`, and the explicit non-goals: this is not RAW
vendor data, not daily fully point-in-time market-cap membership, and not a live
current-membership list.

## v0.4.60 - Short review scoped dossier completion

### Added

- `01_foundations/inspection_dossiers/short_review/evidence_assets/`
- `01_foundations/inspection_dossiers/short_review/build_short_review_inspection_pack.md`
- `01_foundations/inspection_dossiers/short_review/good_justification/short_review_finra_baseline_good_cases_v0_1.md`
- `01_foundations/inspection_dossiers/short_review/flagged_case_evidence_packs/short_review_short_volume_key_flags_v0_1.md`
- `01_foundations/inspection_dossiers/short_review/bad_case_evidence_packs/short_review_scope_and_history_boundaries_v0_1.md`
- `01_foundations/inspection_dossiers/short_review/coverage_case_evidence_packs/short_review_coverage_and_provenance_v0_1.md`

### Changed

- `01_foundations/inspection_dossiers/short_review/README.md`
- `01_foundations/inspection_dossiers/short_review/short_review_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/short_review_quality_report_v0_1.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/short_review_consumption_policy.md`
- `01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml`
- `01_foundations/validators/short_review/short_review_validators.md`

### Notes

`short_review_finra_v0_1` is now complete at the scoped foundation package
level:

```text
foundations_completion_status = human_inspector_ready_scoped
```

The data-quality verdict remains scoped:

```text
data_quality_verdict = complete_scoped
```

The evidence package records FINRA short interest with 505,745 rows and 4,687
tickers, and FINRA short volume with 4,689,038 rows and 4,623 tickers. It also
documents a new key-quality flag: short volume has 824 duplicate `ticker + date`
keys, 5,250 excess rows, concentrated in `CPS`, `OP` and `LFTR`.

This does not promote `short_review` as a production short dataset replacement.
It remains official/free baseline and provenance evidence with explicit source,
history and duplicate-key boundaries.

## v0.4.59 - Intraday regime features scoped dossier completion

### Added

- `01_foundations/inspection_dossiers/intraday_regime_features/evidence_assets/`
- `01_foundations/inspection_dossiers/intraday_regime_features/build_intraday_regime_features_inspection_pack.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/good_justification/intraday_regime_features_semantic_pilot_good_cases_v0_1.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/flagged_case_evidence_packs/intraday_regime_features_lookback_and_boundary_cases_v0_1.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/bad_case_evidence_packs/intraday_regime_features_production_boundary_v0_1.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/coverage_case_evidence_packs/intraday_regime_features_materialization_coverage_v0_1.md`

### Changed

- `01_foundations/inspection_dossiers/intraday_regime_features/README.md`
- `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`
- `01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`

### Notes

`intraday_regime_features_v0_1` is now complete at the scoped foundation package
level:

```text
foundations_completion_status = human_inspector_ready_scoped
```

The data-quality verdict remains scoped:

```text
data_quality_verdict = complete_scoped
```

The evidence package records 8 feature parquets, 243 ticker-day rows, 41
columns, no read errors, no duplicate `ticker + date` rows, expected provenance
values for raw and split-normalized price views, and the 10 semantic pilot
images.

This does not promote the feature layer as a full-universe feature store.

## v0.4.58 - Regime indicators human-inspector dossier completion

### Added

- `01_foundations/inspection_dossiers/regime_indicators/evidence_assets/`
- `01_foundations/inspection_dossiers/regime_indicators/build_regime_indicators_inspection_pack.md`
- `01_foundations/inspection_dossiers/regime_indicators/good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md`
- `01_foundations/inspection_dossiers/regime_indicators/bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md`
- `01_foundations/inspection_dossiers/regime_indicators/flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md`
- `01_foundations/inspection_dossiers/regime_indicators/coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md`

### Changed

- `01_foundations/inspection_dossiers/regime_indicators/README.md`
- `01_foundations/inspection_dossiers/regime_indicators/regime_indicators_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`

### Notes

`regime_indicators_v0_1` is now complete at the foundation package level:

```text
foundations_completion_status = human_inspector_ready
```

The data-quality verdict remains blocked:

```text
data_quality_verdict = blocked_by_data_defect
```

The new evidence package proves the daily blocker directly: all 34 daily files
have only `1970-01-01` as `date`, covering 153,397 daily rows. The scoped minute
review found 33 minute files, 64,348,953 rows, no duplicate timestamp rows, no
non-monotonic files, and 204 `high < low` rows concentrated in
`etfs/UVXY/minute.parquet`.

This does not promote regime indicators for consumption. Daily bars remain
blocked and minute bars remain review/scoped.

## v0.4.57 - Financial human-inspector dossier completion

### Added

- `01_foundations/inspection_dossiers/financial/evidence_assets/`
- `01_foundations/inspection_dossiers/financial/build_financial_inspection_pack.md`
- `01_foundations/inspection_dossiers/financial/good_justification/financial_payload_examples_v0_1.md`
- `01_foundations/inspection_dossiers/financial/bad_case_evidence_packs/financial_blocking_schema_cases_v0_1.md`
- `01_foundations/inspection_dossiers/financial/flagged_case_evidence_packs/financial_temporal_cases_v0_1.md`
- `01_foundations/inspection_dossiers/financial/coverage_case_evidence_packs/financial_coverage_cases_v0_1.md`

### Changed

- `01_foundations/inspection_dossiers/financial/README.md`
- `01_foundations/inspection_dossiers/financial/financial_inspection_readout_v0_1.md`
- `01_foundations/data_quality_report/families/financial_quality_report_v0_1.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`

### Notes

`financial_v0_1` is now complete at the foundation package level:

```text
foundations_completion_status = human_inspector_ready
```

The data-quality verdict remains blocked:

```text
data_quality_verdict = blocked_by_data_defect
```

The update converts the previous minimal dossier into a human-inspector package
with stable evidence assets, good payload examples, bad/blocking schema cases,
temporal/lifecycle cases and coverage evidence. The assets are derived from the
existing `E:/TSIS/data/financial/_audit` and `_run` outputs.

This does not promote financial data for consumption. It only means the
blockers are now visible and inspectable at the same foundation standard used by
the stricter market-data dossiers.

## v0.4.56 - Raw 1m completion status correction

### Changed

- `01_foundations/data_quality_report/families/ohlcv_1m_raw_quality_report_v0_1.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`

### Notes

The previous matrix entry understated the `ohlcv_1m_raw` inspection package.
After checking `inspection_dossiers/minute/`, the raw minute dossier already
contains modern core/vw evidence:

- `minute_00` through `minute_05` notebooks;
- `core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`;
- 7 population maps;
- 60 individual case images;
- contact sheets for core/vw families;
- reproducible visual and population manifests;
- core quality manifests and summaries.

The completion status is therefore corrected to:

```text
foundations_completion_status = human_inspector_ready_scoped
```

This does not change the data-quality verdict. Raw 1m remains scoped and not
globally clean for unflagged production use. The dominant distinction is that
core OHLCV quality and `vw` quality must be read separately, and split-sensitive
cross-session work should continue to use `ohlcv_1m_split_normalized`.

## v0.4.55 - Foundations family completion standard

### Added

- `01_foundations/FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md`

### Changed

- `01_foundations/README.md`
- `01_foundations/DATA_AUDIT_QUALITY_STANDARD.md`
- `01_foundations/data_quality_report/README.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`

### Notes

This update clarifies that "institutionalized" inside `01_foundations` means
complete enough for human inspection across all required foundation surfaces. It
does not mean production-ready data.

The new standard separates:

- `data_quality_verdict`: what the audit concluded about the data;
- `foundations_completion_status`: whether the family package is complete for a
  human inspector.

The matrix now records both axes explicitly. At this version boundary,
`financial` was classified as:

- `data_quality_verdict = blocked_by_data_defect`
- `foundations_completion_status = governance_pack_created_dossier_missing`

This specific `financial` completion status was superseded by `v0.4.57`, where
the dossier package was completed as `human_inspector_ready`.

This prevents a blocked summary report from being mistaken for a finished
`inspection_dossiers/` package.

### Impact

Future family work must not be called complete unless schemas, contracts,
policies, registries, validators, inspection dossiers, evidence assets,
quality reports, indexes and changelog entries meet the completion gate or have
an explicit documented waiver.

## v0.4.54 - Core market data quality reports

### Added

- `01_foundations/data_quality_report/families/daily_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/quotes_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/trades_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/ohlcv_1m_raw_quality_report_v0_1.md`

### Changed

- `01_foundations/data_quality_report/README.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`

### Notes

The normalized `data_quality_report/` surface now includes the core market data
families that had already served as the strictness baseline:

- `daily_core_v0_1`
- `quotes_core_v0_1`
- `trades_core_v0_1`
- `ohlcv_1m_raw_v0_1`

This does not re-audit those families from scratch. It imports their existing
contracts, policies, validators, readouts, casepacks and closeout evidence into
the common per-family report structure.

### Impact

Auditors can now enter `data_quality_report/` and find both:

- the newer `E:/TSIS/data` family reports;
- and the core `daily`, `quotes`, `trades` and raw `1m` reports that define the
  quality bar future data layers must meet.

## v0.4.53 - Data quality report foundation surface

### Added

- `01_foundations/data_quality_report/README.md`
- `01_foundations/data_quality_report/family_status_matrix_v0_1.md`
- `01_foundations/DATA_AUDIT_QUALITY_STANDARD.md`
- `01_foundations/DATA_AUDIT_TOPIC_NAVIGATION.md`
- `01_foundations/data_quality_report/families/additional_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/daily_adjusted_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/financial_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/halts_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/ohlcv_1m_split_normalized_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/reference_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md`
- `01_foundations/data_quality_report/families/short_review_quality_report_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/daily_adjusted_consumption_policy.md`
- `01_foundations/data_consumption_policies/financial_consumption_policy.md`
- `01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md`
- `01_foundations/data_consumption_policies/regime_indicators_consumption_policy.md`
- `01_foundations/dataset_registry/financial/financial_registry_entry.yaml`
- `01_foundations/dataset_registry/regime_indicators/regime_indicators_registry_entry.yaml`
- `01_foundations/validators/financial/financial_validators.md`
- `01_foundations/validators/intraday_regime_features/intraday_regime_features_validators.md`
- `01_foundations/validators/regime_indicators/regime_indicators_validators.md`
- `01_foundations/validators/short_review/short_review_validators.md`
- `01_foundations/inspection_dossiers/financial/`
- `01_foundations/inspection_dossiers/regime_indicators/`
- `01_foundations/inspection_dossiers/short_review/`
- `01_foundations/inspection_dossiers/intraday_regime_features/README.md`

### Changed

- `01_foundations/data_quality_report/family_status_matrix_v0_1.md` records
  `2026-06-20` as the initial reference date for future modifications.

### Notes

The new `data_quality_report/` layer normalizes the audit surface for the
physical roots under `E:/TSIS/data` without treating the physical path as
semantic authority.

The first pass classifies:

- `additional`, `Halts`, `reference`, `ohlcv_daily_adjusted` as
  `complete_import_ready`;
- `ohlcv_1m_split_normalized` as `complete_scoped`;
- `intraday_regime_features` as `complete_scoped_pilot`;
- `short_review` as `complete_scoped_provenance`;
- `financial` as `blocked_documented`;
- `regime_indicators` as `blocked_documented`.

The blocked states are intentional quality outcomes, not missing work:

- `financial_v0_1` has complete endpoint coverage but operational audit
  `status = FAIL`, with severe and temporal issues still blocking consumption;
- `regime_indicators_v0_1` has readable daily files, but daily `date` and
  `datetime` semantics are invalid and clustered in 1970.

### Impact

This is a CAPA 1 governance and reporting update. It defines where future
auditors should look for per-family quality verdicts before building
`master_daily_table`, `master_intraday_table`, features, labels, ML/RL inputs or
live consumers.

## v0.4.52 - Additional RAW vendor context quality package

### Added

- `01_foundations/validators/additional/additional_validators.md`
- `01_foundations/module_contracts/additional_contracts_index.md`
- `01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md`
- `01_foundations/inspection_dossiers/additional/README.md`
- `01_foundations/inspection_dossiers/additional/additional_inspection_readout_v0_2.md`
- `01_foundations/inspection_dossiers/additional/build_additional_inspection_pack.md`
- `01_foundations/inspection_dossiers/additional/evidence_assets/`
- `01_foundations/inspection_dossiers/additional/good_justification/`
- `01_foundations/inspection_dossiers/additional/flagged_case_evidence_packs/`
- `01_foundations/inspection_dossiers/additional/coverage_case_evidence_packs/`
- `scripts/inspection/additional/build_additional_inspection_pack.py`

### Changed

- `01_foundations/README.md`
- `01_foundations/validators/README.md`
- `01_foundations/module_contracts/README.md`
- `01_foundations/module_contracts/transversal_contracts_index.md`
- `01_foundations/inspection_dossiers/README.md`
- `01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/additional_consumption_policy.md`
- `01_foundations/dataset_registry/additional/additional_registry_entry.yaml`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

`additional_v0_1` is now governed as RAW vendor context data with explicit
subfamily quality tables and master-table readiness evidence.

The package records how Additional can contribute to:

- `data_quality_report`
- `master_daily_table`
- `master_intraday_table` as indirect event-time context only
- `symbol_master`
- `corporate_actions_table` as secondary reconciliation only
- `calendar_table`

The maturity reading for `Additional context` moves from `78%` to `92%`.

This is not a promotion to core market data, not a materialized master-table
release and not permission for `ml_primary`, `execution_simulator`,
`rl_allowed` or live consumers. Remaining limits are explicit: ratios are sparse
and vendor-derived, news requires attribution guardrails, corporate actions are
secondary to `reference`, and fundamentals require point-in-time filing logic.

### Impact

This is a CAPA 1 governance/evidence update. It changes how agents should read
Additional when designing data-quality tables and future master tables. It made
the prior `foundations_authority_graph` stale for Additional/master-table
queries; `GFQ-20260619-004` was satisfied by
`foundations_authority_20260620`.

## v0.4.51 - RAW authority and derivation map

### Added

- `01_foundations/module_contracts/raw_data_authority_and_derivation_map.md`
- external physical guide `E:/TSIS/data/README.md`

### Changed

- `01_foundations/README.md`
- `01_foundations/module_contracts/README.md`
- `01_foundations/module_contracts/transversal_contracts_index.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

The new module contract formalizes the distinction between:

- RAW vendor/original or staged data by provenance;
- raw market data by functional role;
- raw reference/context data by functional role;
- RAW audited data;
- reference data;
- context data;
- derived ETL views;
- feature layers;
- label/target layers;
- audit evidence;
- runtime/cache artifacts.

The contract fixes the central rule:

```text
RAW data means data preserved without semantic content alteration.
It does not mean data with minimal transformation.
```

It also records that derived layers such as `daily_adjusted` or
`ohlcv_1m_split_normalized`, feature layers such as
`intraday_regime_features`, label layers such as `daily_return_labels`, and
evidence assets such as dossiers or Graphify outputs cannot displace primary
RAW/reference audit.

Clarification: `RAW` is not limited to price/book/tape market data. Any Polygon
payload preserved without semantic alteration is RAW vendor data, including
short, financials, news, IPOs, economic, reference, halts and additional
subfamilies. The separate question is functional role: market, reference,
context, fundamentals, event, derived, feature, label or evidence.

An external physical guide was also created at `E:/TSIS/data/README.md`. That
file is a disk-level orientation guide only; the versioned authority remains the
`01_foundations` module contract.

### Impact

This is a semantic-governance update. It does not change physical datasets,
schemas, validators or allowed consumers. It made the prior
`foundations_authority_graph` stale for raw-vs-derived questions;
`GFQ-20260619-003` was satisfied by `foundations_authority_20260620`.

## v0.4.50 - graph-first query protocol for foundations

### Changed

- `01_foundations/README.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

The `01_foundations` README now records the operational distinction between:

- `graph_only` answers;
- `graph_first_source_verified` answers;
- `source_only_exception` answers.

Future agents must query the official Graphify leaf first for architecture,
relationships, institutional quality, maturity or coverage questions, and then
verify material claims against source documents, scripts, dossiers and
`evidence_assets`.

The README also records that the historical research graph
`certification_decisions_graph` is primary context for questions that may depend
on historical audit/certification, closeouts, historical policies, global
metrics, `expected/present/healthy/usable` decisions or preserved exploratory
evidence.

### Impact

This is an agent navigation and evidence-use update. It does not change dataset
contracts, schemas, validators or consumption policies. The README change is
covered by `GFQ-20260619-002`, which was satisfied by
`foundations_authority_20260620`.

## v0.4.49 - foundations README cross-graph lookup rule

### Changed

- `01_foundations/README.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`

### Notes

The `01_foundations` README now records that the official
`certification_decisions_graph` exists outside `01_foundations` and must be
consulted for questions that depend on historical audit/certification,
closeouts, historical policies, global metrics or
`expected/present/healthy/usable` decisions.

This prevents future agents from treating `foundations_authority_graph` as the
only semantic graph relevant to data-foundation completion.

### Impact

The README update was registered as `GFQ-20260619-002` with severity `MEDIUM`.
Superseded note: it was satisfied by `foundations_authority_20260620`.

## v0.4.48 - official graphify leaf publication

### Added

- `01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_20260619/`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/.graphifyignore`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/module_contracts/graphify/README.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/module_contracts/graphify/certification_decisions_graph_protocol.md`

### Changed

- Root `.gitignore` now explicitly opens the governed
  `00_data_certification` Graphify leaf path while preserving the default
  protection of heavy historical artifacts.
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md` records
  `foundations_authority_graph` as `leaf_built`.
- `00_data_certification/GRAPHIFY_REFRESH_QUEUE.md` records
  `certification_decisions_graph` as `leaf_built`.

### Notes

This closes the first two official Module 01 Graphify leaves and publishes them
to `origin/main`:

```text
foundations_authority_graph
certification_decisions_graph
```

`foundations_authority_graph` maps the authority and contract layer for
`01_foundations`:

```text
detected_files: 246
detected_words: 411452
nodes: 696
edges: 854
communities: 75
```

`certification_decisions_graph` maps final certification decisions, policies,
contracts and lightweight global metrics inside `00_data_certification`:

```text
detected_files: 89
detected_words: 45813
nodes: 252
edges: 322
communities: 22
```

Both leaves passed `graphify diagnose multigraph` with 0 dangling endpoints, 0
duplicate edges and 0 endpoint-collapsed edge groups. Both intentionally avoid
creating a root `graphify-out/graph.json` for their parent scopes.

### Impact

Future agents can use the two official Graphify leaves as semantic maps, but
must not treat them as physical dataset profilers, certification substitutes or
table design authority by themselves.

Notebook evidence is intentionally not included in
`certification_decisions_graph`. It remains important and should be handled by a
separate future leaf, provisionally:

```text
certification_notebook_evidence_graph
```

## v0.4.47 - data foundation graphify governance protocol

### Added

- `01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
- `01_foundations/GRAPHIFY_REFRESH_QUEUE.md`
- `01_foundations/.graphifyignore`
- `01_foundations/module_contracts/graphify/README.md`
- `01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md`

### Changed

- `01_foundations/README.md`
- `01_foundations/module_contracts/README.md`

### Notes

This adds a module-level protocol for using Graphify before designing CAPA 1
Data Foundation tables.

The root `01_foundations` protocol now mirrors the role of the `00_CTO`
Graphify protocol: it defines what counts as official Graphify output, how to
avoid manual `graph.json` fallbacks, and when to refresh by severity instead of
per commit.

The protocol requires separate graphs for:

- `foundations_authority_graph`
- `certification_decisions_graph`
- `reference_identity_graph`
- `daily_ohlcv_graph`
- `microstructure_quotes_trades_graph`
- `additional_fundamentals_news_graph`

It also states that Graphify is a semantic map, not a physical data profiler or
source of truth. Table design must combine architecture, `01_foundations`
contracts, `00_data_certification` evidence and physical parquet/CSV profiling.

### Impact

Future agents must not build one giant graph of all `01_foundations` or all
`00_data_certification` as the first step for CAPA 1.

Future CAPA 1 tables remain hypotheses until justified by:

```text
contract + certification + evidence + physical profiling + validator
```

## v0.4.46 - halts modern inspection dossier completion

### Added

- `scripts/inspection/halts/build_halts_inspection_pack.py`
- `01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/halts/halts_registry_entry.yaml`
- `01_foundations/data_consumption_policies/halts_consumption_policy.md`
- `01_foundations/validators/halts/halts_validators.md`
- `01_foundations/inspection_dossiers/halts/README.md`
- `01_foundations/inspection_dossiers/halts/build_halts_inspection_pack.md`
- `01_foundations/inspection_dossiers/halts/halts_inspection_readout_v0_1.md`
- `01_foundations/inspection_dossiers/halts/halts_casepacks_traceability_audit_v0_1.md`
- `01_foundations/inspection_dossiers/halts/integration_notes.md`
- `01_foundations/inspection_dossiers/halts/evidence_assets/`
- `01_foundations/inspection_dossiers/halts/good_justification/`
- `01_foundations/inspection_dossiers/halts/flagged_case_evidence_packs/`
- `01_foundations/inspection_dossiers/halts/bad_case_evidence_packs/`
- `01_foundations/inspection_dossiers/halts/causal_case_evidence_packs/`
- `01_foundations/inspection_dossiers/halts/coverage_case_evidence_packs/`

### Changed

- `01_foundations/inspection_dossiers/README.md`
- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/validators/README.md`

### Notes

This promotes `halts` from historical audit/certification into the modern foundation layer without copying historical heavy parquets into `01_foundations`.

The new builder reads only protected provenance:

- `E:/TSIS/data/Halts`
- `D:/Halts`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts`

and emits lightweight assets under `01_foundations`:

- historical cache inventory: `19` rows;
- certification inventory: `10` rows;
- physical root audit: `6` rows;
- population summary: `16` rows;
- population visual overview: `5` PNGs;
- casepacks: `5`;
- run manifest: `evidence_assets/run_manifest.json`.

### Impact

`halts` now has:

- a reproducible builder/toolchain;
- active evidence assets;
- population visuals;
- manifests;
- casepacks;
- a traceability audit;
- dataset contract;
- registry entry;
- consumption policy;
- validators;
- and a readout v0.1 with `Que muestra / Responde / No responde / Consecuencia`.

Correct state:

```text
halts = historical_deep_audit_closed + modern_dossier_complete_for_foundation_promotion
```

This does not enable new sensitive consumers. `halts` remains prohibited as alpha, live, RL, execution truth or ML/backtest feature without later temporal, leakage and consumer-specific contracts.

## v0.4.45 - reference modern inspection dossier completion

### Added

- `scripts/inspection/reference/build_reference_inspection_pack.py`
- `01_foundations/inspection_dossiers/reference/build_reference_inspection_pack.md`
- `01_foundations/inspection_dossiers/reference/reference_inspection_readout_v0_2.md`
- `01_foundations/inspection_dossiers/reference/reference_casepacks_traceability_audit_v0_1.md`
- `01_foundations/inspection_dossiers/reference/integration_notes.md`
- `01_foundations/inspection_dossiers/reference/evidence_assets/`
- `01_foundations/inspection_dossiers/reference/good_justification/`
- `01_foundations/inspection_dossiers/reference/flagged_case_evidence_packs/`
- `01_foundations/inspection_dossiers/reference/bad_case_evidence_packs/`
- `01_foundations/inspection_dossiers/reference/causal_case_evidence_packs/`
- `01_foundations/inspection_dossiers/reference/coverage_case_evidence_packs/`

### Changed

- `01_foundations/inspection_dossiers/reference/README.md`
- `01_foundations/inspection_dossiers/reference/reference_institutional_closeout_v0_1.md`
- `01_foundations/inspection_dossiers/reference/reference_modernization_gap_audit_2026-06-12.md`
- `01_foundations/inspection_dossiers/reference/reference_upgrade_agent_prompt_2026-06-12.md`
- `01_foundations/inspection_dossiers/README.md`
- `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/reference/reference_registry_entry.yaml`
- `01_foundations/validators/reference/reference_validators.md`

### Notes

This closes the modernization gap identified in v0.4.44 for the current foundation-layer scope of `reference`.

The new builder reads only protected provenance:

- `E:/TSIS/data/reference`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference`

and emits lightweight assets under `01_foundations`:

- historical cache inventory: `31` artifacts;
- certification/global metrics inventory: `7` artifacts;
- physical root audit: `8` subfamilies;
- population summary: `26` buckets;
- population visual overview: `5` PNGs;
- casepacks: `5`;
- run manifest: `evidence_assets/run_manifest.json`.

### Impact

`reference` now has:

- a reproducible builder/toolchain;
- active evidence assets;
- population visuals;
- manifests;
- casepacks;
- a traceability audit;
- and a readout v0.2 with `Que muestra / Responde / No responde / Consecuencia`.

Correct state:

```text
reference = historical_deep_audit_closed + modern_dossier_complete_for_foundation_promotion
```

This does not enable new sensitive consumers. `reference` remains prohibited as alpha, live, RL, final universe membership or continuity remap service without later contracts.

## v0.4.44 - reference modernization gap audit

### Added

- `01_foundations/inspection_dossiers/reference/README.md`
- `01_foundations/inspection_dossiers/reference/reference_modernization_gap_audit_2026-06-12.md`
- `01_foundations/inspection_dossiers/reference/reference_upgrade_agent_prompt_2026-06-12.md`

### Changed

- `01_foundations/inspection_dossiers/reference/reference_institutional_closeout_v0_1.md`
- `01_foundations/inspection_dossiers/README.md`
- `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/reference/reference_registry_entry.yaml`

### Notes

This update corrects the maturity reading of `reference`.

`reference` remains valid as a minimally promoted foundation layer, but it must not be described as inspector-forensic parity with `daily`, `quotes`, `trades`, `minute` or `1m_split_normalized` until it has:

- active evidence assets under `01_foundations`;
- a physical root audit;
- population visual overview;
- manifests;
- casepacks;
- a reproducible builder/toolchain;
- and `reference_inspection_readout_v0_2.md`.

The historical evidence is strong and preserved, including `auditoria/reference`, `certification/reference` and `cache_v2`.
The new gap audit makes the next agent task explicit: convert that evidence into a modern general-to-specific inspection dossier without moving historical evidence or physical source data.

## v0.4.43 - reference foundation layer institutionalization

### Added

- `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/reference/reference_registry_entry.yaml`
- `01_foundations/data_consumption_policies/reference_consumption_policy.md`
- `01_foundations/inspection_dossiers/reference/reference_institutional_closeout_v0_1.md`
- `01_foundations/validators/reference/reference_validators.md`

### Changed

- `01_foundations/contract_registry/dataset_contracts/README.md`
- `01_foundations/dataset_registry/README.md`
- `01_foundations/data_consumption_policies/README.md`
- `01_foundations/inspection_dossiers/README.md`
- `01_foundations/validators/README.md`

### Notes

`reference` is now promoted from preserved historical audit evidence into an active `01_foundations` layer.

The promotion does not rerun the historical audit and does not move preserved evidence.
It creates the modern operating layer that connects:

- dataset contract;
- registry entry;
- consumption policy;
- inspection dossier;
- validators;
- existing canonical schemas;
- and historical closeout evidence.

The active physical root is recorded as:

- `E:\TSIS\data\reference`

The historical schemas and audit notes may still contain `D:\reference` examples because those were representative inspection paths at the time of schema drafting.

### Impact

`reference` is now governed as a foundation layer for identity, ticker types, events, splits, dividends, exchanges, price-view support, universe support and causal overlays.

It remains explicitly prohibited to treat `reference` as price, execution tape, final universe membership, feature alpha or full continuity remap service without a later contract.

## v0.4.30 - transversal layer validation standard

### Added

- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`

### Notes

This standard closes a missing transversal governance piece:

- when a new layer may be considered semantically validated;
- what minimum checks it must pass before being called well-built;
- and how to avoid treating "the script ran" or "a few examples looked fine" as sufficient evidence.

The standard fixes seven required validation dimensions:

- semantic validation;
- implementation validation;
- negative controls;
- visual or inspective validation;
- real consumer validation;
- reproducibility;
- and documentary traceability.

It also introduces maturity levels so new layers can be described as:

- defined;
- implemented;
- piloted;
- audited;
- consumed;
- or promoted.

## v0.4.31 - first explicit maturity assessment for core derived layers

### Added

- `01_foundations/module_contracts/layer_maturity_assessment_v0_1.md`

### Notes

This document applies the new transversal validation standard to three active layers:

- `daily_adjusted`
- `ohlcv_1m_split_normalized`
- `intraday_regime_features`

The resulting classification is:

- `daily_adjusted` -> `Nivel 5 - Consumida`
- `ohlcv_1m_split_normalized` -> `Nivel 4 - Auditada`
- `intraday_regime_features` -> `Nivel 1 - Definida`

This makes the current architectural sequence explicit and removes the need to infer maturity from scattered pilots, readouts, and contracts.

## v0.4.32 - first executable landing of `intraday_regime_features`

### Added

- `scripts/materialize_intraday_regime_features.py`
- `01_foundations/module_contracts/intraday_regime_features_initial_materialization_results_v0_1.md`

### Notes

This is the first real executable landing of the first proposed consumer of `ohlcv_1m_split_normalized`.

The materializer now reads:

- `D:\\ohlcv_1m`
- `E:\\TSIS\\data\\ohlcv_1m_split_normalized`

and writes:

- `E:\\TSIS\\data\\intraday_regime_features`

at `ticker-day` grain.

Its first promoted feature families are now explicit in code:

- cross-session regime features computed from `1m_split_normalized`
- local intrasesion features computed from `1m raw`

This moves `intraday_regime_features` from:

- `Nivel 1 - Definida`

to:

- `Nivel 2 - Implementada`

while still leaving semantic pilot and downstream validation as the next required step before calling the layer fully piloted or consumed.

## v0.4.33 - semantic pilot and audit readout for `intraday_regime_features`

### Added

- `scripts/inspection/minute/export_intraday_regime_features_pilot_readout.py`
- `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`
- `01_foundations/module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md`

### Notes

This closes the first semantic pilot of the first real consumer of `ohlcv_1m_split_normalized`.

The readout now compares, case by case, the same cross-session features computed:

- with `1m raw` as a counterfactual
- versus `1m_split_normalized` as the contractual view

The result is now explicit:

- strong reverse-split months show massive false-gap contamination under raw;
- several forward-split months also show materially wrong cross-session readings under raw;
- and controls remain neutral, including the important case where `future_split_factor != 1` but all compared days still live in the same relative scale regime.

This promotes:

- `intraday_regime_features` from `Nivel 2 - Implementada` to `Nivel 3 - Pilotada`
- `ohlcv_1m_split_normalized` from `Nivel 4 - Auditada` to `Nivel 5 - Consumida`

## v0.4.34 - explicit separation between data-audit consumer and deferred feature-engineering backlog

### Added

- `01_foundations/module_contracts/intraday_regime_features_deferred_families_v0_1.md`

### Notes

This update makes a critical phase boundary explicit:

- `intraday_regime_features v0_1` remains a minimal semantic-validation consumer for `1m_split_normalized`;
- it is not yet the start of broad strategy feature engineering or alpha research.

The richer families around:

- premarket context;
- opening/first-hour behavior;
- richer multi-session extension;
- intraday volume profile;
- session range position;
- and contextual compression/expansion

are now preserved as deferred backlog in the correct place, without polluting the current data-audit phase.

## v0.4.35 - navigation layer for `module_contracts` before any physical migration

### Added

- `01_foundations/module_contracts/README.md`
- `01_foundations/module_contracts/daily_contracts_index.md`
- `01_foundations/module_contracts/quotes_contracts_index.md`
- `01_foundations/module_contracts/trades_contracts_index.md`
- `01_foundations/module_contracts/ohlcv_1m_contracts_index.md`
- `01_foundations/module_contracts/transversal_contracts_index.md`

### Notes

This update does **not** move any contract yet.

It introduces a navigation layer first, while explicitly marking physical reorganization as pending work that must avoid:

- broken references;
- orphaned links in readouts and notebooks;
- and silent path drift for humans and agents.

## v0.4.36 - final inspector package for `ohlcv_1m_split_normalized`

### Added

- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `scripts/inspection/minute/build_1m_split_normalized_inspection_notebook.py`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb`

### Notes

This closes the inspector-facing package for `ohlcv_1m_split_normalized` by unifying:

- contractual semantics;
- the price-layer pilot;
- the downstream minimal consumer pilot;
- and a final inspector readout with an executed notebook saved with outputs.

The package now supports both:

- markdown-first institutional review;
- and notebook-first visual supervision without requiring the inspector to recompute the whole chain manually.

## v0.4.37 - exhaustive full-universe split audit for `1m`

### Added

- `scripts/inspection/minute/audit_1m_split_full_universe.py`
- `scripts/inspection/minute/build_1m_split_full_universe_audit_notebook.py`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb`

### Notes

This closes the open debt around "proving all split cases" at the strongest level allowed by the actual `1m` coverage.

The exhaustive audit now covers:

- `3335` split-event cases intersected with real `1m` availability

with results:

- `PASS = 2280`
- `FAIL = 0`
- `NO_PRE_COVERAGE = 164`
- `NO_POST_COVERAGE = 151`
- `NO_1M_COVERAGE = 740`

The key institutional conclusion is now explicit:

- **100% of fully auditable cases pass**
- and the remaining non-pass statuses are classified as coverage limits, not semantic failures.

The new notebook gives the inspector a live selector over the full audited universe instead of a fixed sample of PNGs.

## v0.4.38 - modern core/vw inspector package for `ohlcv_1m_raw`

### Added

- `scripts/inspection/minute/build_minute_modern_inspection_notebooks.py`
- `01_foundations/inspection_dossiers/minute/minute_00_universe_quality_overview_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_01_core_quality_model_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_02_core_quality_population_readout_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_03_casepack_builder_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_04_ticker_month_inspector_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_05_final_readout_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/evidence_assets/core_quality/minute_core_quality_manifest_v0_1.parquet`
- `01_foundations/inspection_dossiers/minute/evidence_assets/core_quality/minute_core_quality_family_counts_v0_1.csv`
- `01_foundations/inspection_dossiers/minute/evidence_assets/core_quality/minute_core_quality_summary_v0_1.csv`

### Changed

- `01_foundations/inspection_dossiers/minute/README.md`
- `01_foundations/inspection_dossiers/README.md`

### Notes

This upgrades the `minute` dossier from a raw closeout plus schema-only readout into a modern inspector package that separates:

- core OHLCV quality;
- `vw_*` quality;
- combined state;
- and allowed consumption.

The executed manifest covers:

- `334660` ticker-month rows;
- `4822` tickers;
- years `2005` to `2026`.

Current core result:

- `core_good = 331511`
- `core_review = 3149`
- `core_bad = 0`

Current `vw` result:

- `vw_good = 46652`
- `vw_review = 75245`
- `vw_bad = 212763`

Current consumption result:

- `controlled_ohlcv_research = 118818`
- `ohlcv_without_vw_only = 212693`
- `flagged_research_or_sensitivity = 3149`

The institutional conclusion is deliberately not "1m raw is productively clean".

The correct conclusion is:

- most raw `1m <1B>` rows are now defensible for controlled OHLCV research when `vw` is excluded;
- a large majority remains unsuitable for `vw`-dependent consumers;
- the small `core_review` tail requires sensitivity or forensic review;
- and any production backtest/ML use still needs an explicit downstream contract and flags.

The notebooks `minute_03` and `minute_04` are intentionally interactive widget notebooks. They are not pre-executed with large widget state because their role is case selection and inspector navigation, not static bulk output.

## v0.4.39 - fixed visual casepacks for `ohlcv_1m_raw` core/vw inspection

### Added

- `scripts/inspection/minute/export_minute_core_quality_casepacks.py`
- `scripts/inspection/minute/build_minute_core_quality_visual_readout.py`
- `scripts/inspection/minute/build_minute_launcher_notebooks.py`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/minute_core_quality_visual_case_manifest_v0_1.csv`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/images/`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/contact_sheets/`

### Changed

- `01_foundations/inspection_dossiers/minute/README.md`
- `01_foundations/inspection_dossiers/README.md`
- `01_foundations/inspection_dossiers/minute/minute_00_universe_quality_overview_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_01_core_quality_model_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_02_core_quality_population_readout_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_03_casepack_builder_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_04_ticker_month_inspector_v0_1.ipynb`
- `01_foundations/inspection_dossiers/minute/minute_05_final_readout_v0_1.ipynb`

### Notes

This corrects an incomplete landing in v0.4.38.

The `minute` dossier now has fixed inspector-facing visual evidence, not only notebooks, widgets and manifests.

The new visual readout contains:

- `60` individual PNG images;
- `6` visual sections;
- `10` cases per section;
- and one independent `Que muestra / Responde / No responde / Consecuencia` reading for every image.

The sections are:

- `core_good_vw_not_flagged`
- `core_good_vw_mild_or_moderate`
- `core_good_vw_bad_persistent`
- `core_good_vw_bad_diffuse`
- `core_review_large_gap`
- `core_review_sparse`

During visual inspection, the important new finding was that `vw_not_flagged` is not visually uniform:

- some cases are materially clean;
- but several `MULN` months show recalculated visual `vw` residue even though the inherited bucket is `vw_not_flagged`.

This does not invalidate the core OHLCV conclusion by itself.

It does require future consumers and inspectors to distinguish:

- inherited closeout family;
- recalculated visual `vw` residue;
- core OHLCV usability;
- and `vw` consumption eligibility.

The notebook/widget layer remains useful for drilldown, but the inspector package now has static, reviewable, embedded image evidence comparable in intent to `daily`, `quotes` and `trades`.

The six modern `minute_*.ipynb` notebooks were regenerated as launcher/reader notebooks:

- no heavy core/vw classification functions remain in notebook cells;
- no plotting materialization logic remains in notebook cells;
- fixed image export lives in `export_minute_core_quality_casepacks.py`;
- fixed markdown readout generation lives in `build_minute_core_quality_visual_readout.py`.

## v0.4.40 - general-to-specific visual dossier rule formalized

### Changed

- `01_foundations/module_contracts/inspection_dossier_model.md`
- `01_foundations/inspection_dossiers/README.md`

### Notes

This formalizes a missing rule that was already implicit in strong dossiers such as `trades`, `quotes` and `daily`.

Inspector-facing dossiers must move from general to specific:

- population visual overview;
- distributions and mass by state/family;
- coverage or expected-universe readout;
- evidence families;
- individual cases;
- consumption decision.

The new rule explicitly states that:

- a sample of cases does not replace a population map;
- a population map does not replace individual visual case analysis;
- visual population summaries should not remain trapped only inside notebooks when they are required for human inspection;
- stable PNGs should be exported and embedded in markdown for final inspector-facing dossiers.

This rule is now binding for future upgrades of `minute`, `1m_split_normalized` and any other inspection dossier with enough mass or complexity to require both aggregate and case-level evidence.

## v0.4.41 - population visual overview applied to `ohlcv_1m_raw` minute dossier

### Added

- `scripts/inspection/minute/export_minute_population_visuals.py`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/population_visual_overview/`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/population_visual_overview/minute_population_visual_manifest_v0_1.csv`

### Changed

- `scripts/inspection/minute/build_minute_core_quality_visual_readout.py`
- `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`
- `01_foundations/inspection_dossiers/minute/README.md`
- `01_foundations/inspection_dossiers/README.md`

### Notes

This applies the v0.4.40 general-to-specific dossier rule to `minute`.

The inspector-facing readout now starts with `7` population visuals before the `60` ticker-month case images:

- core/vw state overview;
- core/vw matrix;
- issue family distributions;
- coverage and temporal footprint;
- schema-only anatomy;
- `vw_not_flagged` visual recalculation delta;
- allowed consumption by year.

The complete fixed visual package now contains `67` embedded images, and every image has an independent `Que muestra / Responde / No responde / Consecuencia` reading.

The important institutional clarification is that `ohlcv_1m_raw <1B>` is not globally rejected as OHLCV: the core axis is mostly usable for controlled OHLCV research, while `vw` remains the dominant unresolved debt. The dossier now makes that visible at population level before asking the inspector to read individual cases.

## v0.4.42 - general-to-specific visual inspector pack for `ohlcv_1m_split_normalized`

### Added

- `scripts/inspection/minute/export_1m_split_normalized_inspector_pack.py`
- `01_foundations/inspection_dossiers/1m_split_normalized/README.md`
- `01_foundations/inspection_dossiers/1m_split_normalized/population_visual_overview/`
- `01_foundations/inspection_dossiers/1m_split_normalized/population_visual_overview/ohlcv_1m_split_normalized_population_visual_manifest_v0_1.csv`
- `01_foundations/inspection_dossiers/1m_split_normalized/event_case_evidence_packs/`
- `01_foundations/inspection_dossiers/1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`
- `01_foundations/inspection_dossiers/1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_case_manifest_v0_1.csv`

### Changed

- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `01_foundations/inspection_dossiers/README.md`

### Notes

This applies the same general-to-specific inspection policy to `ohlcv_1m_split_normalized`.

The new visual inspector pack contains:

- `6` population visuals;
- `28` event-case visuals;
- `34` embedded images in total;
- and one independent `Que muestra / Responde / No responde / Consecuencia` reading for every image.

The institutional clarification is:

- the full-universe audit is closed for split events that are empirically auditable in `1m`;
- `FAIL = 0` across `2280` fully auditable PASS cases;
- `NO_PRE_COVERAGE`, `NO_POST_COVERAGE` and `NO_1M_COVERAGE` are coverage limits, not semantic failures;
- this must not be confused with physical full-universe materialization of every ticker-month in `E:/TSIS/data/ohlcv_1m_split_normalized`.

The final readout was updated because its older wording still said broad aggregate validation was not closed. That is now too weak after the full-universe split-event audit; the remaining limitation is physical promotion/materialization scope, not semantic split-event validation.

## v0.4.15 - repaso transversal final de `01_foundations`

### Added

- `01_foundations/module_contracts/foundations_transversal_final_review_v0_1.md`

### Notes

This review consolidates the current institutional status of the module and separates three layers:

- what is already effectively closed;
- what remains as real methodological debt;
- and what is only cosmetic or asymmetry-of-finish debt.

The main open items left explicit are:

- full downstream integration of `split_normalized`;
- extension of `adjusted` to more complex corporate actions;
- and a final upgrade of `quotes` toward the same global analytic standard already reached by `trades`.

The review was also explicitly marked as a **state snapshot**, not a live primary policy.

It now includes review triggers so it does not silently become stale if:

- `price views` are promoted to real consumers;
- complex downstream consumers are contracted;
- or the module changes phase materially.

## v0.4.16 - transversal standard for institutional state snapshots

### Added

- `01_foundations/module_contracts/state_snapshot_standard.md`

### Notes

This standard fixes how state-review artifacts must be treated:

- as versioned state snapshots;
- not as live primary policies;
- and with explicit review/versioning triggers so they do not become silently stale.

## v0.4.17 - priority plan for real `price view` integration

### Added

- `01_foundations/module_contracts/price_view_consumer_integration_status.md`
- `01_foundations/module_contracts/price_view_integration_priority_plan_v0_1.md`

### Notes

This closes the architectural decision behind transversal priority 1:

- the first real downstream promotion should be `daily_adjusted`;
- then a reusable mass-reconciliation layer around `split_normalized`;
- and only after that should higher-threshold consumers like `execution_simulator`, `rl_allowed`, or `live_downstream_candidate` be opened.

## v0.4.18 - first `daily_adjusted` materializer scaffolded and smoke-tested

### Added

- `scripts/materialize_daily_adjusted.py`
- `01_foundations/contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md`
- `01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md`

### Notes

This is the first executable landing of transversal priority 1.

It does not yet mean full production promotion.

It means:

- `daily_adjusted` now has a real materialization path;
- the layer has a first explicit contract and schema;
- and a smoke test over `ticker=A` succeeded with temporary output under `C:\\tmp\\daily_adjusted_smoke`.

## v0.4.19 - official landing proposal and pilot registry for `daily_adjusted`

### Added

- `01_foundations/module_contracts/daily_adjusted_operational_landing_v0_1.md`
- `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`

### Notes

This fixes the first concrete operational proposal for `daily_adjusted`:

- canonical root: `E:\\TSIS\\data\\ohlcv_daily_adjusted`
- mirrored physical layout from `D:\\ohlcv_daily`
- incremental materialization strategy with provenance
- first pilot consumer: daily return labels
- second target: `backtest_core`

The same update also makes explicit that:

- `daily_adjusted` closes the slow economic truth layer;
- the project core remains intraday and raw-observed;
- and a later `1m_split_normalized` discipline will be required so intraday ML/backtests do not learn split/reverse-split jumps as false alpha.

## v0.4.20 - exact incremental promotion plan for `daily_adjusted`

### Added

- `01_foundations/module_contracts/daily_adjusted_incremental_materialization_plan_v0_1.md`

### Notes

This fixes the concrete step order for promoting `daily_adjusted`:

- smoke test
- semantic pilot on real corporate-action tickers
- first real consumer
- incremental expansion
- and only after that, possible full-universe promotion

## v0.4.21 - first explicit semantic pilot manifest for `daily_adjusted`

### Added

- `01_foundations/dataset_registry/daily/daily_adjusted_pilot_manifest_v0_1.csv`
- `01_foundations/module_contracts/daily_adjusted_pilot_manifest_v0_1.md`

### Notes

The pilot is not random.

It explicitly mixes:

- reverse splits
- split-plus-dividend cases
- dividend-only cases
- and a no-event control

so the first semantic validation can check both:

- that the adjusted layer changes when it should;
- and that it stays neutral where no corporate action exists.

## v0.4.22 - refined pilot validated and first real consumer defined for `daily_adjusted`

### Added

- `01_foundations/module_contracts/daily_adjusted_pilot_results_v0_2.md`
- `01_foundations/module_contracts/daily_return_labels_consumer_contract_v0_1.md`
- `01_foundations/dataset_registry/daily/daily_adjusted_pilot_manifest_v0_2.csv`

### Notes

The refined semantic pilot `v0_2` is now explicitly recorded as validated.

This also fixes the first concrete downstream target for `daily_adjusted`:

- daily return labels built from `c_adjusted`

with initial horizons:

- `ret_1d`
- `ret_3d`
- `ret_5d`

## v0.4.12 - `bad_data` marks `size<=0` directly in the top panel

### Changed

- `scripts/inspection/trades/trades_case_panel.py`
- regenerated:
  - `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`

### Notes

Cases with:

- `size <= 0`

are now marked directly in the top price panel with a red `X`.

This complements the structural-integrity panel and makes the invalid trade row visually locatable inside the tape.

## v0.4.13 - `bad_data` gains universe map and exact invalid-row evidence

### Changed

- `scripts/inspection/trades/export_trades_family_casepacks.py`
- `01_foundations/inspection_dossiers/trades/build_trades_inspection_pack.md`
- regenerated:
  - `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/bad_data/bad_data_cases_v0_1.md`

### Notes

`bad_data` now starts with two universe-level layers:

- full `57f` acceptance distribution
- internal `bad_data` hard-signature distribution

and structural-integrity cases now expose exact evidence, not just aggregate warnings:

- invalid rows with:
  - `timestamp`
  - `price`
  - `size`
  - `exchange`
  - `conditions`
- duplicate groups with exact `timestamp/price/size`

This closes the gap identified in cases like `WSBF`, where price looked almost normal but the real rejection cause lived in tape integrity rather than visible price geometry.

## v0.4.14 - `trades` gets full-universe inspection notebook and global metrics module

### Added

- `scripts/inspection/trades/trades_universe_panel.py`
- `01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb`

### Notes

This adds a second interactive layer for `trades`, complementary to the existing case-level notebook.

The new layer is population-first and works over the full `57f/full_clean_fast_same_schema` universe.

It exports and displays, inline in the notebook:

- final acceptance distribution
- yearly acceptance mix
- scale-bucket mix by label
- hard-signature mix by label
- outside-daily severity by label
- outside-1m severity by label
- duplicate severity by label
- odd-lot severity by label
- 1m-reference coverage by label
- review rehabilitation waterfall

This closes a previous weakness: inspectors could see many cases, but they still lacked a modern, ambitious, executable map of the entire `trades` universe.

## v0.4.15 - `trades` global notebook executed and scope clarified

### Changed

- `01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb`

### Notes

The notebook was executed and saved with embedded outputs.

Its scope is now stated explicitly inside the notebook:

- it runs on the `lt1b` universe
- materialized in `57f/full_clean_fast_same_schema`

This avoids a dangerous ambiguity between:

- the audited `lt1b` production universe
- and a hypothetical all-cap universe outside this certification scope

## v0.4.16 - `trades` global readout and fine-grained universe cuts

### Added

- `01_foundations/inspection_dossiers/trades/trades_global_universe_readout_v0_1.md`

### Changed

- `scripts/inspection/trades/trades_universe_panel.py`
- `01_foundations/inspection_dossiers/trades/trades_universe_inspection_notebook_v0_1.ipynb`

### Notes

The global `trades` universe layer is no longer only a coarse summary.

It now includes fine-grained cuts for:

- `bad_data` by visual subfamily
- `review_microstructure` by dominant texture
- `reference_scale_mismatch` by scale bucket
- `review` by internal rehabilitation severity

The notebook was re-executed so these new sections remain embedded with outputs.

This closes another weakness:

- inspectors can now move from the full-universe map
- to fine-grained population structure
- before they drop into file-level casepacks.

## v0.4.9 - `trades` rules explained line by line

### Added

- companion compacto de reglas:
  - `01_foundations/module_contracts/trades_rules_explained_line_by_line.md`

### Notes

Este documento reescribe la policy de `trades` como:

- una regla por linea,
- agrupada por secciones,
- con formulas y cortes cuando existen.

Su funcion es ayudar a inspectores y agentes cuando necesiten:

- ver todas las reglas de `trades` de una vez,
- sin perder los cortes cuantitativos,
- y sin depender de una explicacion larga en prosa.

## v0.4.10 - `daily` and `quotes` explanatory companions

### Added

- `01_foundations/module_contracts/daily_acceptance_policy_explained.md`
- `01_foundations/module_contracts/daily_rules_explained_line_by_line.md`
- `01_foundations/module_contracts/quotes_acceptance_policy_explained.md`
- `01_foundations/module_contracts/quotes_rules_explained_line_by_line.md`

### Notes

This closes the symmetry with `trades`.

From now on, the three main audited families:

- `daily`
- `quotes`
- `trades`

have:

- a formal policy layer,
- an explanatory companion,
- and a compact line-by-line rule inventory.

## v0.4.11 - Transversal policy symmetry closed

### Added

- `01_foundations/module_contracts/pipeline_price_view_policy_explained.md`
- `01_foundations/module_contracts/pipeline_price_view_rules_line_by_line.md`
- `01_foundations/module_contracts/price_semantics_rules_line_by_line.md`
- `01_foundations/module_contracts/external_price_comparison_rules_line_by_line.md`

### Notes

This closes the institutional symmetry of the main transversal policies.

The module now has, across both dataset-level and transversal policies:

- a formal layer
- an explanatory layer where needed
- and a compact line-by-line rule inventory for fast inspection

## v0.4.8 - Policy explanation standard

### Added

- nuevo estandar transversal:
  - `01_foundations/module_contracts/policy_explanation_standard.md`
- primer companion explicativo especifico de politica de aceptacion:
  - `01_foundations/module_contracts/trades_acceptance_policy_explained.md`

### Notes

Este hito institucionaliza una regla general:

- una policy formal no basta por si sola;
- toda policy operativa importante debe tener una capa explicativa que diga:
  - que significa cada estado;
  - que pregunta responde;
  - que pregunta no responde;
  - que error metodologico evita;
  - y que consecuencia operativa tiene.

Tambien deja enlazada esa regla desde:

- `inspection_dossier_model.md`
- `trades_label_taxonomy_and_cut_policy.md`
- `trades_consumption_policy.md`
- `README.md`
- `AGENTS.md`

## v0.4.7 - Quotes cerrado con lectura poblacional y muestra good representativa

### Added

- cierre institucional de `quotes` mediante:
  - `01_foundations/inspection_dossiers/quotes/good_justification/quotes_good_cases_v0_1.md`
  - `01_foundations/inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md`
- activacion completa del scope `good` en:
  - `scripts/inspection/quotes/quotes_case_panel.py`
- evidencia poblacional global regenerada en:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/global_policy/`

### Notes

Este hito deja `quotes` cerrado en dos planos separados y obligatorios:

- evidencia poblacional global del universo auditado;
- evidencia forense de las familias abiertas `review` y `bad`.

Tambien deja explicitamente declarado que:

- la bolsa `review + bad` traslada exactamente los `79` casos abiertos del historico `v2`;
- la franja `good` no se documenta como enumeracion exhaustiva del universo bueno;
- se documenta como muestra historica representativa para justificar las familias buenas principales.

## v0.4.6 - Policy transversal por pipeline para price views

### Added

- policy transversal de asignacion de vistas de precio por pipeline/departamento:
  - `01_foundations/module_contracts/pipeline_price_view_policy.md`

### Notes

Este hito aterriza la semantica de precio en reglas operativas concretas para:

- vendor audit y forensic reconciliation
- execution research
- signal research diario
- portfolio valuation
- ML microestructural
- ML daily / labels de retorno
- comparacion con plataformas externas

Ademas deja enlazada esa policy desde:

- `daily_dataset_contract_v0_1.md`
- `quotes_dataset_contract_v0_1.md`
- `daily_consumption_policy.md`
- `quotes_consumption_policy.md`

## v0.4.5 - Vista adjusted reusable institucionalizada

### Added

- primera implementacion reusable de la vista `adjusted` en:
  - `src/data/price_views.py`
- nuevo test de secuencia metodologica:
  - `tests/test_price_views.py`
- export publico de `apply_adjusted_view` en:
  - `src/data/__init__.py`

### Notes

Este hito cierra la primera version reusable de la secuencia institucional correcta:

- `raw`
- `split_normalized`
- `adjusted`

La implementacion actual de `adjusted`:

- primero normaliza por splits;
- despues aplica la cadena futura de dividendos sobre esa base ya split-normalized;
- y deja `adjusted_proxy` como capa diagnostica separada, no como sustituto de `adjusted`.

Queda explicitamente documentado que:

- la vista `adjusted` ya existe y es reusable;
- pero su alcance actual cubre la primera capa institucional seria del modulo, no una reproduccion total de todas las cadenas vendor-specific posibles;
- la extension futura a stock dividends, spin-offs u otros eventos complejos sigue pendiente.

## v0.4.4 - Primera implementacion reusable de price views

### Added

- primera capa reusable de price views en:
  - `src/data/price_views.py`
- tests iniciales de price views en:
  - `tests/test_price_views.py`

### Notes

Este hito no cierra aun la vista `adjusted` institucional final.

Si deja materializado por primera vez, fuera del dossier de `quotes`, una implementacion reusable de:

- `split_normalized`
- `adjusted_proxy`

La motivacion fue evitar que la semantica de corporate actions quedara atrapada dentro de scripts de inspeccion locales.

Ademas, se deja explicitamente anotado un matiz de lectura importante de `quotes`:

- los `15 bad` y `64 review` de los dossiers actuales no representan todos los `HARD_FAIL` del universo;
- representan solo los casos abiertos y representativos que el flujo historico `v2` llevo al inspector final;
- el universo total auditado sigue conteniendo una masa mucho mayor de `PASS`, `SOFT_FAIL` y `HARD_FAIL`, ya resumida en los artefactos historicos de severidad y taxonomia.

## v0.4.2 - Politica transversal de semantica de precio y ajustes

### Added

- politica transversal institucional de vistas de precio:
  - `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`
- refuerzo bibliografico e institucional de la politica transversal:
  - CRSP
  - Kenneth French Data Library
  - Lopez de Prado
  - Gu/Kelly/Xiu
  - AQR
  - Andrew Lo

### Notes

Este hito fija a nivel de modulo:

- la separacion entre `quotes_raw`, `trades_raw`, `daily_raw`, `split_normalized`, `adjusted` y `adjusted_proxy`;
- la diferencia entre precio de senal, precio de ejecucion y precio de valoracion;
- la regla de uso de series ajustadas en backtest y ML;
- y la forma correcta de reconciliar discrepancias con plataformas externas.

La politica queda enlazada desde:

- `external_price_comparison_caveats.md`
- `inspection_dossier_model.md`
- `daily_dataset_contract_v0_1.md`
- `quotes_dataset_contract_v0_1.md`

Ademas, deja fijada una norma metodologica adicional:

- toda decision operativa futura sobre semantica de precio, ajuste, comparacion externa, backtest o ML debe incluir respaldo cientifico o institucional suficiente dentro del documento que la establezca.

## v0.4.3 - Infraestructura general de datos y pausa metodologica explicita de quotes

### Added

- topologia general de almacenamiento y estado objetivo:
  - `01_foundations/module_contracts/data_storage_topology_and_target_state.md`
- inventario general de familias de evento y referencia con ejemplos reales:
  - `01_foundations/module_contracts/event_families_and_reference_inventory.md`
- registro institucional de vistas de precio:
  - `01_foundations/module_contracts/price_views_registry.md`
- metodologia general de corporate actions y ajustes:
  - `01_foundations/module_contracts/corporate_actions_adjustment_methodology.md`

### Notes

Este hito deja explicitamente anotado que:

- el stack ya contiene mucho mas que market data bruto;
- existen capas reales de `dividends`, `splits`, `reverse splits`, `ticker_change`, `halts`, `ipos`, `news`, `economic`, `financial`, `short_interest`, `short_volume`, `ticker_types`, `exchanges` e identidad temporalizada;
- y el modulo debe tratarlas como infraestructura general, no como detalles locales de `daily` o `quotes`.

Ademas se deja constancia de una pausa metodologica parcial en `quotes`:

- el bloque no se abandona;
- se aparta temporalmente parte del refinamiento local porque la semantica de precio y ajustes ya exige una solucion transversal reusable.

## v0.4.1 - Quotes inspection packs y dossiers review/bad activados

### Added

- exportador institucional de packs de evidencia de `quotes`:
  - `scripts/inspection/quotes/quotes_case_panel.py`
- capa global de policy visual para `quotes` en:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/global_policy/`
- exportacion de packs por caso para:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/review/`
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/bad/`
- manifiestos generados:
  - `quotes_global_policy_manifest.csv`
  - `quotes_review_case_packs_manifest.csv`
  - `quotes_bad_case_packs_manifest.csv`
- primer dossier humano `review` de `quotes`:
  - `01_foundations/inspection_dossiers/quotes/flagged_case_evidence_packs/quotes_review_cases_v0_1.md`
- primer dossier humano `bad` de `quotes`:
  - `01_foundations/inspection_dossiers/quotes/bad_case_evidence_packs/quotes_bad_cases_v0_1.md`

### Notes

Este hito ya no solo fija contrato y policy de `quotes`; activa evidencia visual institucional reutilizable.

La exportacion actual de `quotes` cubre:

- capa global de distribucion/policy;
- packs por caso `review`;
- packs por caso `bad`;
- e incrusta, cuando existe, la imagen historica de certificacion junto al pack nuevo.

La franja `good` de `quotes` queda pendiente para la siguiente iteracion.

## v0.4.0 - Quotes contractual base y sesion de mercado institucionalizadas

### Added

- regla horizontal de alcance de sesion para market data:
  - `01_foundations/module_contracts/market_session_scope.md`
- taxonomia exacta y politica de corte de `quotes`:
  - `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md`
- contrato alto nivel de `quotes`:
  - `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md`
- policy de consumo de `quotes`:
  - `01_foundations/data_consumption_policies/quotes_consumption_policy.md`
- schema contract canonico de `quotes`:
  - `01_foundations/canonical_schemas/quotes/quotes_schema_contract.md`
- documento de validators de `quotes`:
  - `01_foundations/validators/quotes/quotes_validators.md`
- registry entry institucional de `quotes`:
  - `01_foundations/dataset_registry/quotes/quotes_registry_entry.yaml`

### Notes

Este hito no reaudita `quotes`.

Promueve a capa contractual institucional la evidencia historica ya cerrada del bloque y fija ademas una regla horizontal de sesion:

- `premarket -> regular -> afterhours`
- `04:00-20:00 America/New_York`

La lectura contractual de `quotes` queda cerrada sobre una regla clave:

- el contexto causal puede explicar el episodio;
- pero no rehabilita automaticamente la calidad local del libro.

## v0.2.0 - Primer dataset institucional real formalizado

### Added

- primer dataset contract institucional real del modulo:
  - `daily_dataset_contract_v0_1.md`
- primera policy de consumo institucional real para dataset:
  - `daily_consumption_policy.md`
- primer schema contract canonico real de dataset:
  - `daily_schema_contract.md`
- primer documento de validators institucionales reales para dataset:
  - `daily_validators.md`
- primera registry entry institucional real:
  - `daily_registry_entry.yaml`
- primera instancia completa del circuito:
  - `evidencia preservada -> contrato -> policy -> schema -> validators -> registry`

### Notes

Este hito no toca:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Formaliza `daily` como primer objeto institucional real construido sobre evidencia auditada y certificada ya existente.

## v0.3.0 - Modelo canonico de inspeccion institucional iniciado

### Added

- modelo canonico general de `inspection dossier` para el modulo:
  - `inspection_dossier_model.md`
- primera estructura de dossier de inspeccion especifica para `daily`
- primer `daily_inspection_readout_v0_1.md`
- documento inicial de construccion del inspection pack de `daily`
- arbol base para:
  - `good_justification`
  - `flagged_case_evidence_packs`
  - `bad_case_evidence_packs`
  - `coverage_case_evidence_packs`
  - `evidence_assets`

### Notes

Este hito fija el metodo general con el que `daily`, `quotes`, `trades`, `1m` y otros bloques deberan presentar evidencia a inspectores humanos y agentes.
No sustituye notebooks historicos ni closeouts.
Introduce la capa institucional de presentacion e inspeccion de evidencia.

## v0.1.0 - Fundacion local del modulo formalizada

### Added

- baseline de gobernanza local mediante `README.md`
- contrato local de agentes mediante `AGENTS.md`
- restricciones operativas locales mediante `LOCAL_RULES.md`
- regla explicita de preservacion de evidencia historica de auditoria y certificacion
- proteccion explicita de no tocar para:
  - `01_research/01_auditoria_RAW_DATA/`
  - `data/`
  - `run/`
  - `runs/`
- direccion explicita de consolidacion institucional para el modulo 01
- reconocimiento formal de `01_foundations/` como nueva capa operativa institucional que debe construirse al lado del arbol actual de research

### Notes

Este hito no reorganiza los arboles historicos de research ni de datos.
Establece la gobernanza necesaria para institucionalizar conocimiento auditado sin destruir lineage ni memoria cientifica.

## 2026-05-25 | trades foundations start

- created `01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md`
- created `01_foundations/contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md`
- created `01_foundations/data_consumption_policies/trades_consumption_policy.md`
- created `01_foundations/inspection_dossiers/trades/build_trades_inspection_pack.md`
- documented that `trades` must be interpreted through three layers: population snapshot, file-acceptance methodology sample, and full-closeout `57f`
- documented the crucial difference between the `380`-file methodological sample and the final full `<1B>` closure
- recorded full final `57f` label counts, including the residual `bad_data` tail and the extremely narrow `good` tail
- created `01_foundations/canonical_schemas/trades/trades_schema_contract.md`
- created `01_foundations/validators/trades/trades_validators.md`
- created `01_foundations/dataset_registry/trades/trades_registry_entry.yaml`
- anchored the trades registry and contracts to the real local `57f` full-closeout cache under `runs/backtest/trades_v2_materialized`
- documented that the methodological `380`-file sample is explanatory authority but not a replacement for the final `57f` full-closeout counts

## 2026-05-25 | Certification review promoted

- Added `01_foundations/module_contracts/auditoria_and_certification_source_hierarchy.md`.
- Documented the correct hierarchy between `auditoria/` and `certification/` for `daily`, `quotes`, and `trades`.
- Recorded that `certification/daily` and especially `certification/trades` contain more advanced recovery and usage semantics than current simplified foundations summaries.
- Recorded that `certification/quotes` complements the promoted foundations layer with stronger artifact mapping and certification framing.
- Recorded that `global_metrics` is a critical cross-block authority, but may need drift checks against newer local caches before counts are promoted as final truth.

## 2026-05-25 | Daily certification semantics aligned

- Refined `daily_inspection_readout_v0_1.md` to distinguish the visual inspection partition from the final certification state that combines quality and coverage.
- Updated `build_daily_inspection_pack.md` to require an explicit `coverage_case_evidence_packs` layer and to preserve the historical `001..007` coverage images as institutional evidence.
- Tightened `daily_dataset_contract_v0_1.md` and `daily_consumption_policy.md` so `daily` is no longer read as a simple `good / review / bad` block but as a two-axis final certification system.

## 2026-05-25 | Trades certification semantics aligned

- Refined `trades_dataset_contract_v0_1.md` so foundations now reflects the source hierarchy `auditoria -> certification -> foundations` explicitly.
- Elevated the final trades certification states `good / recoverable_with_flag / review_not_rehabilitated / bad` above the raw file-label vocabulary.
- Refined `trades_consumption_policy.md` to map file labels into final certification states instead of treating the label list as the final operational truth.
- Expanded `build_trades_inspection_pack.md` to record the existing certification images and to require a future trades inspection stack that separates population stress, file labels and final certification states.

## 2026-05-25 - Daily coverage visual closeout

- Promovida la evidencia historica `001.png` a `007.png` de `auditoria/daily/img` al cierre institucional de foundations.
- Creado `01_foundations/inspection_dossiers/daily/coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`.
- Fijadas dos familias visuales de coverage en `daily`:
  - familia A alineada, compatible con `recoverable_without_penalty`;
  - familia B de desalineacion moderada, compatible con `recoverable_with_flag`.
- Actualizado `daily_inspection_readout_v0_1.md` para que `daily` deje de presentar la cobertura como deuda pendiente y pase a tratarla como evidencia ya integrada.

## 2026-05-25 - Trades inspection stack promoted

- Promoted `certification/trades/img/*.png` into `01_foundations/inspection_dossiers/trades/evidence_assets/historical_assets/`.
- Created `trades_population_readout_v0_1.md` to separate population stress from file-level decisions.
- Created `trades_file_acceptance_readout_v0_1.md` to document exactly what the `380`-file methodological sample proves and what it cannot prove.
- Created `trades_review_cases_v0_1.md`, `trades_bad_cases_v0_1.md` and `trades_good_cases_v0_1.md` using the strongest historical representative images.
- Created `trades_inspection_readout_v0_1.md` as the final institutional inspection synthesis for the block.
- Updated `build_trades_inspection_pack.md` to reflect that the initial foundations inspection stack now exists and future work is refinement, not greenfield scaffolding.
## 2026-05-25 - Trades `good` bucket interpretation clarified

- strengthened the `trades` readouts to explain that the tiny `good` share (`80` historical files in certification; `106` in current `57f` aggregate) must not be read as "almost all trades data is bad";
- documented explicitly that `good` measures only the pristine tail where `trades`, `daily`, and `1m` align almost perfectly;
- documented that the economically usable mass of `trades` is expected to live mainly in `recoverable_with_flag`, not in `good`;
- anchored that interpretation in `certification/trades/12_trades_good.md` and the final recovery policy.

## 2026-05-25 - Trades next-step handoff recorded

- recorded the next high-value operational step for `trades` in `build_trades_inspection_pack.md`;
- the pending task is to rematerialize the rehabilitation rule on `57f/full_clean_fast_same_schema`;
- the goal is to quantify how much of the current `review` mass would now pass into `recoverable_with_flag`;
- this was explicitly recorded because that number is more informative than the tiny `good` share when judging the real usable mass of the `trades` block.

## 2026-05-26 - Trades inspection notebook added in `01_foundations`

- created `01_foundations/inspection_dossiers/trades/trades_inspection_notebook_v0_1.ipynb` as a user-facing inspection notebook;
- added `scripts/inspection/trades/trades_case_panel.py` as the reusable widget selector for `trades`;
- the selector lets the user choose `capa`, `bucket` and `caso` over the promoted historical evidence;
- translated the `trades` build/inspection entry-point material to castellano so the new interactive layer does not drift in language from the rest of the module.

## 2026-05-26 - Trades family-semantics rule strengthened

- recorded explicitly in the `trades` inspection plan and readout that each case family must be explained as a semantic, causal and operational family;
- documented that future `trades` dossiers must not rely on bucket names, file names or raw attributes alone;
- required each family explanation to cover meaning, shared signature, methodological error avoided, pipeline impact and institutional decision consequence.

## 2026-05-26 - Trades stratified sampling policy recorded

- created `trades_sampling_strategy_v0_1.md` under `01_foundations/inspection_dossiers/trades/`;
- fixed the rule that future `trades` case packs must be built from enumeracion completa or muestra estratificada por familia, not from ad-hoc examples;
- documented per-family stratification variables for:
  - `reference_scale_mismatch`
  - `review_microstructure`
  - `review_no_1m_reference`
  - `review_1m_reference_alignment`
  - `review`
  - `bad_data`
  - `good`

## 2026-05-26 - General evidence-explanation rule formalized

- formalized in `inspection_dossier_model.md` the rule that every graph, table, example and evidence layer must explain:
  - `que muestra`
  - `responde`
  - `no responde`
  - `consecuencia`
- propagated the rule to the local `AGENTS.md` and `README.md` so future agents treat it as a general inspection norm, not a one-off preference from a single block.
### 2026-05-26 | trades | muestra_380 ya con panel rico comparable

- `scripts/inspection/trades/trades_case_panel.py` deja de mostrar `muestra_380` como preview tabular simple y pasa a renderizar un panel rico por caso.
- El panel ahora cruza:
  - `trades raw`,
  - referencia `daily`,
  - referencia `1m`,
  - y concentracion temporal del conflicto.
- El notebook `01_foundations/inspection_dossiers/trades/trades_inspection_notebook_v0_1.ipynb` queda actualizado para explicarlo en castellano.
- La distincion entre `population`, `case_pack` y `muestra_380` se mantiene por semantica de evidencia, pero `muestra_380` ya no debe sentirse como una capa visualmente inferior.
### 2026-05-27 | trades | rehabilitacion de review rematerializada sobre 57f real

- La politica historica de recuperacion de `trades` deja de apoyarse solo en el parcial `57e/full_clean`.
- Se recalcula la regla estricta y la extendida sobre el cache canonico real:
  - `root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema`
- Resultado sobre `review`:
  - `review_total = 4,851,211`
  - `strict_recoverable = 3,327,955` (`68.6005%`)
  - `strict_residual = 1,523,256`
  - `extended_recoverable = 3,505,290` (`72.2560%`)
  - `extended_residual = 1,345,921`
- Implicacion institucional:
  - la masa util real de `trades` es mucho mayor que `good`;
  - pero la vision optimista del parcial `57e` (`85.89%` rehabilitable estricto) ya no puede presentarse como cierre operativo del bloque.

### 2026-05-27 | trades | recuperacion por familia propagada a policy y readouts intermedios

- `trades_consumption_policy.md` ya no documenta solo la rehabilitacion de `review`, sino tambien la recuperacion operativa provisional de:
  - `review_microstructure`
  - `review_1m_reference_alignment`
- `trades_population_readout_v0_1.md` ahora explica que la masa util real del bloque vive sobre todo en la parte rehabilitable de `review` y familias vecinas, no en la cola `good`.
- `trades_file_acceptance_readout_v0_1.md` ahora conecta explicitamente la muestra metodologica `380` con los conteos reales de recuperacion sobre `57f`.
- Con esto, la lectura de `trades` ya no depende solo del readout final para entender:
  - cuanta masa es recuperable hoy;
  - que parte sigue como `review_not_rehabilitated`;
  - y por que la muestra metodologica y el cierre final cumplen funciones distintas.

### 2026-05-27 | trades | manifests estratificados materializados sobre 57f

- se creo `scripts/inspection/trades/build_trades_stratified_sample_manifests.py`;
- el script materializa manifests reproducibles por familia sobre `57f/full_clean_fast_same_schema`;
- se generaron en `01_foundations/inspection_dossiers/trades/evidence_assets/stratified_samples/`:
  - `review`: `60`
  - `reference_scale_mismatch`: `60`
  - `review_microstructure`: `60`
  - `bad_data`: `60`
  - `review_no_1m_reference`: `60`
  - `review_1m_reference_alignment`: `60`
  - `good`: `106` (enumeracion completa)
- se actualizo `trades_sampling_strategy_v0_1.md` para reflejar que `review_no_1m_reference` y `review_1m_reference_alignment` ya no deben tratarse como buckets diminutos en el cierre real;
- y se promovio esta muestra al plan y al readout final para que la siguiente etapa parta de manifests fijos y no de ejemplos elegidos a mano.

### 2026-05-27 | trades | casepacks amplios por familia ya exportados

- se creo `scripts/inspection/trades/export_trades_family_casepacks.py`;
- el exportador reutiliza el panel rico file-level del selector de `trades` y lo guarda como `.png` por caso;
- se generaron los dossiers amplios por familia en `01_foundations/inspection_dossiers/trades/family_case_evidence_packs/`:
  - `bad_data`: `60` imagenes
  - `good`: `106` imagenes
  - `reference_scale_mismatch`: `60` imagenes
  - `review`: `60` imagenes
  - `review_1m_reference_alignment`: `60` imagenes
  - `review_microstructure`: `60` imagenes
  - `review_no_1m_reference`: `60` imagenes
- se creo el indice:
  - `family_casepacks_index_v0_1.md`
- con esto, `trades` ya no depende solo de:
  - ejemplos historicos curados,
  - ni del notebook interactivo;
- tambien tiene una capa exportada amplia y reproducible por familia para lectura del inspector.

### 2026-05-27 | trades | `bad_data` dividido en subfamilias visuales y lectura por imagen endurecida

- se formaliza en `inspection_dossier_model.md` una regla mas fuerte:
  - la explicacion de una imagen no puede salir solo de bucket + metricas;
  - debe salir de la lectura visual real del panel;
  - y si el panel no demuestra la causalidad principal, el dossier debe decirlo y pedir una visualizacion complementaria.
- en `trades`, `bad_data` deja de tratarse como familia visual unica:
  - subfamilia de colapso de escala/rango;
  - subfamilia de integridad estructural del tape.
- cuantificacion sobre `57f`:
  - `trade_price_outside_daily_range`: `9,606` (`60.53%`)
  - `scale_bucket_vw = nan`: `4,247` (`26.76%`)
  - `negative_or_zero_size_rows`: `695` (`4.38%`)
  - `duplicate_excess_ratio_gt_hard_cap`: `1,329` (`8.37%`)
  - componente estructural sin conflicto diario fuerte: `204` (`1.29%`)
- se endurecio la lectura de:
  - `ASTI 2007-12-24`
  - `DCTH 2005-12-29`
  - `WSBF 2009-08-14`
- conclusion importante:
  - `ASTI` y `DCTH` ya quedan bien justificados por el panel actual como `bad_data` de colapso de escala/rango;
  - `WSBF` puede seguir siendo `bad_data`, pero el panel actual no demuestra bien su causalidad y exige un panel adicional de integridad (`size <= 0`, duplicados, filas invalidas).

### 2026-05-27 | trades | `bad_data` reexportado con panel de integridad y comentarios por subfamilia

- `trades_case_panel.py` ahora anade un tercer panel operativo de `Integridad estructural del tape` con:
  - `size <= 0`
  - `size NA`
  - `price NA`
  - `dup rows`
- la lectura file-level de `bad_data` ya no es generica:
  - clasifica cada caso en subfamilias visuales;
  - usa comentarios distintos para colapso de escala/rango, integridad estructural, dano mixto y conflictos ralos;
  - y documenta cuando el panel de precio no demuestra por si solo la causalidad del rechazo.
- se ha reexportado `bad_data_cases_v0_1.md` completo (`60` casos) con esta logica nueva.

### 2026-05-29 | price views | primer consumidor real de `daily_adjusted` ya materializado

- se ejecuto `scripts/materialize_daily_return_labels.py` sobre la fuente oficial piloto:
  - `E:\TSIS\data\ohlcv_daily_adjusted`
- se materializo la salida operativa en:
  - `E:\TSIS\data\daily_return_labels`
- layout confirmado por `ticker/year`, por ejemplo:
  - `E:\TSIS\data\daily_return_labels\ticker=A\year=2005\day_aggs_A_2005_labels.parquet`
- columnas verificadas en parquet real:
  - `c_adjusted`
  - `ret_1d`
  - `ret_3d`
  - `ret_5d`
  - `label_source_view`
  - `label_contract`
- resumen del piloto:
  - `A`: `22` files / `5327` rows
  - `AAME`: `22` / `4949`
  - `ABEO`: `12` / `2693`
  - `ABIO`: `16` / `3925`
  - `ABTX`: `8` / `1758`
  - `BBW`: `22` / `5327`
  - `CASS`: `22` / `5241`
  - `CVLY`: `20` / `4420`
  - `SELF`: `11` / `2548`
  - `SGC`: `22` / `5199`
- con esto, `daily_adjusted` deja de ser solo semantica documentada y queda conectado a un consumidor real reproducible de labels diarios de retorno.

### 2026-05-29 | price views | contrato minimo de `1m_split_normalized` ya fijado

- se formalizo la siguiente capa intradia prioritaria despues de `daily_adjusted`:
  - `ohlcv_1m_split_normalized`
- se anadieron:
  - `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
  - `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- queda fijado que:
  - esta capa corrige escala mecanica por split entre sesiones;
  - no sustituye a `1m raw`;
  - no es todavia un `1m_adjusted` economico completo;
  - y debe promocionarse incrementalmente por `ticker-month` bajo demanda del consumidor real.

### 2026-05-29 | price views | `daily_adjusted` orientado ya a full-universe y piloto semantico de `1m_split_normalized` fijado

- se anadio:
  - `01_foundations/module_contracts/daily_adjusted_full_universe_promotion_plan_v0_1.md`
- queda fijado que `daily_adjusted` ya tiene madurez suficiente para apuntar a cobertura full-universe `2005-2026`;
- la deuda pendiente ya no es semantica sino promocion operativa disciplinada.
- se anadieron tambien:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`
  - `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_pilot_manifest_v0_1.md`
- queda fijado que el siguiente paso de `1m_split_normalized` no es full-universe inmediato, sino:
  - piloto semantico con `forward split`, `reverse split` y controles;
  - seleccionado por cobertura real en `D:\ohlcv_1m`;
  - y con unidad `ticker-month`.

### 2026-05-29 | price views | lote real del piloto `1m_split_normalized` ya seleccionado

- se cruzo cobertura real de:
  - `D:\ohlcv_1m`
  - `D:\ohlcv_daily`
  - y fuentes maestras de `splits`
- se fijo un lote minimo de `10` casos, alineado con la escala del piloto de `daily_adjusted`:
  - `4` `reverse split`
  - `4` `forward split`
  - `2` `control`
- artefactos creados:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
  - `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`
- casos seleccionados:
  - `BXRX 2022-12`
  - `COSM 2022-12`
  - `CEI 2022-12`
  - `BNGO 2025-01`
  - `EFSH 2025-01`
  - `SAVA 2023-12`
  - `PD 2006-03`
  - `LIVE 2014-02`
  - `BXRX 2022-11` control
  - `BNGO 2025-02` control

### 2026-05-29 | price views | piloto `1m_split_normalized` ya materializado y leido semanticamente

- se creo:
  - `scripts/materialize_1m_split_normalized.py`
- se materializo el piloto en:
  - `E:\TSIS\data\ohlcv_1m_split_normalized`
- se genero el resumen:
  - `E:\TSIS\data\ohlcv_1m_split_normalized\_split_normalized_materialization_summary.csv`
- se documento la lectura semantica en:
  - `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md`
- hallazgo importante fijado:
  - un control pre-evento puede y debe seguir teniendo `future_split_factor != 1`;
  - un control post-evento debe quedar neutro;
  - y la capa protege contra shocks mecanicos de split entre sesiones sin reemplazar `1m raw`.

### 2026-05-29 | price views | readout visual del piloto `1m_split_normalized` ya exportado

- se creo:
  - `scripts/inspection/minute/export_1m_split_normalized_pilot_readout.py`
- se exporto:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`
- se generaron `10` imagenes de auditoria visual en:
  - `01_foundations/inspection_dossiers/1m_split_normalized/images/`
- cada caso muestra:
  - `1m raw` del mes completo
  - `1m split_normalized` del mes completo
  - ventana focalizada alrededor del evento o ancla
  - trayectoria diaria de `future_split_factor`
- con esto, la validacion de `1m_split_normalized` ya no depende solo de tablas y texto contractual; tambien queda auditada visualmente caso por caso.

### 2026-05-29 | price views | primer consumidor recomendado de `1m_split_normalized` ya fijado

- se anadieron:
  - `01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md`
  - `01_foundations/module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md`
  - `01_foundations/module_contracts/intraday_regime_features_operational_landing_v0_1.md`
  - `01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml`
- queda fijado que el primer consumidor natural de `1m_split_normalized` no es:
  - `execution_simulator`
  - ni RL
  - ni una policy final de entrada/salida
- sino una capa de `intraday_regime_features` que:
  - use `1m_split_normalized` para comparaciones cross-session
  - use `1m raw` para estado local de la sesion
  - y deje la microestructura fina para una fase posterior con `quotes_raw` y `trades_raw`.

### 2026-06-02 | governance | `module_contracts` ya tiene indice maestro e indices por dominio

- se anadieron:
  - `01_foundations/module_contracts/README.md`
  - `01_foundations/module_contracts/daily_contracts_index.md`
  - `01_foundations/module_contracts/quotes_contracts_index.md`
  - `01_foundations/module_contracts/trades_contracts_index.md`
  - `01_foundations/module_contracts/ohlcv_1m_contracts_index.md`
  - `01_foundations/module_contracts/transversal_contracts_index.md`
- se crearon, todavia vacias, las carpetas destino de una futura migracion fisica:
  - `module_contracts/daily/`
  - `module_contracts/quotes/`
  - `module_contracts/trades/`
  - `module_contracts/minute/`
  - `module_contracts/transversal/`
  - `module_contracts/consumers/`
  - `module_contracts/governance/`
- queda fijado que la reorganizacion fisica no se hace todavia y que cualquier migracion futura debe priorizar no romper referencias desde markdowns, notebooks, readouts y agentes.

### 2026-06-02 | price views | cierre inspector final de `1m_split_normalized` ya consolidado

- se anadieron:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
  - `scripts/inspection/minute/build_1m_split_normalized_inspection_notebook.py`
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb`
- el notebook queda ejecutado con outputs y enlaza:
  - contrato
  - formula
  - piloto semantico
  - consumidor minimo real
- con ello `1m_split_normalized` deja de estar solo defendido por contrato y tablas; tambien queda presentado como paquete inspector navegable.

### 2026-06-02 | price views | auditoria exhaustiva full-universe de splits en `1m` ya ejecutada

- se creo:
  - `scripts/inspection/minute/audit_1m_split_full_universe.py`
- se generaron:
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_cases.csv`
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_cases.parquet`
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_status_summary.csv`
  - `01_foundations/inspection_dossiers/1m_split_normalized/evidence_assets/full_universe_split_audit/full_universe_split_event_audit_meta.csv`
- resultados:
  - `total_event_cases = 3335`
  - `PASS = 2280`
  - `FAIL = 0`
  - `NO_PRE_COVERAGE = 164`
  - `NO_POST_COVERAGE = 151`
  - `NO_1M_COVERAGE = 740`
- conclusion institucional fijada:
  - el `100%` de los casos plenamente auditables pasa;
  - los no-`PASS` observados son limites de cobertura y no fallos semanticos de la capa.

### 2026-06-02 | price views | notebook interactivo full-universe para auditoria de splits en `1m` ya disponible

- se creo:
  - `scripts/inspection/minute/build_1m_split_full_universe_audit_notebook.py`
- se genero:
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb`
  - `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- el notebook no usa PNGs como interfaz principal; permite al inspector seleccionar cualquier caso del universo auditado por:
  - `status`
  - `ticker`
  - `evento`
- y visualizar inline:
  - metadata del caso
  - serie `raw`
  - serie `split_normalized`
  - trayectoria de `future_split_factor`
  - lectura tecnica del estado de auditoria

### 2026-06-02 | quotes | readout poblacional reescrito con lectura numerica grafico por grafico

- se reescribio:
  - `01_foundations/inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md`
- la nueva version ya no solo explica intencion y semantica de cada panel; ahora cuantifica explicitamente:
  - peso de las familias dominantes
  - masa real de la cola dura
  - diferencia entre severidad, taxonomia y open buckets
  - y por que una familia visualmente extrema puede ser pequena mientras otra mas pequena puede ser economicamente mas peligrosa
- esto deja `quotes` mas cerca del estandar analitico ya usado en `trades`.

### 2026-06-02 | quotes | auditoria de integridad de la bolsa abierta `review/bad` ya ejecutada

- se creo:
  - `scripts/inspection/quotes/audit_quotes_open_casepacks.py`
- se generaron:
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/open_casepacks_audit/quotes_open_casepacks_audit_summary.csv`
  - `01_foundations/inspection_dossiers/quotes/evidence_assets/open_casepacks_audit/quotes_open_casepacks_audit_summary.parquet`
  - `01_foundations/inspection_dossiers/quotes/quotes_open_casepacks_audit_v0_1.md`
- resultados:
  - `review`: `64` esperados, `64` en manifest, `64` en markdown, `64` con assets completos, `PASS`
  - `bad`: `15` esperados, `15` en manifest, `15` en markdown, `15` con assets completos, `PASS`
- conclusion institucional fijada:
  - la bolsa abierta de `quotes` no contiene casos perdidos ni casos anadidos ad hoc;
  - queda cerrada con integridad de coverage y de assets respecto al pool historico abierto.

### 2026-06-02 | governance | snapshot transversal `v0_2` ya refleja el nuevo estado de cierre

- se creo:
  - `01_foundations/module_contracts/foundations_transversal_final_review_v0_2.md`
- y `v0_1` queda enlazado hacia `v0_2` como snapshot historico previo.
- `v0_2` fija explicitamente:
  - que `quotes` ya no tiene solo buen cierre semantico, sino tambien auditada la integridad de su frontera abierta;
  - que `1m` ya tiene cerrada exhaustivamente la deuda de splits sobre el universo auditable;
  - y que las deudas restantes viven mas en promocion operacional, uniformidad final y alcance que en definicion base.

### 2026-06-02 | governance | compatibilidad futura de paths en `module_contracts` ya preparada

- se anadio al `README` de `module_contracts` una seccion explicita de:
  - compatibilidad de paths y referencias;
  - regla de resolucion de rutas antiguas;
  - y obligacion de usar mapa oficial en vez de heuristica.
- se creo:
  - `01_foundations/module_contracts/module_contracts_migration_map_v0_1.md`
- el mapa deja preparado:
  - origen -> destino previsto;
  - agrupacion por dominios futuros;
  - y la nota institucional de que cualquier documento futuro que cite paths antiguos debe resolverlos mediante este mapa si la migracion fisica ya se hubiera ejecutado.

### 2026-06-02 | governance | pre-auditoria real de referencias a `module_contracts` ya exportada

- se creo:
  - `scripts/inspection/governance/audit_module_contracts_references.py`
  - `01_foundations/module_contracts/module_contracts_reference_pre_audit_v0_1.md`
- se exportaron:
  - `01_foundations/module_contracts/evidence_assets/module_contracts_reference_audit/module_contracts_reference_hits.csv`
  - `01_foundations/module_contracts/evidence_assets/module_contracts_reference_audit/module_contracts_reference_summary.csv`
  - `01_foundations/module_contracts/evidence_assets/module_contracts_reference_audit/module_contracts_reference_sources.csv`
- resultados agregados:
  - `reference_hits_total = 188`
  - `unique_source_files = 41`
  - `unique_target_documents = 55`
- targets mas sensibles por volumen de referencias:
  - `policy_explanation_standard.md` -> `20` referencias en `20` archivos
  - `price_semantics_and_adjustment_policy.md` -> `13` referencias en `10` archivos
  - `external_price_comparison_caveats.md` -> `9` referencias en `7` archivos
  - `pipeline_price_view_policy.md` -> `8` referencias en `8` archivos
- con esto, la futura migracion de `module_contracts` ya no parte de intuicion: queda cuantificada su superficie de ruptura potencial.

### 2026-06-03 | governance | plan de ejecucion segura de migracion de `module_contracts` ya preparado para otro agente

- se creo:
  - `01_foundations/module_contracts/module_contracts_migration_execution_plan_v0_1.md`
- y se enlazo desde:
  - `01_foundations/module_contracts/README.md`
- el plan deja preparado:
  - orden por fases;
  - lotes de riesgo;
  - checklist de entrada, ejecucion y salida;
  - criterio de parada;
  - y reglas de handoff para que otro agente pueda ejecutar la migracion sin empezar desde cero ni mover todo de golpe.

### 2026-06-03 | daily | auditoria de estado full-universe de `daily_adjusted` ya ejecutada

- se creo:
  - `scripts/inspection/daily/audit_daily_adjusted_full_universe.py`
  - `01_foundations/inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md`
- se exportaron:
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_full_universe_summary.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_ticker_activation_summary.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/daily_adjusted_file_activation_summary.csv`
- resultado clave:
  - `raw_tickers = 12494`
  - `adjusted_tickers = 10`
  - `raw_year_files = 125438`
  - `adjusted_year_files = 177`
  - `ticker_coverage_pct = 0.080038%`
  - `year_file_coverage_pct = 0.141106%`
- conclusion fijada:
  - la deuda abierta de `daily_adjusted` ya no es semantica de la capa, sino promocion operacional amplia y auditoria agregada posterior a esa expansion.

### 2026-06-03 | daily | cola compleja de corporate actions para `daily_adjusted` ya medida

- se creo:
  - `scripts/inspection/daily/audit_daily_adjusted_complex_actions_tail.py`
  - `01_foundations/inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md`
- se exportaron:
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_complex_actions_tail_summary.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_ticker_change_tail.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_non_cd_dividend_tail.csv`
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_complex_actions_tail_audit/daily_adjusted_complex_actions_type_summary.csv`
- resultado clave:
  - `ticker_event_rows_total = 3037`
  - `ticker_change_rows_within_daily_window = 2142`
  - `ticker_change_tickers_within_daily_window = 2072`
  - `dividend_non_cd_rows = 361`
  - `non_cd_dividend_rows_within_daily_window = 331`
  - `non_cd_dividend_tickers_within_daily_window = 184`
- conclusion fijada:
  - la frontera compleja visible hoy no es una masa estructurada de `spin-offs` o `stock dividends`;
  - la deuda material real es, sobre todo, `ticker_change` como problema de continuidad corporativa;
  - y la cola `dividend_type != CD` existe pero es pequena y aparece solo como `SC`.

### 2026-06-03 | 1m | reconciliacion explicita entre cierre raw historico, marco `lt1b` y cierre moderno de splits

- se creo:
  - `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`
- el documento fija explicitamente:
  - que el proyecto institucional moderno si vive en marco `lt1b`;
  - que el cierre historico raw de `1m` sigue siendo valido en policy y causalidad;
  - pero que sus porcentajes historicos deben declararse como `full-scope` salvo recalculo nominal `<1B>`;
  - y que el cierre nuevo de `ohlcv_1m_split_normalized` no contradice ese cierre raw, sino que resuelve la deuda especifica de splits.

### 2026-06-03 | 1m | arranque del recalculo raw `1m` sobre universo `<1B>` explicito

- se creo:
  - `scripts/inspection/minute/audit_1m_raw_lt1b_closeout.py`
  - `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- el recalculo queda definido para:
  - reutilizar los buckets historicos raw de `1m`;
  - filtrarlos por ticker + ventana PTI del corte canonico `<1B>`;
  - y exportar conteos y porcentajes compatibles ya con el alcance moderno del proyecto.

### 2026-06-03 | 1m | cierre cuantitativo del recálculo raw `1m` sobre universo `<1B>` explicito

- se actualizan:
  - `scripts/inspection/minute/audit_1m_raw_lt1b_closeout.py`
  - `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`
- el script ya reconstruye la taxonomia fina `vw_*` directamente desde las metricas historicas guardadas en `rescue_schema_plus_vw.parquet`
- el recalculo `<1B>` queda exportado con conteos finales reales:
  - `lt1b_current_1m_rows = 334660`
  - `good = 46652 (13.940118%)`
  - `review = 75245 (22.484014%)`
  - `bad = 212763 (63.575868%)`
- a partir de aqui:
  - los porcentajes `full-scope` del closeout raw historico de `1m` siguen siendo antecedente metodologico;
  - pero las afirmaciones cuantitativas raw `1m` estrictamente `<1B>` deben citar este recalculo.

### 2026-06-04 | 1m | paquete inspector especifico para `schema_only` en raw `<1B>`

- se crean:
  - `scripts/inspection/minute/build_1m_schema_only_lt1b_inspection_notebook.py`
  - `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
  - `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`
- el notebook queda ejecutado con outputs y widgets para:
  - seleccionar firma de warning;
  - seleccionar ticker;
  - y seleccionar cualquier `year-month` del bloque `RESCUE_SCHEMA_ONLY`
- la lectura institucional que queda fijada es:
  - el `5.89%` no-`vw` no es una cola economica difusa;
  - esta dominado por `dataset_read_incompatible_schema` + `schema_merge_conflict_ticker_encoding`;
  - y debe leerse como problema de compatibilidad estructural / merge de schema.

### 2026-06-05 | daily | materializacion fisica full-universe de `daily_adjusted` completada

- se completo la materializacion fisica de `daily_adjusted` contra el universo diario raw:
  - raw input: `D:\ohlcv_daily`
  - adjusted output: `E:\TSIS\data\ohlcv_daily_adjusted`
- comprobacion fisica final:
  - `raw_files = 125438`
  - `adjusted_files = 125438`
  - `missing_outputs = 0`
  - `extra_adjusted_outputs = 0`
- la ejecucion final se cerro mediante runner seguro de reanudacion fisica:
  - no dependia de `_materialization_summary.csv` como checkpoint;
  - decidia completitud por presencia fisica de parquets por `ticker/year`;
  - y mantuvo `overwrite=False`, por lo que no reescribia parquets ya existentes.
- durante la ejecucion se detecto un bloqueo transitorio de escritura del volumen `E:` (`HFS Plus`); tras reabrir el volumen, el proceso retomo desde el primer ticker incompleto (`NKX`) y completo solo los anos faltantes.
- estado institucional fijado:
  - el computo full-universe de parquets `daily_adjusted` esta materialmente completo;
  - no queda proceso materializador activo;
  - la promocion semantica/contractual final todavia requiere ejecutar y registrar la auditoria full-universe correspondiente antes de llamar la capa `full-universe bueno`.

### 2026-06-05 | daily | `daily_adjusted` promovido full-universe tras auditoria contractual agregada

- se actualizo y ejecuto:
  - `scripts/inspection/daily/audit_daily_adjusted_full_universe.py`
  - `01_foundations/inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md`
- se regeneraron evidence assets bajo:
  - `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/`
- durante la auditoria se detecto un parquet ajustado invalido de `0` bytes:
  - `E:\TSIS\data\ohlcv_daily_adjusted\ticker=NHI\year=2007\day_aggs_NHI_2007_adjusted.parquet`
- el archivo invalido se preservo en cuarentena y se regenero solo el `ticker-year` afectado con `overwrite=False`:
  - `E:\TSIS\data\ohlcv_daily_adjusted\_quarantine_zero_byte_20260605\day_aggs_NHI_2007_adjusted.parquet.zero_bytes`
- resultado final de auditoria full-universe:
  - `raw_tickers_with_files = 12230`
  - `adjusted_tickers_with_files = 12230`
  - `raw_year_files = 125438`
  - `adjusted_year_files = 125438`
  - `missing_outputs = 0`
  - `extra_adjusted_outputs = 0`
  - `read_error_files = 0`
  - `files_missing_required_columns = 0`
  - `nonpositive_factor_rows = 0`
  - `null_factor_rows = 0`
  - `bad_price_view_rows = 0`
  - `missing_source_daily_file_rows = 0`
- se actualizo:
  - `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`
  - `01_foundations/module_contracts/layer_maturity_assessment_v0_1.md`
- estado institucional fijado:
  - `daily_adjusted` pasa de `Nivel 5 - Consumida` a `Nivel 6 - Promovida`;
  - queda activa como vista derivada diaria full-universe para verdad economica lenta;
  - no habilita automaticamente ejecucion, RL ni uso live.

### 2026-06-06 | additional | institucionalizacion del bloque auxiliar `<1B>`

- se migra a `01_foundations` la lectura institucional del bloque `additional`, preservando la evidencia historica de `01_research`;
- se crean contratos canonicos para:
  - `01_foundations/canonical_schemas/additional/additional_financials_schema_contract.md`
  - `01_foundations/canonical_schemas/additional/additional_corporate_actions_schema_contract.md`
  - `01_foundations/canonical_schemas/additional/additional_economic_schema_contract.md`
  - `01_foundations/canonical_schemas/additional/additional_ipos_schema_contract.md`
  - `01_foundations/canonical_schemas/additional/additional_news_schema_contract.md`
- se crea el dossier:
  - `01_foundations/inspection_dossiers/additional/additional_institutional_closeout_v0_1.md`
- se crea la policy:
  - `01_foundations/data_consumption_policies/additional_consumption_policy.md`
- se registra el contrato:
  - `01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md`
  - `01_foundations/dataset_registry/additional/additional_registry_entry.yaml`
- estado institucional fijado:
  - `additional` no queda obsoleto;
  - queda aceptado como bloque auxiliar compuesto para el universo `<1B>`;
  - `financials_core` y `economic` quedan como partes fuertes;
  - `news` e `ipos` quedan como overlays causales/contextuales con frontera `review`;
  - `corporate_actions_additional` queda secundario frente a `reference`;
  - `ratios` queda en `review` por cobertura efectiva baja.

### 2026-06-06 | short | institucionalizacion de `short` y `short_review`

- se institucionaliza la familia `short` como dataset auxiliar de contexto short-side, no como capa core limpia universal;
- se crean:
  - `01_foundations/canonical_schemas/short/short_interest_schema_contract.md`
  - `01_foundations/canonical_schemas/short/short_volume_schema_contract.md`
  - `01_foundations/inspection_dossiers/short/short_institutional_closeout_v0_1.md`
  - `01_foundations/data_consumption_policies/short_consumption_policy.md`
  - `01_foundations/contract_registry/dataset_contracts/short_dataset_contract_v0_1.md`
  - `01_foundations/dataset_registry/short/short_registry_entry.yaml`
- se fija que `E:\TSIS\data\short` es la raiz operativa actual:
  - `short_interest`: 4824 files presentes, 520048 filas;
  - `short_volume`: 4824 files presentes, 1430506 filas.
- se fija que `E:\TSIS\data\short_review\finra_short` es baseline official/free FINRA y provenance:
  - `short_interest`: 505745 filas, 4687 tickers, `2017-12-29 -> 2026-04-15`;
  - `short_volume`: 4689038 filas, 4623 tickers, `2018-08-01 -> 2026-04-29`.
- se preserva la decision de certificacion v2:
  - `CERTIFIED_OK = 1130`;
  - `CERTIFIED_OK_WITH_LIMITED_WINDOW = 738`;
  - `REVIEW_TICKER_REUSE = 761`;
  - `REVIEW_REFERENCE_CONFLICT = 2195`.
- estado institucional fijado:
  - `short` es util y debe preservarse;
  - `short_review` no es obsoleto, es evidencia/provenance y baseline FINRA;
  - no existe promocion full-history `2005-2026` limpia con fuentes official/free;
  - cualquier consumo debe preservar estado de certificacion, ventana valida y scope de fuente.

### 2026-06-06 | 1m | schema fisico y registry de `ohlcv_1m_split_normalized`

- se completa la documentacion fisica de la capa piloto `ohlcv_1m_split_normalized`:
  - `01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md`
- se actualiza:
  - `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- estado institucional fijado:
  - la capa ya no queda como `planned_contract_only`;
  - queda como `pilot_materialized_semantically_validated`;
  - la raiz operativa es `E:\TSIS\data\ohlcv_1m_split_normalized`;
  - existen `10` parquets piloto y un summary fisico;
  - no es materializacion full-universe ni sustituto de `1m raw`;
  - su uso correcto es comparabilidad intradia entre sesiones cuando hay frontera de split.
### 2026-06-06 | features | `intraday_regime_features` institucionalizada como consumidor piloto validado

- se completa la documentacion institucional minima de `intraday_regime_features_v0_1`:
  - `01_foundations/canonical_schemas/features/intraday_regime_features_schema_contract.md`
  - `01_foundations/data_consumption_policies/intraday_regime_features_consumption_policy.md`
  - `01_foundations/contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md`
- se actualiza:
  - `01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml`
- estado institucional fijado:
  - pasa de `planned_contract_only` a `pilot_semantic_validation_consumer`;
  - queda como `Nivel 3 - Pilotada`;
  - la raiz operativa es `E:\TSIS\data\intraday_regime_features`;
  - existen `8` parquets piloto y `243` filas `ticker-day` observadas;
  - no es full-universe `<1B>` ni feature layer productiva global;
  - su rol actual es demostrar que las features cross-session deben usar `1m_split_normalized` para no aprender falsos gaps/shocks de splits.
- se anade el plan de promocion disciplinada a `<1B>`:
  - `01_foundations/module_contracts/intraday_regime_features_lt1b_promotion_plan_v0_1.md`
- queda fijado que la futura ruta `<1B>` debe ser separada del piloto y no sobrescribir:
  - `E:\TSIS\data\intraday_regime_features`
- se explicita la lectura de fase:
  - hoy es validacion arquitectonica y consumidor piloto de normalizacion;
  - no es feature productiva ni dependencia bloqueante del backtest base;
  - las preguntas de regimen que permite formular pertenecen a una fase posterior de `features/states`.
### 2026-06-06 | daily | `daily_return_labels` documentado como target layer piloto

- se completa la documentacion institucional minima de `daily_return_labels_v0_1`:
  - `01_foundations/canonical_schemas/daily/daily_return_labels_schema_contract.md`
  - `01_foundations/data_consumption_policies/daily_return_labels_consumption_policy.md`
  - `01_foundations/contract_registry/dataset_contracts/daily_return_labels_dataset_contract_v0_1.md`
  - `01_foundations/module_contracts/daily_return_labels_lt1b_promotion_plan_v0_1.md`
- se actualiza:
  - `01_foundations/dataset_registry/daily/daily_return_labels_registry_entry.yaml`
- estado institucional fijado:
  - la capa sigue como `pilot_materialization` / `pilot_target_layer`;
  - la raiz operativa piloto es `E:\TSIS\data\daily_return_labels`;
  - existen `177` parquets, `10` tickers y `41487` rows observados en summary;
  - no es full-universe `<1B>`;
  - `ret_1d`, `ret_3d`, `ret_5d` son targets/outcomes, no features;
  - la futura promocion `<1B>` debe ir a raiz separada y cerrar coverage + anti-leakage.
### 2026-06-06 | universes | universo operativo `<1B>` institucionalizado como capa transversal

- se institucionaliza el corte operativo `<1B>` fuera de `reference`, en familia propia `universes`:
  - `01_foundations/canonical_schemas/universes/lt1b_universe_schema_contract.md`
  - `01_foundations/data_consumption_policies/lt1b_universe_consumption_policy.md`
  - `01_foundations/contract_registry/dataset_contracts/lt1b_universe_dataset_contract_v0_1.md`
  - `01_foundations/dataset_registry/universes/lt1b_universe_registry_entry.yaml`
- artefacto canónico:
  - `runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet`
- cifras fijadas:
  - `lt1b_tickers = 4824`
  - `active_lt_1b_last_classifiable = 2476`
  - `inactive_died_lt_1b = 2348`
  - `panel_end_date = 2026-03-09`
- regla institucional:
  - toda afirmación `<1B>` debe filtrar por `ticker` y por intersección con ventana PTI (`first_seen_date`, `last_observed_date`);
  - este corte no es `E:\TSIS\data\reference`;
  - tampoco sustituye un futuro `population_target_pti` diario fully point-in-time.

### 2026-06-06 | ohlcv_1m | `ohlcv_1m_raw` institucionalizado como foundation layer

- se cierra la deuda de homogeneidad documental de `ohlcv_1m_raw`, separandolo explicitamente de `ohlcv_1m_split_normalized`:
  - `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md`
  - `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml`
  - `01_foundations/data_consumption_policies/ohlcv_1m_raw_consumption_policy.md`
  - `01_foundations/validators/ohlcv_1m/ohlcv_1m_raw_validators.md`
- se actualiza:
  - `01_foundations/module_contracts/ohlcv_1m_contracts_index.md`
- evidencia institucional enlazada:
  - `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
  - `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
  - `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`
- cifras `<1B>` fijadas para el raw closeout:
  - `lt1b_tickers_reference = 4824`
  - `lt1b_current_1m_unique_tickers = 4822`
  - `lt1b_current_1m_unique_task_keys = 334660`
  - `good = 46652` (`13.940118%`)
  - `review = 75245` (`22.484014%`)
  - `bad = 212763` (`63.575868%`)
- estado institucional fijado:
  - `ohlcv_1m_raw` queda como raw foundation layer entendido y documentado;
  - no queda promovido como capa productiva global limpia;
  - `bad` queda restringido a uso forense;
  - `review` queda restringido a exploratorio/diagnostico declarado;
  - trabajo split-sensitive y features cross-session deben usar `ohlcv_1m_split_normalized`.

### 2026-06-06 | short_review | FINRA baseline/provenance institucionalizado como capa propia

- se separa `short_review` de `short` como capa documental propia, manteniendo su rol de baseline official/free FINRA y provenance:
  - `01_foundations/canonical_schemas/short_review/finra_short_interest_schema_contract.md`
  - `01_foundations/canonical_schemas/short_review/finra_short_volume_schema_contract.md`
  - `01_foundations/canonical_schemas/short_review/finra_short_provenance_schema_contract.md`
  - `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
  - `01_foundations/data_consumption_policies/short_review_consumption_policy.md`
  - `01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml`
- se enlaza desde:
  - `01_foundations/contract_registry/dataset_contracts/short_dataset_contract_v0_1.md`
  - `01_foundations/data_consumption_policies/short_consumption_policy.md`
- raiz operativa fijada:
  - `E:\TSIS\data\short_review\finra_short`
- artefactos FINRA fijados:
  - `short_interest_all_biweekly_finra.parquet`: `505745` filas, `4687` tickers, `2017-12-29 -> 2026-04-15`
  - `short_volume_all_daily_finra.parquet`: `4689038` filas, `4623` tickers, `2018-08-01 -> 2026-04-29`
- estado institucional fijado:
  - `short_review` no sustituye silenciosamente a `short`;
  - no prueba completitud official/free `2005-2026`;
  - debe usarse para source validation, coverage comparison, forensic review y features declaradas con scope/ventana;
  - manifests y logs quedan como provenance, no como features de modelo.

### 2026-06-07 | inspection_dossiers | README local de `daily` institucionalizado

- se crea el README operativo del dossier `daily`:
  - `01_foundations/inspection_dossiers/daily/README.md`
- se actualiza el README raiz de `inspection_dossiers` para enlazarlo dentro de la madurez relativa:
  - `01_foundations/inspection_dossiers/README.md`
- el README local fija de forma navegable:
  - diferencia entre `daily_core_v0_1` y `daily_adjusted_v0_1`;
  - separacion obligatoria entre `quality axis` y `coverage axis`;
  - estado full-universe promovido de `daily_adjusted`;
  - rol de `good_justification`, `flagged_case_evidence_packs`, `bad_case_evidence_packs`, `coverage_case_evidence_packs` y `evidence_assets`;
  - consumidores permitidos, restringidos y no habilitados automaticamente;
  - reglas para futuros agentes y mantenimiento documental.

### 2026-06-07 | inspection_dossiers | README local de `minute` institucionalizado

- se crea el README operativo del dossier `minute`:
  - `01_foundations/inspection_dossiers/minute/README.md`
- se actualiza el README raiz de `inspection_dossiers` para enlazarlo dentro de la madurez relativa:
  - `01_foundations/inspection_dossiers/README.md`
- el README local fija de forma navegable:
  - que `minute` documenta `ohlcv_1m_raw_v0_1`, no `ohlcv_1m_split_normalized`;
  - que el estado vigente es `institutional_raw_closeout_reconciled_lt1b`;
  - que los porcentajes raw `1m <1B>` validos salen del recalculo local, no del closeout historico `full-scope`;
  - que el estado refinado `<1B>` actual es `good = 46652`, `review = 75245`, `bad = 212763`;
  - que `RESCUE_SCHEMA_ONLY` no equivale a production-good;
  - que raw 1m no debe consumirse como capa productiva limpia ni para trabajo split-sensitive.

### 2026-06-07 | inspection_dossiers | paquete inspector profundo documentado

- se anade en el README raiz de `inspection_dossiers` una seccion explicita para inspectores humanos:
  - `01_foundations/inspection_dossiers/README.md`
- la nueva seccion fija que markdowns deben abrirse para comprender en profundidad:
  - `daily`
  - `quotes`
  - `trades`
- el paquete distingue:
  - entrada local del bloque;
  - readout institucional;
  - casepacks visuales `good`, `review/flagged`, `bad`;
  - coverage en `daily`;
  - auditoria de casepacks en `quotes`;
  - family casepacks amplios en `trades`.
- objetivo: que un inspector no tenga que inferir desde notebooks o assets sueltos que documentos visuales debe revisar.
