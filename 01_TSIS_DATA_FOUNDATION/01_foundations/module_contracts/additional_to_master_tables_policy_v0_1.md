# Additional To Master Tables Policy v0.1

## Purpose

This policy defines how `additional_v0_1` may contribute to CAPA 1 outputs.

The goal is to support:

- `data_quality_report`
- `master_daily_table`
- `master_intraday_table`
- `symbol_master`
- `corporate_actions_table`
- `calendar_table`

without confusing RAW vendor context with core market-data authority or
reference authority.

## Principle

Additional can enrich audited data tables.

Additional cannot certify the market data that it enriches.

```text
RAW market data and reference authority come first.
Additional context comes after them.
```

## Approved Destinations

| Target table | Additional contribution | Status |
| --- | --- | --- |
| `data_quality_report` | subfamily quality flags, coverage, attribution risk, reference overlap | ready_for_contextual_quality_columns |
| `master_daily_table` | `news_flag`, IPO age/listing context, filing-aware fundamentals context, macro date overlays | partial_context_ready |
| `master_intraday_table` | event-time context from news/IPO/macro calendar | indirect_context_only |
| `symbol_master` | issuer/listing/fundamental identity context | partial_context_ready |
| `corporate_actions_table` | secondary reconciliation for splits, dividends and ticker events | secondary_reconciliation_only |
| `calendar_table` | macro date series | macro_context_ready |

The current readiness table lives at:

```text
inspection_dossiers/additional/evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv
```

## Subfamily Rules

### Financial Statements

May support:

- contextual fundamentals fields;
- filing coverage diagnostics;
- data-quality completeness;
- symbol or issuer context.

Must preserve:

- `filing_date`;
- `period_end`;
- `fiscal_year`;
- `fiscal_quarter`;
- `timeframe`.

Forbidden:

- treating period-end data as known at period end;
- using financial fields as direct features without point-in-time filing logic.

### Ratios

May support:

- sparse context;
- data-quality diagnostics;
- exploratory research flags.

Forbidden:

- universal coverage assumption;
- primary ML feature promotion from coverage alone.

### News

May support:

- daily `news_flag`;
- event context;
- forensic explanation;
- candidate causal overlays.

Must preserve:

- `published_utc`;
- article id;
- requested ticker;
- article ticker list or ticker-count ambiguity;
- attribution bucket.

Forbidden:

- reading requested ticker as sole causal subject in multi-ticker articles;
- treating nearby market anomaly as causal proof.

### IPOs

May support:

- `ipo_flag`;
- `ipo_age`;
- listing context in `symbol_master`;
- early-life risk context.

Forbidden:

- treating sparse IPO coverage as missing-data failure for mature tickers.

### Corporate Actions Additional

May support:

- reconciliation queue;
- secondary confirmation;
- data-quality diagnostics.

Forbidden:

- overriding `reference`;
- adjusting price views from Additional when reference disagrees.

### Economic

May support:

- macro calendar context;
- regime-level date overlays;
- data-quality diagnostics for macro series.

Forbidden:

- direct ticker-level causal claims without a separate model and contract.

## Promotion Barrier

No field sourced from Additional may become a primary downstream feature,
label, trading signal, execution input or RL state unless a later promotion
document proves:

- point-in-time availability;
- source lineage;
- coverage state;
- leakage control;
- consumer class;
- schema and validator;
- evidence dossier;
- changelog entry.

## Interaction With Core Authorities

Additional never outranks:

- `daily` for daily price/volume bars;
- `quotes` for visible book state;
- `trades` for tape/prints;
- `ohlcv_1m` for intraday bars;
- `reference` for identity and corporate actions;
- `halts` for regulatory/event halt authority.

## Current Status

This policy enables CAPA 1 planning and quality-table design.

It does not authorize a materialized `master_daily_table` or
`master_intraday_table` release by itself.
