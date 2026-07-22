# Short Dataset Contract v0.1 - Modulo 01

## 1. Role

This contract defines the institutional role of short data inside module 01.

It covers:

- `E:\TSIS\data\short\short_interest`
- `E:\TSIS\data\short\short_volume`
- `E:\TSIS\data\short_review\finra_short`

## 2. Primary Semantics

Short data provides short-side pressure and crowding context:

- `short_interest`: slow biweekly crowding / days-to-cover
- `short_volume`: daily reported short-sale activity / venue-scope pressure

It is not:

- executable quote data
- trade tape
- complete consolidated shorting truth
- full 2005-2026 official/free history

## 3. Schema Contracts

- `01_foundations/canonical_schemas/short/short_interest_schema_contract.md`
- `01_foundations/canonical_schemas/short/short_volume_schema_contract.md`

`short_review` now has its own FINRA baseline schema contracts:

- `01_foundations/canonical_schemas/short_review/finra_short_interest_schema_contract.md`
- `01_foundations/canonical_schemas/short_review/finra_short_volume_schema_contract.md`
- `01_foundations/canonical_schemas/short_review/finra_short_provenance_schema_contract.md`

## 4. Consumption Policy

Operational consumption rules live in:

- `01_foundations/data_consumption_policies/short_consumption_policy.md`
- `01_foundations/data_consumption_policies/short_review_consumption_policy.md`

Dataset-specific `short_review` governance lives in:

- `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml`

## 5. Evidence Dossier

Institutional evidence lives in:

- `01_foundations/inspection_dossiers/short/short_institutional_closeout_v0_1.md`

## 6. Historical/Operational Evidence

Short review documents:

- [finra_short_build_status.md](</E:/TSIS/data/short_review/finra_short_build_status.md>)
- [research_short_sources.md](</E:/TSIS/data/short_review/research_short_sources.md>)
- [short_data_recovery_plan.md](</E:/TSIS/data/short_review/short_data_recovery_plan.md>)
- [finra_short README.md](</E:/TSIS/data/short_review/finra_short/README.md>)

Run evidence:

- `runs/backtest/short_downloads/lt1b_short_refresh/download_summary.json`
- `runs/backtest/short_data_audit/lt1b_short_refresh_audit/short_data_lt1b_ticker_coverage_audit_summary.json`
- `runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certification_summary.json`

## 7. Institutional Status

| Component | Status |
|---|---|
| local `short` download/file presence | complete for `<1B>` |
| `short_interest` schema | coherent |
| `short_volume` schema | coherent |
| lifecycle/reference certification | mixed |
| FINRA review layer | official/free baseline |
| full 2005-2026 official/free completeness | not certified |

## 8. Allowed Consumers

Allowed with certification restrictions:

- `research_only`
- `backtest_extended`
- `ml_flagged`
- `forensic_only`

Not automatically enabled:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 9. Verdict

Short data is accepted as an institutional auxiliary/event-context dataset, not as a clean universal core layer. Consumption must preserve certification status and source/window limitations.
