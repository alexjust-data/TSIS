# Additional Dataset Contract v0.1 - Modulo 01

## 1. Role

This contract defines `additional` as an auxiliary composite dataset block for module 01.

It covers:

- `E:\TSIS\data\additional\financials`
- `E:\TSIS\data\additional\corporate_actions`
- `E:\TSIS\data\additional\economic`
- `E:\TSIS\data\additional\ipos`
- `E:\TSIS\data\additional\news`

## 2. Primary Semantics

`additional` is not a single homogeneous analytical table.

It contains:

- fundamentals and ratios
- corporate action events
- IPO events
- news events
- macro/economic date series

The institutional unit depends on subblock:

- financial statements: `ticker + period_end + filing_date + timeframe`
- ratios: `ticker + date`
- corporate actions: `ticker + event_date + event_type/id`
- IPOs: `ticker + listing_date + issuer_name`
- news: `ticker + published_utc + id`
- economic: `dataset + date`

## 3. Source And Scope

The block was materialized from Polygon endpoints for the `<1B>` operating universe.

Materialization evidence:

- ticker universe: 4824 tickers
- ticker-based tasks: 43416
- ticker-based ok tasks: 43416
- ticker-based errors: 0
- macro tasks: 3
- macro ok tasks: 3
- macro errors: 0

## 4. Canonical Schema Contracts

- `01_foundations/canonical_schemas/additional/additional_financials_schema_contract.md`
- `01_foundations/canonical_schemas/additional/additional_corporate_actions_schema_contract.md`
- `01_foundations/canonical_schemas/additional/additional_economic_schema_contract.md`
- `01_foundations/canonical_schemas/additional/additional_ipos_schema_contract.md`
- `01_foundations/canonical_schemas/additional/additional_news_schema_contract.md`

## 5. Consumption Policy

Operational consumption rules live in:

- `01_foundations/data_consumption_policies/additional_consumption_policy.md`

## 6. Evidence Dossier

Institutional evidence lives in:

- `01_foundations/inspection_dossiers/additional/additional_institutional_closeout_v0_1.md`
- `01_foundations/inspection_dossiers/additional/additional_inspection_readout_v0_2.md`
- `01_foundations/inspection_dossiers/additional/evidence_assets/quality_tables/additional_subfamily_quality_table_v0_2.csv`
- `01_foundations/inspection_dossiers/additional/evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv`
- `01_foundations/validators/additional/additional_validators.md`
- `01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md`

Historical source evidence remains preserved under:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/`

Specific historical evidence links:

- [01_contrato_additional.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/01_contrato_additional.md)
- [02_diseno_implementacion_additional_v2.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/02_diseno_implementacion_additional_v2.md)
- [descarga_additional.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/descarga_additional.md)
- [03_additional_root_cause_audit_phase1_closeout.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/03_additional_root_cause_audit_phase1_closeout.md)
- [04_additional_causal_overlay_closeout.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md)
- [04_additional_closeout.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_closeout.md)

## 7. Allowed Consumers

Allowed with subblock restrictions:

- `research_only`
- `backtest_extended`
- `ml_flagged`
- forensic/causal review

Not automatically enabled:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Subblock-specific promotion is required before any stricter consumer is enabled.

## 8. Institutional Status

| Subblock | Status |
|---|---|
| `financials_core` | good |
| `financials_ratios` | review |
| `news` | good/review |
| `ipos` | good/review |
| `corporate_actions_additional` | review, secondary to reference |
| `economic` | good as macro dataset, review for ticker causality |

No aggregate `bad` family is currently assigned.

## 9. Non-Goals

This contract does not:

- replace `reference`
- replace `financial`
- certify ratios as complete
- certify multi-ticker news as ticker-causal truth
- promote macro data as direct ticker-level causality

## 10. Verdict

`additional` is accepted as an institutional auxiliary block. It must be preserved and consumed by subblock-specific rules.

## 11. CAPA 1 Use Boundary

`additional` is RAW vendor context by provenance.

It may enrich CAPA 1 outputs:

- `data_quality_report`
- `master_daily_table`
- `symbol_master`
- `corporate_actions_table`
- `calendar_table`
- indirect `master_intraday_table` context

It does not replace:

- `daily`
- `quotes`
- `trades`
- `ohlcv_1m`
- `reference`
- `halts`

The current master-table boundary is governed by:

- `01_foundations/module_contracts/additional_to_master_tables_policy_v0_1.md`
