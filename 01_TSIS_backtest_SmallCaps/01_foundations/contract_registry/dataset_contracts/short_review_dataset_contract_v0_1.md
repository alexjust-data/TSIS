# Short Review Dataset Contract v0.1

## 1. Dataset Identity

- `dataset_id`: `short_review_finra_v0_1`
- `dataset_family`: `short_review`
- `physical_root`: `E:\TSIS\data\short_review\finra_short`
- `status`: `official_free_baseline_provenance`
- `registry_entry`: `01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml`
- `consumption_policy`: `01_foundations/data_consumption_policies/short_review_consumption_policy.md`

## 2. Role

`short_review` is the FINRA official/free baseline and provenance layer for the module's short-side context data.

It exists to:

- validate and contextualize `E:\TSIS\data\short`;
- preserve source evidence for FINRA short interest and short volume;
- support coverage comparisons and forensic review;
- define the official/free source limits of short data.

It is not:

- a silent replacement for `short`;
- proof of 2005-2026 full-history completeness;
- executable quote/trade data;
- consolidated market-wide shorting truth.

## 3. Schema Contracts

- `01_foundations/canonical_schemas/short_review/finra_short_interest_schema_contract.md`
- `01_foundations/canonical_schemas/short_review/finra_short_volume_schema_contract.md`
- `01_foundations/canonical_schemas/short_review/finra_short_provenance_schema_contract.md`

## 4. Source Lineage

Source documents and build notes:

- `E:\TSIS\data\short_review\finra_short_build_status.md`
- `E:\TSIS\data\short_review\research_short_sources.md`
- `E:\TSIS\data\short_review\short_data_recovery_plan.md`
- `E:\TSIS\data\short_review\finra_short\README.md`

Evidence dossier:

- `01_foundations/inspection_dossiers/short/short_institutional_closeout_v0_1.md`

## 5. Coverage Snapshot

FINRA short interest:

- rows: `505745`
- tickers: `4687`
- date range: `2017-12-29` to `2026-04-15`

FINRA short volume:

- rows: `4689038`
- tickers: `4623`
- date range: `2018-08-01` to `2026-04-29`

Comparison to local `short`:

- short volume intersection: `4623`
- short volume only local/Polygon: `201`
- short interest intersection: `4687`
- short interest only local/Polygon: `137`

## 6. Allowed Consumers

Allowed:

- `source_validation`
- `coverage_comparison`
- `forensic_review`
- `research_only`
- `backtest_extended` when source scope and windows are declared
- `ml_flagged` when source scope and windows are declared

Not automatically enabled:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 7. Known Limitations

- Official/free FINRA `short_volume` does not close the `2005-2018` gap.
- FINRA `short_interest` pre-modern semantics require caution.
- FINRA source scope must travel with all derived features.
- `short_volume_ratio` is source-scope, not universal market shorting pressure.
- Local-only tickers require review for identity, ticker reuse, provider coverage, or valid-window differences.

## 8. Verdict

`short_review` is accepted as an institutional official/free FINRA baseline and provenance layer. It should be preserved and cited whenever `short` is used, audited, compared, or promoted.
