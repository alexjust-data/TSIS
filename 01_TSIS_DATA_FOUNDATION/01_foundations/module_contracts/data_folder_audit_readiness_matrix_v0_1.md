# Data Folder Audit Readiness Matrix v0.1

## Purpose

This document is the mandatory entry point for agents that continue CAPA 1 data
foundation audits after the first strong families: `daily`, `quotes`, `trades`
and `minute`.

It answers four operational questions:

1. which physical folders exist under `E:/TSIS/data`;
2. which institutional family each folder maps to inside `01_foundations`;
3. which families are below, at, or still not equivalent to the `daily`,
   `quotes`, `trades` and `minute` inspection standard;
4. exactly what evidence must be produced before a family can be read as
   `>90%` institutional.

This is not a replacement for dataset-specific contracts. It is the work queue
and quality gate that prevents unaudited folders from being treated as
hedge-fund-grade inputs.

Evidence mode:

```text
graph_first_source_verified
```

Graphify was used to orient the document map. The current source files,
contracts, registries, validators and sampled physical paths were then checked
directly.

## Active Physical Root

The active target root for current module-01 data work is:

```text
E:/TSIS/data
```

Historical or specialized roots can still be valid inputs when a live contract
requires them, but new audits should start from `E:/TSIS/data` unless the
dataset-specific contract says otherwise.

Current top-level physical folders observed under `E:/TSIS/data`:

```text
Halts
additional
daily_return_labels
financial
images_Flash_Research
intraday_regime_features
ohlcv_1m
ohlcv_1m_split_normalized
ohlcv_daily
ohlcv_daily_adjusted
quotes
reference
regime_indicators
short
short_review
trades_ticks_prod_2005_2026
```

## Sampling Rule Used For This Matrix

This matrix uses only one representative file per top-level folder or semantic
subfolder.

This sampling is enough to identify the physical shape and map folders to
institutional families. It is not enough to promote a dataset. Promotion still
requires the full package defined in:

- `data_engineering_physical_audit_standard_v0_1.md`
- `inspection_dossier_model.md`
- `evidence_model.md`
- `layer_validation_standard_v0_1.md`
- `bad_evidence_and_rehabilitation.md`

## The Standard We Expect To Obtain

For every family below, the expected result is not "similar quality" in vague
terms. The expected result is this concrete package.

### 1. Physical Data-Engineering Audit

Required outputs:

- `inspection_dossiers/<family>/evidence_assets/sample_files/<family>_sample_file_manifest_v0_1.csv`
- `inspection_dossiers/<family>/evidence_assets/physical_root_audit/<family>_physical_root_audit_v0_1.csv`
- `inspection_dossiers/<family>/evidence_assets/physical_root_audit/<family>_physical_root_audit_v0_1.md`

Minimum columns or sections:

- physical root;
- sampled file;
- reader used;
- read status;
- row count;
- column list;
- physical/logical types;
- required-column conformance;
- unexpected columns;
- null rates for critical fields;
- duplicate key diagnostics;
- date/timestamp min and max;
- partition key vs payload key checks;
- file naming vs payload checks;
- source/provenance evidence;
- `expected / present / healthy / usable` state.

### 2. Dataset Contract Set

Required or explicitly not-applicable outputs:

- `canonical_schemas/<family>/...`
- `contract_registry/dataset_contracts/<family>_dataset_contract_v0_1.md`
- `data_consumption_policies/<family>_consumption_policy.md`
- `dataset_registry/<family>/<family>_registry_entry.yaml`
- `validators/<family>/<family>_validators.md`
- `module_contracts/<family>_contracts_index.md` when the family has multiple
  contracts or subfamilies.

Each contract must say:

- what the data is;
- what the data is not;
- raw/vendor/derived/feature/label/evidence class;
- allowed consumers;
- forbidden interpretations;
- authority hierarchy;
- expected use in CAPA 1 master tables, if any.

### 3. Human Inspection Dossier

Required outputs:

- `inspection_dossiers/<family>/README.md`
- `inspection_dossiers/<family>/<family>_inspection_readout_v0_1.md`
- casepacks under:
  - `good_justification/`
  - `flagged_case_evidence_packs/`
  - `bad_case_evidence_packs/`
  - `coverage_case_evidence_packs/`
  - or a documented reason why a bucket is not applicable.

Every meaningful image, chart, table card or casepack must include:

```text
What it shows
What it answers
What it does not answer
How an inspector should read it
What institutional decision it supports
What limit remains open
```

### 4. Quality Tables For CAPA 1

Required outputs:

- `inspection_dossiers/<family>/evidence_assets/quality_tables/<family>_subfamily_quality_table_v0_1.csv`
- `inspection_dossiers/<family>/evidence_assets/quality_tables/<family>_master_table_readiness_v0_1.csv`

These tables must be suitable as inputs or design evidence for:

- `data_quality_report`;
- `master_daily_table`;
- `master_intraday_table`;
- `symbol_master`;
- `corporate_actions_table`;
- `calendar_table`.

If a family cannot contribute to a master table, the table must say so and
explain why.

### 5. Reproducible Builder

Preferred location:

```text
scripts/inspection/<family>/build_<family>_inspection_pack.py
```

The builder must read active physical data and historical evidence where
relevant, then emit current evidence under `01_foundations/inspection_dossiers`.

## Current Folder Matrix

| E:/TSIS/data folder | Institutional identity | Current maturity/readiness | Required action |
| --- | --- | ---: | --- |
| `Halts` | `halts_v0_1` | `92%` | Keep as reference pattern; no immediate uplift unless roots change. |
| `additional` | `additional_v0_1` | `92% governance, not yet trades/quotes-grade by subfamily` | Finish subfamily DE audit and inspector package expansion before treating as fully equivalent to core families. |
| `daily_return_labels` | `daily_return_labels_v0_1` | `62%` | Needs anti-leakage validator, physical audit, label dossier and LT1B/full-universe promotion evidence. |
| `financial` | `financial_standalone_v0_1` or merge into `additional/financials` | `25%` | Needs decision of identity, contract, policy, registry, validator and full DE dossier. |
| `images_Flash_Research` | support visual archive, not market data | `unclassified` | Must be classified as evidence/support archive or moved out of active data root by explicit later decision. |
| `intraday_regime_features` | `intraday_regime_features_v0_1` | `66%` | Needs feature validator, physical audit, population dossier and no-alpha/no-label policy enforcement. |
| `ohlcv_1m` | `ohlcv_1m_raw_v0_1` | `82%` | Needs full physical root audit and global-readiness dossier before >90. |
| `ohlcv_1m_split_normalized` | `ohlcv_1m_split_normalized_v0_1` | `90% threshold` | Needs dedicated validator and consumption policy if promoted beyond split-event audit scope. |
| `ohlcv_daily` | `daily_core_v0_1` | `92%` | Keep as reference pattern; maintain raw-vs-adjusted separation. |
| `ohlcv_daily_adjusted` | `daily_adjusted_v0_1` | `100%` | Keep as reference pattern; do not use as raw replacement. |
| `quotes` | `quotes_core_v0_1` | `93%` | Keep as reference pattern. |
| `reference` | `reference_v0_1` | `90%` | Keep as reference pattern; extend only if new reference endpoints enter. |
| `regime_indicators` | `regime_indicators_v0_1` | `22%` | Needs almost full institutionalization from schemas to dossier. |
| `short` | `short_v0_1` | `74%` | Needs dedicated validator, FINRA/local reconciliation, physical audit and casepacks. |
| `short_review` | `short_review_finra_v0_1` | `76%` | Needs separate validator and separate dossier, not only shared `short` closeout. |
| `trades_ticks_prod_2005_2026` | `trades_raw_v0_1` | `90%` | Keep as reference pattern; finish editorial index debt only. |

## Family Work Items

### Additional

Physical root:

- `E:/TSIS/data/additional`

Sample files:

- `additional/economic/inflation.parquet`
- `additional/corporate_actions/dividends/ticker=AACT/dividends_AACT.parquet`
- `additional/financials/balance_sheets/ticker=AACT/balance_sheets_AACT.parquet`
- `additional/ipos/ipos/ticker=AACT/ipos_AACT.parquet`
- `additional/news/news/ticker=AACT/news_AACT.parquet`

Current `01_foundations` representation:

- `canonical_schemas/additional/`
- `contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md`
- `data_consumption_policies/additional_consumption_policy.md`
- `dataset_registry/additional/additional_registry_entry.yaml`
- `inspection_dossiers/additional/`
- `module_contracts/additional_contracts_index.md`
- `module_contracts/additional_to_master_tables_policy_v0_1.md`
- `validators/additional/additional_validators.md`

Required to reach inspector-grade closure:

- per-subfamily physical audit for `corporate_actions`, `economic`,
  `financials`, `ipos` and `news`;
- table explaining which fields can feed `data_quality_report`,
  `master_daily_table`, `symbol_master`, `corporate_actions_table` and
  `calendar_table`;
- richer inspector evidence for news attribution, IPO sparse context,
  financial filing coverage and corporate-action reconciliation against
  `reference`;
- explicit statement that `additional` is RAW vendor/context, not core
  market-data authority.

### Daily Return Labels

Physical root:

- `E:/TSIS/data/daily_return_labels`

Sample file:

- `daily_return_labels/ticker=A/year=2005/day_aggs_A_2005_labels.parquet`

Current `01_foundations` representation:

- `canonical_schemas/daily/daily_return_labels_schema_contract.md`
- `contract_registry/dataset_contracts/daily_return_labels_dataset_contract_v0_1.md`
- `data_consumption_policies/daily_return_labels_consumption_policy.md`
- `dataset_registry/daily/daily_return_labels_registry_entry.yaml`
- `module_contracts/daily_return_labels_consumer_contract_v0_1.md`
- `module_contracts/daily_return_labels_operational_landing_v0_1.md`
- `module_contracts/daily_return_labels_lt1b_promotion_plan_v0_1.md`

Missing:

- `validators/daily/daily_return_labels_validators.md`
- `inspection_dossiers/daily_return_labels/`

Required outputs:

- anti-leakage validator proving labels are never features at decision time;
- physical root audit with label horizons, nulls, date ranges and upstream
  `daily_adjusted` lineage;
- coverage table by ticker/year/horizon;
- readout explaining target semantics: outcome layer, not raw audit and not
  alpha;
- casepack showing at least clean label rows, missing-horizon rows and corporate
  action sensitive rows.

### Financial

Physical root:

- `E:/TSIS/data/financial`

Sample files:

- `financial/_audit/audit_summary.json`
- `financial/balance_sheets/ticker=A/balance_sheets_A.parquet`
- `financial/cash_flow_statements/ticker=A/cash_flow_statements_A.parquet`
- `financial/income_statements/ticker=A/income_statements_A.parquet`
- `financial/ratios/ticker=A/ratios_A.parquet`

Current `01_foundations` representation:

- `canonical_schemas/financial/`
- related but separate: `canonical_schemas/additional/additional_financials_schema_contract.md`

Missing:

- standalone dataset contract;
- standalone consumption policy;
- standalone dataset registry;
- standalone validator;
- standalone inspection dossier;
- explicit decision whether this is its own family or absorbed into
  `additional/financials`.

Required outputs:

- identity decision: `financial_standalone_v0_1` vs `additional_financials`;
- filing-date and period-end validation;
- point-in-time caveat for any future features;
- ratio denominator/nullability audit;
- coverage by statement type, ticker and fiscal period;
- master-table readiness statement for fundamentals columns.

### Intraday Regime Features

Physical root:

- `E:/TSIS/data/intraday_regime_features`

Sample file:

- `intraday_regime_features/ticker=BNGO/year=2025/day_features_BNGO_2025.parquet`

Current `01_foundations` representation:

- `canonical_schemas/features/intraday_regime_features_schema_contract.md`
- `contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md`
- `data_consumption_policies/intraday_regime_features_consumption_policy.md`
- `dataset_registry/features/intraday_regime_features_registry_entry.yaml`
- `inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`
- `module_contracts/intraday_regime_features_*`

Missing:

- `validators/features/intraday_regime_features_validators.md`
- full physical root audit;
- broad population dossier beyond pilot evidence.

Required outputs:

- feature-layer validator proving this is not a raw audit and not an alpha
  claim;
- lineage check to `ohlcv_1m_split_normalized`;
- coverage by ticker/date and feature family;
- null/outlier/drift report;
- casepacks showing usable days, coverage-limited days and excluded days;
- policy statement for `research_only`, `ml_flagged` and forbidden
  interpretations.

### OHLCV 1m Raw

Physical root:

- `E:/TSIS/data/ohlcv_1m`

Sample file:

- `ohlcv_1m/ticker=AAA/year=2005/month=01/minute_aggs_AAA_2005_01.parquet`

Current `01_foundations` representation:

- `canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md`
- `contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md`
- `data_consumption_policies/ohlcv_1m_raw_consumption_policy.md`
- `dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml`
- `validators/ohlcv_1m/ohlcv_1m_raw_validators.md`
- `inspection_dossiers/minute/`
- `module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`

Required to move above `90%`:

- full physical root audit for `E:/TSIS/data/ohlcv_1m`;
- global file-readability and schema-conformance summary;
- partition/payload ticker-year-month check;
- duplicate ticker-minute check;
- null and `vw` quality separation;
- updated readout explaining what is globally usable, LT1B-only usable,
  schema-only and not production-clean.

### OHLCV 1m Split Normalized

Physical root:

- `E:/TSIS/data/ohlcv_1m_split_normalized`

Sample file:

- `ohlcv_1m_split_normalized/ticker=BNGO/year=2025/month=01/minute_aggs_BNGO_2025_01_split_normalized.parquet`

Current `01_foundations` representation:

- `canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md`
- `contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
- `dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- `inspection_dossiers/1m_split_normalized/`
- `module_contracts/ohlcv_1m_split_normalized_*`

Missing or conditional:

- dedicated validator;
- dedicated consumption policy;
- explicit physical materialization audit if used beyond split-event scope.

Required outputs:

- validator for split factors, adjusted columns, invariant checks and
  provenance;
- physical audit of materialized files;
- readout separating event-audit pass from full-root production claim;
- policy defining when it can feed features or intraday states.

### Short

Physical root:

- `E:/TSIS/data/short`

Sample files:

- `short/short_interest/AACT.parquet`
- `short/short_volume/AACT.parquet`

Current `01_foundations` representation:

- `canonical_schemas/short/short_interest_schema_contract.md`
- `canonical_schemas/short/short_volume_schema_contract.md`
- `contract_registry/dataset_contracts/short_dataset_contract_v0_1.md`
- `data_consumption_policies/short_consumption_policy.md`
- `dataset_registry/short/short_registry_entry.yaml`
- `inspection_dossiers/short/short_institutional_closeout_v0_1.md`

Missing:

- `validators/short/short_validators.md`
- richer physical root audit;
- dedicated casepacks for local Polygon short data.

Required outputs:

- short-interest and short-volume arithmetic validation;
- ticker/date coverage table;
- FINRA/local reconciliation against `short_review`;
- source-window and provider-risk flags;
- casepacks for good, limited-window, provider-conflict, ticker-reuse and
  sparse-but-valid cases;
- explicit statement that short is context/crowding, not intraday causal proof.

### Short Review FINRA

Physical root:

- `E:/TSIS/data/short_review`

Sample files:

- `short_review/finra_short_build_status.md`
- `short_review/finra_short/README.md`

Current `01_foundations` representation:

- `canonical_schemas/short_review/finra_short_interest_schema_contract.md`
- `canonical_schemas/short_review/finra_short_volume_schema_contract.md`
- `canonical_schemas/short_review/finra_short_provenance_schema_contract.md`
- `contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `data_consumption_policies/short_review_consumption_policy.md`
- `dataset_registry/short_review/short_review_registry_entry.yaml`

Missing:

- `validators/short_review/short_review_validators.md`
- dedicated `inspection_dossiers/short_review/`

Required outputs:

- provenance validator for official/free FINRA baseline;
- file inventory and build-status audit;
- ticker/date coverage table;
- comparison table to local `short`;
- readout proving it is baseline/provenance, not a replacement for every short
  consumer.

### LT1B Universe

Physical root:

- no dedicated top-level `E:/TSIS/data/lt1b_universe` folder observed.
- logical family depends on reference/universe materializations and historical
  certification evidence.

Current `01_foundations` representation:

- `canonical_schemas/universes/lt1b_universe_schema_contract.md`
- `contract_registry/dataset_contracts/lt1b_universe_dataset_contract_v0_1.md`
- `data_consumption_policies/lt1b_universe_consumption_policy.md`
- `dataset_registry/universes/lt1b_universe_registry_entry.yaml`
- related evidence in `minute`, `trades`, `daily` and `halts` dossiers.

Missing:

- `validators/universes/lt1b_universe_validators.md`
- `inspection_dossiers/universes/lt1b_universe_inspection_readout_v0_1.md`

Required outputs:

- point-in-time membership audit;
- market-cap threshold methodology check;
- lifecycle and anti-survivorship evidence;
- expected coverage manifest for downstream families;
- explicit statement that current `lt1b_universe_v0_1` is an operational cut,
  not fully daily PTI membership unless proven.

### Regime Indicators

Physical root:

- `E:/TSIS/data/regime_indicators`

Sample files:

- `regime_indicators/etfs/DIA/day.parquet`
- `regime_indicators/indices/I_COMP/day.parquet`

Current `01_foundations` representation:

- `canonical_schemas/regime_indicators/regime_etf_bars_schema_contract.md`
- `canonical_schemas/regime_indicators/regime_index_bars_schema_contract.md`
- `canonical_schemas/regime_indicators/regime_metadata_schema_contract.md`
- `canonical_schemas/regime_indicators/regime_indicators_quality_notes.md`

Missing:

- dataset contract;
- consumption policy;
- registry entry;
- validator;
- inspection dossier;
- module contract defining relation to market regime context.

Required outputs:

- `contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md`
- `data_consumption_policies/regime_indicators_consumption_policy.md`
- `dataset_registry/regime_indicators/regime_indicators_registry_entry.yaml`
- `validators/regime_indicators/regime_indicators_validators.md`
- `inspection_dossiers/regime_indicators/regime_indicators_inspection_readout_v0_1.md`
- ETF/index coverage and date-range audit;
- timestamp/date sanity check;
- allowed-use statement: regime context only until validated as feature layer.

## Already Strong Reference Families

These families are not the immediate backlog, but they define the target
standard:

| Folder | Institutional reference |
| --- | --- |
| `ohlcv_daily` | `daily_core_v0_1`: validators, contract, policy, registry, visual dossiers and coverage logic. |
| `ohlcv_daily_adjusted` | `daily_adjusted_v0_1`: full-universe materialization and physical coverage audit. |
| `quotes` | `quotes_core_v0_1`: validators, casepacks, global policy visuals and good/review/bad taxonomy. |
| `trades_ticks_prod_2005_2026` | `trades_raw_v0_1`: file-level tape audit, population readout, file acceptance and family casepacks. |
| `Halts` | `halts_v0_1`: root audit, source reconciliation, event taxonomy and population visuals. |
| `reference` | `reference_v0_1`: identity/reference authority, but must remain distinct from price and context families. |

## Agent Rule

Before continuing any lower-maturity family, an agent must:

1. read this file;
2. read `data_engineering_physical_audit_standard_v0_1.md`;
3. read the dataset-specific contract, schema, policy, registry and dossier if
   they exist;
4. inspect at least one physical file per relevant folder/subfolder;
5. state whether the target family is RAW vendor, RAW market data, reference,
   context, derived ETL, feature, label or evidence;
6. write missing evidence into `01_foundations`, not into the frozen historical
   `01_research/01_auditoria_RAW_DATA` tree.

No family in this matrix should be promoted above `90%` only because it has a
schema or because a historical notebook exists. The promotion gate is:

```text
contract + schema + registry + policy + validator + physical audit + human dossier + evidence assets + explicit limits
```
