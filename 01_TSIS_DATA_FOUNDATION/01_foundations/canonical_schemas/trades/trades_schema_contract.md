# `trades` Schema Contract

## Purpose

This schema contract defines the canonical structural expectations for raw `trades` files and for file-level audit rows derived from them.

`trades` has two distinct schema layers:

1. raw trade-row schema
2. file-level audit / acceptance schema

They must not be conflated.

## Layer 1: Raw Trade-Row Schema

A canonical raw `trades` file is expected to expose, at minimum, the following columns:

- `ticker`
- `date`
- `timestamp`
- `price`
- `size`
- `exchange`
- `conditions`
- `year`
- `month`
- `day`

Observed example from active local data:

- `C:\TSIS_Data\data\trades_ticks_prod_2005_2026\SELF\year=2016\month=01\day=2016-01-19\market.parquet`

### Field semantics

#### `ticker`

- upper-case trading symbol at file extraction time
- not a stable corporate identity key by itself
- must be interpreted alongside `ticker_events` / identity layers when continuity matters

#### `date`

- session day at file granularity
- must agree with folder partition and with timestamp normalization after timezone conversion

#### `timestamp`

- raw event timestamp for the print
- the canonical intraday ordering field
- must remain raw at schema level; no economic adjustment is applied to timestamps

#### `price`

- executed print price
- this is `trades_raw` semantics, not `daily_adjusted`
- valid comparison against other price layers requires explicit view declaration

#### `size`

- executed print size
- central to odd-lot vs round-lot analysis
- a file with valid prices but pathological size structure may still fall into review buckets

#### `exchange`

- venue identifier at print level
- useful for fragmentation and quality analysis
- not optional when venue-sensitive diagnostics are needed

#### `conditions`

- sale-condition payload for the print
- not all conditions are semantically equivalent
- canonical downstream logic must preserve the raw list or list-like representation before any reduction

### Structural rules

A canonical raw file should satisfy:

- row-level `timestamp` parseability
- non-negative `price`
- non-negative `size`
- stable `ticker` within file
- stable `date` within file

Important methodological note:

- `price = 0` and `size = 0` are not automatically treated as physical corruption by schema alone
- those cases may still matter to validators, but the schema contract does not collapse them into failure by definition

This follows the historical `05` refactor, which explicitly separated hard physical invalidity from later interpretive acceptance policy.

## Layer 2: File-Level Audit / Acceptance Schema

The file-level acceptance layer is not a raw tape schema. It is a derived audit representation built by the historical builders and full-closeout runners.

A canonical file-level audit row should include, conceptually, fields covering:

- file identity
- severity snapshot
- issue / warning aggregates
- reference-comparison metrics
- session diagnostics
- odd-lot / round-lot diagnostics
- scale / comparability diagnostics
- final acceptance label

### Required semantic groups

#### Identity

- `ticker`
- `date`
- `file`
- partition metadata if present

#### Snapshot severity

- `severity`
- hard issue counts
- warning counts

#### Reference comparison

- trade price conflict against `daily`
- trade price conflict against `1m`
- break side and magnitude metrics

#### Microstructure diagnostics

- duplicate burden
- odd-lot / round-lot mix
- session profile
- condition-code structure

#### Final policy

- `acceptance_label`
- supporting taxonomy / rationale fields when available

## Canonical Use Rule

The raw trade-row schema feeds:

- execution research
- microstructure analysis
- file-level recompute

The file-level audit schema feeds:

- acceptance policy
- population readouts
- case selection
- institutional inspection dossiers

No consumer should infer file-level acceptance directly from raw columns without passing through the relevant validators and policy logic.

## Relation To Price Views

`trades` raw schema always maps first to:

- `trades_raw`

Derived comparisons may later project into:

- `split_normalized`
- `adjusted_proxy`
- eventually `adjusted`

But those are views over raw values, not replacements for the schema itself.

## Why this split matters

The historical audit showed that a file can:

- look severe in snapshot metrics
- disagree strongly with `daily` or `1m`
- yet still be better explained by scale mismatch or microstructure context than by intrinsic tape corruption

Therefore the schema must keep raw observation separate from acceptance semantics.
