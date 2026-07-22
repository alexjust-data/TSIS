# Regime Indicators Dataset Contract v0.1 - Modulo 01

## 1. Role

This contract defines `regime_indicators_v0_1` as a raw/context regime-proxy data family under:

```text
E:/TSIS/data/regime_indicators
```

It covers:

- ETF regime bars under `etfs/`;
- index regime bars under `indices/`;
- root metadata files.

This family is market/regime context. It is not small-cap tradable universe data, not alpha by itself, and not a replacement for `daily`, `quotes`, `trades` or `ohlcv_1m`.

## 2. Current Institutional Status

Status:

```text
blocked_daily_scoped_minute_review_v0_1
```

Reason:

- minute files have coherent physical schemas;
- root metadata is coherent as coverage evidence;
- daily ETF and index files have invalid date semantics;
- no daily regime consumer may use the current `date` or `datetime` fields.

## 3. Physical Scope

Observed root:

```text
E:/TSIS/data/regime_indicators
```

Observed layout:

| Subroot/file | Role |
| --- | --- |
| `etfs/<ETF_SYMBOL>/minute.parquet` | ETF minute regime proxy bars |
| `etfs/<ETF_SYMBOL>/day.parquet` | ETF daily bars, currently blocked |
| `indices/<INDEX_SYMBOL_DIRECTORY>/minute.parquet` | available index minute bars |
| `indices/<INDEX_SYMBOL_DIRECTORY>/day.parquet` | index daily bars, currently blocked |
| `download_metadata.json` | operational metadata |
| `ticker_ranges.json` | detected range metadata |

Observed physical footprint:

- 67 parquet files;
- 2 JSON files;
- 34 observed daily parquet files;
- 34 symbols in `ticker_ranges.json`.

## 4. Canonical Schema Contracts

Schemas live in:

- `01_foundations/canonical_schemas/regime_indicators/regime_etf_bars_schema_contract.md`
- `01_foundations/canonical_schemas/regime_indicators/regime_index_bars_schema_contract.md`
- `01_foundations/canonical_schemas/regime_indicators/regime_metadata_schema_contract.md`
- `01_foundations/canonical_schemas/regime_indicators/regime_indicators_quality_notes.md`

Known schema-location debt:

- existing schema docs mention `D:/regime_indicators`;
- the active physical root in this report is `E:/TSIS/data/regime_indicators`;
- root equivalence must not be assumed without a migration/root audit.

## 5. Primary Semantics

Minute ETF bars:

```text
symbol + timestamp
```

Minute index bars:

```text
logical_symbol + timestamp
```

Daily bars:

```text
blocked until valid symbol + date semantics are repaired
```

Metadata:

```text
coverage/range evidence only
```

## 6. Known Blocking Issue

All observed daily ETF/index files have invalid daily date semantics:

- `date` minimum: `1970-01-01`;
- `date` maximum: `1970-01-01`;
- `date` unique values: 1;
- `datetime` values are clustered in 1970.

This blocks daily regime use.

## 7. Evidence Dossier

Modern foundation readout:

- `01_foundations/inspection_dossiers/regime_indicators/regime_indicators_inspection_readout_v0_1.md`

Data-quality report:

- `01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md`

Validator:

- `01_foundations/validators/regime_indicators/regime_indicators_validators.md`

## 8. Required Consumer Rules

Consumers must:

- treat daily bars as blocked;
- not use daily `date` or `datetime` columns as calendar keys;
- not silently repair daily files from metadata;
- use minute files only with timestamp coverage and price sanity validation;
- map index directory names to logical symbols explicitly;
- preserve ETF/index symbol scope;
- not treat regime proxies as small-cap tradable securities.

## 9. Allowed Consumers

Allowed now:

- `data_quality_report`;
- `source_validation`;
- `repair_planning`;
- `forensic_review`;
- minute-level research inspection with explicit scope.

Blocked until repair:

- daily regime features;
- calendar-level joins from current daily files;
- master daily regime columns;
- ML/RL/live consumers.

## 10. Non-Goals

This contract does not:

- repair daily dates;
- promote minute bars as full production regime features;
- certify all timestamp coverage;
- certify ETF/index price sanity;
- enable small-cap universe membership decisions.

## 11. Verdict

`regime_indicators_v0_1` is governed but not promoted.

The correct state is:

```text
daily_bars_blocked_minute_bars_schema_readable_pending_full_audit
```
