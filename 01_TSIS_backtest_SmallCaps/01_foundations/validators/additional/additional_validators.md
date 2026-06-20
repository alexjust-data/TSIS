# Additional Validators

## Scope

This validator contract governs `additional_v0_1`.

`additional` is RAW vendor context data from Polygon, not one uniform analytical
dataset. Validation must therefore operate by subfamily:

- `financials_core`: income statements, balance sheets, cash-flow statements.
- `financials_ratios`: ratios.
- `news`: timestamped news/event context.
- `ipos`: listing and IPO event context.
- `corporate_actions_additional`: dividends, splits and ticker events.
- `economic`: macro date series.

The current inspection package lives in:

- `01_foundations/inspection_dossiers/additional/additional_inspection_readout_v0_2.md`
- `01_foundations/inspection_dossiers/additional/evidence_assets/quality_tables/additional_subfamily_quality_table_v0_2.csv`
- `01_foundations/inspection_dossiers/additional/evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv`

## Authorities

This validator must be read with:

- `contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md`
- `data_consumption_policies/additional_consumption_policy.md`
- `dataset_registry/additional/additional_registry_entry.yaml`
- `canonical_schemas/additional/additional_financials_schema_contract.md`
- `canonical_schemas/additional/additional_corporate_actions_schema_contract.md`
- `canonical_schemas/additional/additional_economic_schema_contract.md`
- `canonical_schemas/additional/additional_ipos_schema_contract.md`
- `canonical_schemas/additional/additional_news_schema_contract.md`
- `module_contracts/raw_data_authority_and_derivation_map.md`
- `module_contracts/additional_to_master_tables_policy_v0_1.md`

## Validation Unit

There is no single row key for the whole block.

Validation units are:

| Subfamily | Unit |
| --- | --- |
| financial statements | `ticker + period_end + filing_date + timeframe` |
| ratios | `ticker + date` |
| news | `ticker + published_utc + id` |
| IPOs | `ticker + listing_date + issuer_name` |
| dividends | `ticker + ex_dividend_date + id` |
| splits | `ticker + execution_date + id` |
| ticker events | `ticker + date + type` |
| economic | `dataset + date` |

## Required Checks

### Root And Provenance

The validator must check:

- active root exists: `E:/TSIS/data/additional`;
- expected subroots exist: `financials`, `corporate_actions`, `economic`, `ipos`, `news`;
- download evidence exists for ticker-based and macro refreshes;
- run evidence exists for the `20260405_additional_lt1b_coverage` audit;
- historical audit cache is readable but not modified.

### Schema

Each subfamily must be checked against its own schema contract.

The validator must not attempt blind directory-level merging across all
Additional subfamilies. Heterogeneous schema is expected.

### Empty Sentinel Semantics

Ticker-based Additional files may contain valid no-data sentinel rows:

- `ticker`
- `_empty`
- `_dataset`
- `_ingested_utc`

Files-present coverage is not enough. The validator must emit effective
non-empty coverage.

### Financial Statements

Required checks:

- `ticker` identity present;
- `period_end` parseable;
- `filing_date` parseable;
- `fiscal_year`, `fiscal_quarter`, `timeframe` coherent when present;
- no promotion to decision-time feature unless filing availability is respected.

Passing this check permits contextual use and quality-table use. It does not
promote fundamentals to primary alpha features.

### Ratios

Required checks:

- `ticker + date` key parseable;
- sparsity explicit;
- denominator or vendor-derived caveats preserved;
- no universal coverage assumption.

Ratios remain `review_sparse_snapshot` until a separate point-in-time and
coverage promotion exists.

### News

Required checks:

- `published_utc` parseable and timezone-aware;
- `news_date` derived consistently;
- `id` present when available;
- `ticker` request identity preserved separately from article ticker list;
- multi-ticker ambiguity flagged;
- market evidence used only as context, not causal proof.

News can support `news_flag`, event context and forensic review. It cannot prove
that the requested ticker caused or received the full article effect.

### IPOs

Required checks:

- `listing_date` parseable when present;
- `announced_date` fallback explicit when used;
- issuer identity preserved;
- sparse expectedness documented.

Sparse IPO coverage is not a failure by itself because most tickers are not IPO
events in the audited window.

### Corporate Actions Additional

Required checks:

- splits and dividends reconciled against `reference`;
- exact overlap and non-overlap buckets emitted;
- `ticker_events` treated as review taxonomy unless normalized separately;
- Additional corporate actions never override reference by default.

### Economic

Required checks:

- macro file present;
- date field parseable;
- date range emitted;
- macro/calendar scope explicit.

Economic series can support `calendar_table` and regime context. They cannot be
read as direct ticker-level causal evidence.

## Output Contract

A compliant validator or inspection build must emit, directly or indirectly:

- dataset identity and version;
- source roots and historical evidence roots;
- universe scope;
- subfamily quality table;
- master-table readiness table;
- corporate-actions reference reconciliation;
- news attribution summary;
- IPO context summary;
- physical root audit;
- run manifest;
- human-readable readout.

The current outputs are:

- `inspection_dossiers/additional/evidence_assets/run_manifest.json`
- `inspection_dossiers/additional/evidence_assets/quality_tables/additional_subfamily_quality_table_v0_2.csv`
- `inspection_dossiers/additional/evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/reference_reconciliation/additional_corporate_actions_reference_reconciliation_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/news_attribution/additional_news_attribution_quality_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/ipo_context/additional_ipo_context_quality_v0_1.csv`

## Acceptance States

Allowed states:

- `good_context_candidate`
- `good_review_attribution_aware`
- `good_review_sparse_event`
- `good_macro_context`
- `review_sparse_snapshot`
- `review_secondary_to_reference`

No aggregate `bad` family is assigned by the current evidence.

## Forbidden Conclusions

The validator must not conclude:

- Additional is a uniform dataset.
- Additional replaces `reference`.
- Additional replaces `daily`, `quotes`, `trades` or `ohlcv_1m`.
- Financial statement fields are decision-time features without filing-date
  logic.
- News is ticker-causal truth because it was downloaded under a ticker.
- Macro data proves ticker-level causality.
- Corporate actions in Additional can adjust prices when reference disagrees.

## Current Status

The validator is documented and backed by the executable inspection builder:

```text
scripts/inspection/additional/build_additional_inspection_pack.py
```

This is sufficient for institutional readout and CAPA 1 quality-table planning.
Full automated CI enforcement remains a future implementation step.
