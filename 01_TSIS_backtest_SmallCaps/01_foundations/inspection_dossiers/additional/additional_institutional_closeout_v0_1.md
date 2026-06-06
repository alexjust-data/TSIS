# Additional Institutional Closeout v0.1

## Scope

This dossier institutionalizes the `additional` block inside `01_foundations`.

Source evidence was migrated from the historical audit work under:

`01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/`

The active data root reviewed here is:

`E:\TSIS\data\additional`

## Historical Evidence Links

The institutional readout in this dossier is grounded in these preserved historical documents:

- [01_contrato_additional.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/01_contrato_additional.md)
- [02_diseno_implementacion_additional_v2.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/02_diseno_implementacion_additional_v2.md)
- [descarga_additional.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/descarga_additional.md)
- [03_additional_root_cause_audit_phase1_closeout.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/03_additional_root_cause_audit_phase1_closeout.md)
- [04_additional_causal_overlay_closeout.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md)
- [04_additional_closeout.md](../../../01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_closeout.md)

## Why This Block Exists

`additional` was created to add auxiliary Polygon context for the `<1B>` operating universe:

- fundamentals
- news
- IPOs
- corporate actions
- macro/economic context

It was not created as a replacement for the core raw roots (`daily`, `1m`, `quotes`, `trades`) or for the primary `reference` layer.

## Materialization Evidence

Ticker-based download:

- date: `2026-04-05`
- universe: 4824 `<1B>` tickers
- datasets: 9
- submitted tasks: 43416
- ok tasks: 43416
- error tasks: 0

Macro download:

- datasets: `inflation`, `inflation_expectations`, `treasury_yields`
- submitted tasks: 3
- ok tasks: 3
- error tasks: 0

Manifests:

- `runs/backtest/additional_downloads/20260405_full_refresh_ticker_based/download_summary.json`
- `runs/backtest/additional_downloads/20260405_full_refresh_macro/download_summary.json`

## Effective Coverage

Ticker-based audit against 4824 `<1B>` tickers:

| Dataset | files_present | files_non_empty | coverage_non_empty_pct | interpretation |
|---|---:|---:|---:|---|
| `income_statements` | 4824 | 4813 | 99.772 | good |
| `balance_sheets` | 4824 | 4813 | 99.772 | good |
| `cash_flow_statements` | 4824 | 4810 | 99.710 | good |
| `news` | 4824 | 3869 | 80.203 | good/review |
| `ticker_events` | 4824 | 2703 | 56.032 | review |
| `ratios` | 4824 | 2232 | 46.269 | review |
| `splits` | 4824 | 1876 | 38.889 | review/secondary |
| `dividends` | 4824 | 1258 | 26.078 | review/secondary |
| `ipos` | 4824 | 1255 | 26.016 | good/review |

Macro audit:

| Dataset | rows | date_min | date_max | interpretation |
|---|---:|---|---|---|
| `inflation` | 950 | 1947-01-01 | 2026-02-01 | good macro |
| `inflation_expectations` | 531 | 1982-01-01 | 2026-03-01 | good macro |
| `treasury_yields` | 16047 | 1962-01-02 | 2026-04-02 | good macro |

Coverage artifacts:

- `runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_lt1b_coverage_audit_summary.json`
- `runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_ticker_datasets_summary.parquet`
- `runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_macro_datasets_summary.parquet`

## Structural Findings

`additional` is not a homogeneous dataset. It contains:

- `ticker-filing` data: financial statements
- `ticker-snapshot` data: ratios
- `ticker-event` data: corporate actions and IPOs
- `news-event` data: news
- `macro-date` data: economic series

Placeholders with `ticker`, `_empty`, `_dataset`, `_ingested_utc` are valid no-data outputs.

The audit explicitly avoided blind dataset-merge reads because partition/schema conflicts were observed around `ticker` encoding.

## Relationship To Existing Layers

`additional\financials`:

- overlaps in concept with `financial`
- is scoped to the `<1B>` additional refresh
- is not byte-identical to `financial`
- should not replace `financial` without reconciliation

`additional\corporate_actions`:

- overlaps with `reference`
- `splits` and `dividends` are mostly secondary confirmation
- `ticker_events` remains review due taxonomy/normalization instability

`additional\news`:

- strongest causal/contextual value
- strongest class is `news_near_halt_market_event`
- multi-ticker attribution ambiguity is material

`additional\ipos`:

- sparse but useful for early-life and halt/anomaly context

`additional\economic`:

- good macro overlay
- not direct ticker-level causal proof

## Final Institutional Status

| Subblock | Status |
|---|---|
| `financials_core` | good |
| `financials_ratios` | review |
| `news` | good/review |
| `ipos` | good/review |
| `corporate_actions_additional` | review, secondary to reference |
| `economic` | good as macro dataset, review for ticker causality |

No aggregate `bad` family emerged. The limits are sparsity, multi-ticker ambiguity and redundancy versus `reference`, not mass corruption.

## Verdict

`additional` is an institutional auxiliary block and should be preserved. It is not obsolete, but it must be consumed by subblock-specific rules rather than as one uniform dataset.
