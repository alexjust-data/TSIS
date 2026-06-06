# Additional IPOs Schema Contract

Status: canonical schema contract for `E:\TSIS\data\additional\ipos`.

## Purpose

`additional\ipos` stores IPO event data for the `<1B>` operating universe. It exists to explain early-life behavior, listing fragility and halt/anomaly contexts around newly listed securities.

## Physical Layout

Observed root:

`E:\TSIS\data\additional\ipos\ipos`

Observed pattern:

`ticker=<TICKER>\ipos_<TICKER>.parquet`

Observed representative payload:

`E:\TSIS\data\additional\ipos\ipos\ticker=AARD\ipos_AARD.parquet`

## Valid Physical Forms

Ticker files may contain either:

- IPO payload rows
- empty sentinel rows with `ticker`, `_empty`, `_dataset`, `_ingested_utc`

## Observed Payload Columns

`ticker`, `last_updated`, `announced_date`, `listing_date`, `issuer_name`, `currency_code`, `us_code`, `isin`, `final_issue_price`, `max_shares_offered`, `lowest_offer_price`, `highest_offer_price`, `total_offer_size`, `primary_exchange`, `shares_outstanding`, `security_type`, `lot_size`, `security_description`, `ipo_status`, `_dataset`, `_ingested_utc`.

## Canonical Event Key

`ticker + listing_date + issuer_name`

If `listing_date` is missing, consumers may use `announced_date` only under an explicit review flag.

## Coverage Evidence

Audited against 4824 `<1B>` tickers:

- `files_present = 4824`
- `files_non_empty = 1255`
- `coverage_non_empty_pct = 26.016`
- `rows_total = 4850`

## Causal Buckets

Observed causal overlay buckets:

- `ipo_near_halt_market_event = 156`
- `ipo_near_market_anomaly = 676`
- `ipo_market_clean = 449`

## Required Consumer Rules

- Use IPOs as early-life context, not as universal ticker metadata.
- Strongest use is near halts or early market anomalies.
- Keep `ipo_market_clean` as contextual/review, not causal proof.
- Preserve empty sentinels as valid no-data outputs.

## Verdict

`additional\ipos` is sparse but valid. It is useful for early-life and halt/anomaly context, with strongest institutional confidence in `ipo_near_halt_market_event`.
