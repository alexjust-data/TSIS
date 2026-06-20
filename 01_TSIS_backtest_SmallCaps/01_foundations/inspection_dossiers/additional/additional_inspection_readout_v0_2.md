# Additional Inspection Readout v0.2

## Scope

`additional_v0_1` is RAW vendor context data from Polygon. It includes financials, corporate actions, economic/macro series, IPOs and news.

This readout does not promote Additional into core market data. It promotes the inspection package that explains how Additional contributes to CAPA 1 data-quality and master-table design.

Visual inspection status:

```text
visual_complete
```

## Verdict

Additional is institutional as a governed RAW vendor context block with subfamily-specific restrictions.

It must not be consumed as one uniform dataset. Its subfamilies feed quality/context tables differently:

| target_table | additional_role | readiness | blocking_limit |
| --- | --- | --- | --- |
| data_quality_report | subfamily quality flags, coverage state, attribution risk, reference overlap | ready_for_contextual_quality_columns | Not a single uniform dataset; each subfamily must keep its state. |
| master_daily_table | news_flag, IPO age/listing context, financial context with filing-date guardrails, macro day overlays | partial_context_ready | No direct alpha/feature promotion without point-in-time and attribution controls. |
| master_intraday_table | event-time context for news/IPO/macro calendar only | indirect_context_only | Does not replace quotes, trades or 1m intraday market evidence. |
| symbol_master | issuer/listing/fundamental identity context | partial_context_ready | Reference identity remains primary authority. |
| corporate_actions_table | secondary reconciliation for dividends, splits and ticker_events | secondary_reconciliation_only | Reference corporate actions remain primary authority. |
| calendar_table | macro date series for inflation, expectations and treasury yields | macro_context_ready | Macro presence is not ticker-level causality. |

## Subfamily quality table

| dataset | dataset_family | quality_state | coverage_non_empty_pct | rows_total | master_table_destination |
| --- | --- | --- | --- | --- | --- |
| income_statements | financials_core | good_context_candidate | 99.772 | 242897 | master_daily_table context; data_quality_report |
| balance_sheets | financials_core | good_context_candidate | 99.772 | 136672 | master_daily_table context; symbol_master; data_quality_report |
| cash_flow_statements | financials_core | good_context_candidate | 99.71 | 242223 | master_daily_table context; data_quality_report |
| ratios | financials_ratios | review_sparse_snapshot | 46.269 | 4824 | data_quality_report; deferred context only |
| news | news | good_review_attribution_aware | 80.203 | 288093 | master_daily_table news_flag; event/context table; data_quality_report |
| ipos | ipos | good_review_sparse_event | 26.016 | 4850 | symbol_master listing context; master_daily_table ipo_age/ipo_flag; data_quality_report |
| dividends | corporate_actions_additional | review_secondary_to_reference | 26.078 | 49684 | corporate_actions_table reconciliation; data_quality_report |
| splits | corporate_actions_additional | review_secondary_to_reference | 38.889 | 6283 | corporate_actions_table reconciliation; data_quality_report |
| ticker_events | corporate_actions_additional | review_secondary_to_reference | 56.032 | 5158 | event/reference reconciliation; data_quality_report |
| inflation | economic | good_macro_context |  | 950 | calendar_table macro context; data_quality_report |
| inflation_expectations | economic | good_macro_context |  | 531 | calendar_table macro context; data_quality_report |
| treasury_yields | economic | good_macro_context |  | 16047 | calendar_table macro context; data_quality_report |

## Corporate actions reconciliation

| dataset | overlap_bucket | tickers | rows | overlap_rows | institutional_reading |
| --- | --- | --- | --- | --- | --- |
| dividends | reference_exact_overlap | 1253 | 1253 | 45968 | secondary confirmation; reference remains primary |
| dividends | reference_present_no_exact_overlap | 5 | 5 | 0 | review queue; do not override reference |
| splits | reference_exact_overlap | 1858 | 1858 | 3293 | secondary confirmation; reference remains primary |
| splits | reference_present_no_exact_overlap | 18 | 18 | 0 | review queue; do not override reference |
| ticker_events | reference_present_no_exact_overlap | 2703 | 2703 | 0 | review queue; do not override reference |

## News attribution

| news_link_bucket | events | tickers | mean_tickers_per_news | institutional_reading |
| --- | --- | --- | --- | --- |
| review_multi_ticker_ambiguous_news | 169154 | 3627 | 16.26471144637431 | high attribution risk; context only unless ticker attribution is explicit |
| news_near_market_anomaly | 98400 | 3103 | 1.0 | candidate event context with market evidence; still not causal proof |
| news_context_only | 18296 | 2798 | 28.048589855706165 | contextual news without nearby market anomaly |
| news_near_halt_market_event | 1268 | 707 | 1.0 | strongest contextual bucket; halt/event evidence required |
| news_near_short_flow_only | 20 | 15 | 6.2 | short-flow context only; not price authority |

## IPO context

| ipo_link_bucket | events | tickers | institutional_reading |
| --- | --- | --- | --- |
| ipo_near_market_anomaly | 676 | 668 | candidate early-life event context |
| ipo_market_clean | 449 | 443 | sparse valid IPO context without nearby anomaly |
| ipo_near_halt_market_event | 156 | 156 | strong IPO/halt context; requires event-aware handling |

## Core restrictions

- `reference` remains the primary authority for identity and corporate actions.
- `daily`, `quotes`, `trades` and `ohlcv_1m` remain the primary raw market-data authorities.
- Additional financials require point-in-time filing logic before feature use.
- News requires ticker-attribution and timestamp guardrails.
- Macro/economic series can populate calendar context, not ticker-level causal proof.

## Evidence assets

- `evidence_assets/quality_tables/additional_subfamily_quality_table_v0_2.csv`
- `evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv`
- `evidence_assets/reference_reconciliation/additional_corporate_actions_reference_reconciliation_v0_1.csv`
- `evidence_assets/news_attribution/additional_news_attribution_quality_v0_1.csv`
- `evidence_assets/ipo_context/additional_ipo_context_quality_v0_1.csv`
- `evidence_assets/visual_overview/additional_coverage_by_dataset_v0_2.png`
- `evidence_assets/visual_overview/additional_quality_role_by_family_v0_2.png`
- `visual_inspector_pack/additional_visual_inspector_pack_v0_1.md`
- `visual_inspector_pack/additional_visual_case_manifest_v0_1.csv`
- `visual_inspector_pack/additional_visual_asset_audit_v0_1.csv`

## Human casepacks

- `good_justification/additional_financials_core_good_cases_v0_1.md`
- `flagged_case_evidence_packs/additional_news_attribution_review_cases_v0_1.md`
- `flagged_case_evidence_packs/additional_corporate_actions_reference_review_v0_1.md`
- `coverage_case_evidence_packs/additional_sparse_valid_context_cases_v0_1.md`

## Open limits

The package raises Additional above the old auxiliary-only state, but does not close every subfamily at 100%. Remaining limits are intentional:

- ratios remain sparse and vendor-derived;
- news remains attribution-sensitive;
- corporate actions remain secondary to reference;
- macro/economic data remains calendar context, not ticker causality;
- no downstream feature promotion is granted by this readout alone.
