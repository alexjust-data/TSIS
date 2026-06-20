# Additional Visual Overview v0.2

Generated visual assets:

- `additional_coverage_by_dataset_v0_2.png`
- `additional_quality_role_by_family_v0_2.png`

These images summarize coverage and quality roles. They are not a substitute for the subfamily contracts or validators.

## Master table readiness

| target_table | additional_role | readiness | blocking_limit |
| --- | --- | --- | --- |
| data_quality_report | subfamily quality flags, coverage state, attribution risk, reference overlap | ready_for_contextual_quality_columns | Not a single uniform dataset; each subfamily must keep its state. |
| master_daily_table | news_flag, IPO age/listing context, financial context with filing-date guardrails, macro day overlays | partial_context_ready | No direct alpha/feature promotion without point-in-time and attribution controls. |
| master_intraday_table | event-time context for news/IPO/macro calendar only | indirect_context_only | Does not replace quotes, trades or 1m intraday market evidence. |
| symbol_master | issuer/listing/fundamental identity context | partial_context_ready | Reference identity remains primary authority. |
| corporate_actions_table | secondary reconciliation for dividends, splits and ticker_events | secondary_reconciliation_only | Reference corporate actions remain primary authority. |
| calendar_table | macro date series for inflation, expectations and treasury yields | macro_context_ready | Macro presence is not ticker-level causality. |
