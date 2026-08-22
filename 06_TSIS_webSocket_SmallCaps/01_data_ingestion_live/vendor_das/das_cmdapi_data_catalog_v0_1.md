# DAS CMD API Data Catalog v0_1

Status: draft source inventory  
Owner module: `04_TSIS_webSocket_SmallCaps`  
Physical live data root: default `E:/TSIS/data_DAS_live`; current operator override `C:/TSIS_Data/data` when supplied through `--data-root`  
Contract reference:

- `C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md`

Reference evidence:

- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/CMD API Manual.pdf`
- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/DAS_CMD_API_First_Connection.ipynb`
- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/das_cmdapi_full_readonly_dump_SOXS_20260703_105830.json`
- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/das_cmdapi_transcript_SOXS_*.json`

## Menu

- [Purpose](#purpose)
- [Core Rule](#core-rule)
- [Physical Data Layout](#physical-data-layout)
- [Data Storage Architecture](#data-storage-architecture)
- [Long-running Capture Requirements](#long-running-capture-requirements)
- [Authentication And Session Data](#authentication-and-session-data)
- [Market Data Streams](#market-data-streams)
  - [Level 1 Quotes](#level-1-quotes)
  - [Time And Sales](#time-and-sales)
  - [Level 2 Book](#level-2-book)
  - [Level 3 / Market-By-Order Depth](#level-3--market-by-order-depth)
  - [Top Lists / Scanner-like Lists](#top-lists--scanner-like-lists)
  - [Daily Chart Bars](#daily-chart-bars)
  - [Minute Chart Bars](#minute-chart-bars)
- [Symbol Status And Short-side Data](#symbol-status-and-short-side-data)
  - [Short Info](#short-info)
  - [Limit Up / Limit Down](#limit-up--limit-down)
  - [Symbol Status / SSR](#symbol-status--ssr)
- [Account And Broker State Data](#account-and-broker-state-data)
  - [Buying Power](#buying-power)
  - [Account Info](#account-info)
  - [Positions](#positions)
  - [Orders](#orders)
  - [Trades](#trades)
  - [Route Status](#route-status)
  - [Locates](#locates)
  - [Internal Messages](#internal-messages)
- [Short Locate Queries](#short-locate-queries)
- [Blocked Execution Commands](#blocked-execution-commands)
- [Known DAS Capacity Limits](#known-das-capacity-limits)
- [Screener v0 Data Plan](#screener-v0-data-plan)
- [Source Parity Notes](#source-parity-notes)
- [Current Evidence Gaps](#current-evidence-gaps)
- [v0 Implementation Boundary](#v0-implementation-boundary)

## Purpose

This document records the DAS CMD API data families that TSIS can capture for live operation research.

It is an inventory of available source data, not a production feature contract.

DAS live captures must be stored under the configured DAS data root. Default contract root:

```text
E:/TSIS/data_DAS_live
```

Current operator-directed DAS CMDAPI read-only root:

```text
C:/TSIS_Data/data
```

Code, documentation, source parity notes and service wrappers belong under:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps
```

Do not store DAS live payloads under `data/raw_ws`; that path is preserved for the existing Polygon/Massive WebSocket prototype.

## Core Rule

Default DAS work in TSIS is read-only and data-only.

The first application must capture live market, account-state and broker-state evidence. It must not send orders, cancels, replaces, locate orders, route actions or execution commands.

Secrets, usernames, passwords, account ids and broker credentials must not be written to markdown, JSONL, parquet metadata, logs, screenshots or manifests.

## Physical Data Layout

Recommended root uses raw-by-run plus normalized-by-family/date/symbol. The raw JSONL files should preserve the original DAS text lines and add TSIS wrapper metadata such as receive timestamp, command context, socket session id, subscription id, symbol, parser version and raw line hash.

## Data Storage Architecture

La arquitectura fisica de DAS live tiene dos capas obligatorias:

```text
1. raw evidence layer
   -> particion primaria por run_id
   -> verdad de auditoria append-only

2. normalized query layer
   -> particion por data_family / market_date / symbol
   -> forma comoda para analisis, replay, inspeccion y futuros builders
```

Regla central:

```text
raw_cmdapi/runs/<run_id> is the audit truth
normalized/<data_family>/market_date=<YYYY-MM-DD>/symbol=<SYMBOL>/ is the query surface
```

No se debe usar `date/symbol` como particion primaria del raw porque DAS CMD API
es un stream operacional: comandos, respuestas, no-response, errores,
subscriptions, heartbeats y cortes de luz se entienden por run. La particion
por fecha/ticker se construye despues como capa normalizada derivada.

### Required Physical Layout

Use the configured DAS data root. In the default contract examples below that root is `E:/TSIS/data_DAS_live`; in the current operator-directed run replace it with `C:/TSIS_Data/data`.

```text
E:/TSIS/data_DAS_live/
  README.md

  raw_cmdapi/
    runs/
      <run_id>/
        pre_manifest.json
        pid_manifest.json
        heartbeat.json
        command_transcript.jsonl
        events.jsonl
        candidate_registry.jsonl
        subscription_state.json
        capture.log
        final_summary.json

  screener/
    runs/
      <run_id>/
        screener_manifest.json
        candidates.jsonl
        candidates.csv

  normalized/
    lv1/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    tms/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    lv2/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    toplist/
      market_date=<YYYY-MM-DD>/
        data.parquet
    shortinfo/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    symstatus/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    ldlu/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    daychart/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    minchart_1m/
      market_date=<YYYY-MM-DD>/
        symbol=<SYMBOL>/
          data.parquet
    account_state/
      market_date=<YYYY-MM-DD>/
        run_id=<run_id>/
          data.parquet

  indexes/
    candidate_daily_index/
      market_date=<YYYY-MM-DD>/
        candidates.parquet
    run_index.parquet

  catalog/
    das_cmdapi_command_catalog_v0_1.json
    das_cmdapi_field_inventory_v0_1.md
```

`normalized/account_state` is separated from symbol-market data because account
and broker telemetry can be sensitive and is not automatically model-facing.

### Date And Timestamp Semantics

- Every raw event must preserve `observed_at_utc`.
- Any source timestamp returned by DAS must be preserved as a source field.
- Normalized partitions use `market_date=<YYYY-MM-DD>` for the US equity market
  session date, not the local machine date in Europe.
- If market_date cannot be inferred safely, the event remains in raw and the
  normalized writer must record an explicit `market_date_unavailable` reason.

### Candidate Registry Contract

Every ticker that passes or is evaluated by the screener must produce an entry
in:

```text
raw_cmdapi/runs/<run_id>/candidate_registry.jsonl
```

Minimum fields:

| Field | Meaning |
| --- | --- |
| `run_id` | Capture run id. |
| `detected_at_utc` | Time TSIS detected/evaluated the candidate. |
| `market_date` | US equity market date if known. |
| `session` | `premarket`, `regular_market` or `afterhours` if known. |
| `symbol` | Candidate ticker. |
| `price_usd` | Price used for the denominator if available. |
| `volume_shares` | Volume used for the denominator if available. |
| `market_cap_usd` | Market cap from governed TSIS reference unless DAS is later certified. |
| `filter_status` | `pass`, `fail` or `unavailable`. |
| `failure_reasons` | Explicit reasons; missing fields are not invented. |
| `capture_plan` | Data families planned for full capture. |
| `capture_status` | `pending`, `active`, `complete`, `partial`, `failed` or `interrupted`. |
| `raw_event_refs` | References to raw run/event offsets or command transcript ids when available. |
| `normalized_paths` | Paths written under `normalized/` when available. |

### Full Candidate Capture Bundle

For every candidate that passes the initial screener, the app should attempt the
full read-only symbol bundle allowed by config:

- Lv1;
- Time and Sales;
- Lv2 if enabled;
- TOPLIST context if available;
- SHORTINFO;
- LDLU;
- SymStatus;
- DAYCHART;
- MINCHART 1m;
- no-response / permission / login-required observations.

`all data` means all read-only data families available to the app and permitted
by config/contract. It does not mean orders, cancels, replaces, locate orders,
credential capture or unredacted account secrets.

### Write Order

During live capture:

1. Write raw JSONL first.
2. Flush raw JSONL continuously.
3. Update heartbeat.
4. Append/update candidate registry.
5. Write normalized outputs only after raw evidence exists.
6. Link normalized outputs back to raw run ids and event ids.

A normalized writer failure must not invalidate raw evidence.

## Long-running Capture Requirements

DAS capture is a long-running operation. The app must write progress continuously.

Required files per run:

| File | Role |
| --- | --- |
| `pre_manifest.json` | Intended run config before opening the socket. |
| `pid_manifest.json` | Process id, host, port, start time and active command set. |
| `heartbeat.json` | Atomic progress heartbeat, refreshed while running. |
| `command_transcript.jsonl` | Every command sent and response block received. |
| `events.jsonl` | Parsed/source-preserved event stream, one event per line. |
| `candidate_registry.jsonl` | Candidate decisions, capture plan/status and links to raw/normalized evidence. |
| `subscription_state.json` | Current subscribed symbols and channels. |
| `capture.log` | Human-readable run log. |
| `final_summary.json` | Final counts and status if the app exits cleanly. |

If power is lost, `final_summary.json` may be missing, but all flushed JSONL lines already written remain valid evidence.

## Authentication And Session Data

Terminal-prompt socket login is the default operating mode for TSIS DAS v0. The human launches the app, the app asks for DAS username, password and account in the terminal, then sends socket `LOGIN` and stores only the redacted command in `command_transcript.jsonl`.

Observed flow:

```text
LOGIN <user> <password> <account> 0  # terminal prompt only; transcript redacted
ECHO OFF
CLIENT
ReturnFullLv1 YES
```

Important behavior:

- DAS frontend login/passport can affect CMD API availability, but TSIS does not rely on frontend login alone.
- Each live capture session should explicitly login through the socket after prompting the operator.
- Quote-only commands may work without API logon if DAS is configured with disabled logon check, but TSIS should not rely on that.
- Credentials must not come from committed config files and must not be logged; in v0 they are entered interactively in the terminal and kept in memory only.
## Market Data Streams

### Level 1 Quotes

Command:

```text
SB <symbol> Lv1
UNSB <symbol> Lv1
ReturnFullLv1 YES
```

Observed response prefix:

```text
$Quote
```

Observed fields include:

| Field family | Examples |
| --- | --- |
| symbol | ticker/symbol |
| ask | `A`, `Asz` |
| bid | `B`, `Bsz` |
| last/volume | `L`, `V` |
| session extrema | `Hi`, `Lo`, `op`, `ycl`, `tcl` |
| derived live metrics | `VWAP`, `RVOL`, `tradesAllDay` |
| time | `T` |

Notes:

- This is the primary live market feed for a small symbol universe.
- `ReturnFullLv1 YES` should be enabled for fuller quote payloads.
- Empty responses are valid evidence and should be logged.

### Time And Sales

Command:

```text
SB <symbol> tms
UNSB <symbol> tms
```

Observed response prefix:

```text
$T&S
```

Observed fields include:

| Field family | Examples |
| --- | --- |
| symbol | ticker/symbol |
| price | execution/print price |
| size | print volume |
| flag/condition | trade flag |
| time | print time |
| venue | exchange/market center |
| side/indicator | observed flags in DAS payload |

Notes:

- This is the closest DAS stream to live tape/trades.
- It should be stored raw and parsed into a separate event type.

### Level 2 Book

Command:

```text
SB <symbol> Lv2
UNSB <symbol> Lv2
```

Manual response prefix:

```text
$Lv2
```

Expected fields include:

| Field family | Examples |
| --- | --- |
| symbol | ticker/symbol |
| condition/side | bid/ask or condition |
| MMID/venue | market maker or venue id |
| price | level price |
| size | level size |
| time/order metadata | source-dependent DAS fields |

Notes:

- Local SOXS evidence returned no Lv2 lines in one test. That can mean no data, permission limits, symbol/session issue or timing.
- The app must record no-response outcomes as valid command observations.
- Lv2 is capacity-limited and should be enabled only for selected symbols.

### Level 3 / Market-By-Order Depth

Status v0:

```text
not certified / not in current DAS CMD API contract
```

TSIS currently treats `Lv2` as the depth feed. Do not label DAS data as `L3`
until a DAS CMD API command and response payload are found in the manual or live
evidence, added to the allowlist, captured in raw JSONL, parsed conservatively
and smoke-tested. Until then, L3 must be recorded as unavailable/not certified,
not inferred from Lv2.
### Top Lists / Scanner-like Lists

Command:

```text
SB TOPLIST
UNSB TOPLIST
```

Observed response prefix:

```text
$TopLst
```

Observed list families:

| Top list | Meaning |
| --- | --- |
| `NASActive` | Nasdaq active list. |
| `NASGain` | Nasdaq gainers list. |
| `NASLost` | Nasdaq losers list. |
| `LSTActive` | Listed active list. |

Notes:

- This is the best DAS-native seed for a live screener.
- The full payload should be tested during market hours to confirm symbol list detail and refresh behavior.

### Daily Chart Bars

Command:

```text
SB <symbol> DAYCHART <start_date> <end_date>
UNSB <symbol> DAYCHART
```

Observed response prefix:

```text
$Bar
```

Observed fields:

```text
$Bar symbol date high low open close volume status/count
```

Notes:

- This is source data from DAS, not a replacement for the governed historical daily foundation.
- It can be useful for live session context, quick validation and source parity checks.

### Minute Chart Bars

Command:

```text
SB <symbol> MINCHART <start_datetime> <end_datetime> 1
UNSB <symbol> MINCHART
```

Observed/manual response prefix:

```text
$Bar
```

Observed fields:

```text
$Bar symbol date-time high low open close volume status/count
```

Notes:

- This is DAS minute/chart source data.
- It must not be confused with canonical TSIS 1m history under `E:/TSIS/data/ohlcv_1m`.
- Any comparison to quote-guarded 1m must go through source parity/audit docs.

## Symbol Status And Short-side Data

### Short Info

Command:

```text
GET SHORTINFO <symbol>
```

Observed response prefixes:

```text
$SHORTINFO
$STINFOEX
```

Data families:

| Field family | Role |
| --- | --- |
| shortable flag | Whether DAS reports the symbol as shortable. |
| available shares | Source-dependent availability/count. |
| easy/hard/borrow flags | DAS-specific short metadata. |
| extended short info | Additional text fields when returned as `$STINFOEX`. |

Notes:

- Some unauthenticated tests returned no response.
- The capture app should run this after login for each screener candidate.

### Limit Up / Limit Down

Commands:

```text
GET LDLU <symbol>
```

Also returned after some Lv1 subscriptions.

Observed response prefix:

```text
$LDLU
```

Fields:

| Field family | Role |
| --- | --- |
| symbol | ticker/symbol |
| limit down | DAS reported lower band |
| limit up | DAS reported upper band |

### Symbol Status / SSR

Command:

```text
GET SymStatus <symbol>
```

Observed response prefixes:

```text
$SymStatus
$IssueStatus
```

Fields:

| Field family | Role |
| --- | --- |
| symbol | ticker/symbol |
| SSR | short-sale restriction yes/no |
| issue status | source-dependent trading/status flags |

Notes:

- Local evidence showed `GET SymStatus` can fail with a message saying Lv1 must be subscribed first.
- The app should subscribe Lv1 briefly before symbol status if needed.

## Account And Broker State Data

These are read-only state snapshots. They are useful for operations and risk monitoring, but they are broker/account telemetry, not model-training features by default.

### Buying Power

Command:

```text
GET BP
```

Observed response prefix:

```text
BP
```

Fields:

| Field family | Role |
| --- | --- |
| buying power | DAS account buying power |
| net buying power | DAS account net buying power |

### Account Info

Command:

```text
GET AccountInfo
```

Observed response prefix:

```text
$AccountInfo
```

Observed fields include:

| Field family | Examples |
| --- | --- |
| equity | `OpenEQ`, `CurrEQ` |
| PnL | `RealizedPL`, `UnrealizedPL`, `NetPL` |
| fees/costs | `HTBCost`, `SecFee`, `FINRAFee`, `ECNFee`, `Commission` |

Notes:

- This data is sensitive account telemetry.
- It must be redacted or excluded from shared evidence unless explicitly needed.

### Positions

Command:

```text
GET POSITIONS
```

Observed response block:

```text
#POS
%POS
#POSEND
```

Fields include symbol, type, quantity, average cost, initial quantity/price, realized/unrealized values and creation time.

### Orders

Command:

```text
GET ORDERS
```

Observed response block:

```text
#Order
%ORDER
#OrderEnd
```

Fields include order id, token, symbol, side, order type, quantity, leaves/cancelled quantity, price, route, status, time, account/trader/source, TIF and preferences.

### Trades

Command:

```text
GET TRADES
```

Observed response block:

```text
#Trade
%TRADE
#TradeEnd
```

Fields include trade id, symbol, side, quantity, price, route, time, order id, liquidity flag, ECN fee and PnL.

### Route Status

Command:

```text
GET ROUTESTATUS
```

Observed response prefix:

```text
$RouteStatus
```

Fields:

| Field family | Role |
| --- | --- |
| route | broker/DAS route name |
| status | enabled/disabled/other route status |

### Locates

Command:

```text
GET LOCATES
```

Observed response block:

```text
#SLOrder
%SLOrder
#SLOrderEnd
```

Fields include locate order id, symbol, shares, open shares, executed shares, price, status, route, time, limit price, token and notes.

### Internal Messages

Command:

```text
GET INTMSGS
```

Manual response prefix:

```text
$INTMSG
```

Fields include send time, sender, recipient, title and message body.

## Short Locate Queries

These commands relate to locate availability and cost. In v0 only read-only inquiries are allowed.

Read-only candidates:

```text
SLPRICEINQUIRE <symbol> <shares> <route>
SLAvailQuery <account> <symbol>
SLReuseQuery <symbol|ALL>
SLRouteMinCharge <route|ALLROUTE>
```

Observed/manual response prefixes:

```text
%SLRET
$SLAvailQueryRet
$SLReuseQueryRet
$SLRouteMinChargeRet
```

Blocked in v0:

```text
SLNEWORDER
SLCANCELORDER
SLOFFEROPERATION
```

Reason: these are operational locate actions, not passive data capture.

## Blocked Execution Commands

The DAS manual and example code include order-routing commands. These must be hard-blocked by the TSIS DAS capture app v0:

```text
NEWORDER
REPLACE
CANCEL
CANCEL ALL
COMPLEXORDER
SLNEWORDER
SLCANCELORDER
SLOFFEROPERATION
```

If future execution work is requested, it must live under an execution bridge contract, not under source ingestion.

## Known DAS Capacity Limits

Manual default limits observed:

| Item | Default limit | Applies to |
| --- | ---: | --- |
| Level 1 symbols | 100 | `SB <symbol> Lv1` |
| Time and sales symbols | 50 | `SB <symbol> tms` |
| Level 2 symbols | 10 | `SB <symbol> Lv2` |
| Chart symbols | 50 | `SB <symbol> DAYCHART/MINCHART` |
| Locate inquiry interval | 3 seconds | `SLPRICEINQUIRE` |
| Order rate | 50 per second | `NEWORDER`, blocked in v0 |
| Cancel rate | 100 per minute | `CANCEL`, blocked in v0 |
| Replace rate | 100 per minute | `REPLACE`, blocked in v0 |
| Complex orders | 100 per minute | `COMPLEXORDER`, blocked in v0 |
| Locate orders | 100 per minute | `SLNEWORDER`, blocked in v0 |

The screener must respect these limits by selecting a small active subscription set.

## Screener v0 Data Plan

Initial screener denominator:

| Filter | Initial rule |
| --- | --- |
| Sessions | Cover `premarket`, `regular_market` and `afterhours`. |
| Market cap | `market_cap < 100,000,000 USD`; sourced from governed TSIS reference/universe unless DAS later proves it exposes this field. |
| Price | `0.50 <= price <= 20.00 USD`. |
| Volume | Require `min_volume_shares >= 300,000`; preferred source is DAS Lv1 field `V`; if unavailable, record `null`/`unavailable` rather than inventing volume. |
Default screener v0 is contract-capped at `100` evaluated symbols per run and should decide what symbols are worth subscribing to before the capture app consumes scarce Lv1/T&S/Lv2 slots. A larger evaluated-symbol scan requires explicit `--allow-large-scan`; this expands only the serial read-only screener pass and does not raise active full-capture subscription limits. The terminal app must show TOPLIST status, candidate universe size, candidate source counts and one PASS/FAIL line per evaluated symbol in real time; persisted JSONL/CSV files remain the audit source of truth.

Recommended flow:

1. Build seed universe cumulatively:
   - manual symbol list;
   - optional DAS `SB TOPLIST` output;
   - governed TSIS market-cap reference/universe when `--scan-tsis-universe` is enabled, especially when DAS `TOPLIST` returns 0 symbols.
2. For each candidate, collect:
   - `GET SHORTINFO <symbol>`;
   - `SB <symbol> Lv1` with `ReturnFullLv1 YES`;
   - `GET LDLU <symbol>`;
   - `GET SymStatus <symbol>`;
   - optional brief `SB <symbol> tms`.
3. Apply filters:
   - price range;
   - volume;
   - `tradesAllDay`;
   - `RVOL`;
   - bid/ask spread;
   - SSR;
   - shortable/borrow availability;
   - LDLU/trading status;
   - TopList membership.
4. Emit candidate files:
   - `candidates.jsonl`;
   - `candidates.csv`;
   - `screener_manifest.json`.

## Source Parity Notes

DAS data is live broker/vendor evidence. It does not automatically replace Polygon historical data or TSIS Data Foundation datasets.

Before any field becomes model-facing, the source parity audit must declare:

- historical source;
- live DAS source;
- Polygon WebSocket source, if any;
- timestamp semantics;
- arrival/latency behavior;
- null behavior;
- whether the field is trainable, live-only, broker-only or forbidden.

Official source parity workspace:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit
```

## Current Evidence Gaps

The following need market-hours testing:

- full `$TopLst` symbol payload shape;
- whether DAS CMD API exposes any certifiable Level 3 / market-by-order depth command beyond `Lv2`;
- Lv2 response shape for a symbol with entitlement and active book;
- `MINCHART` behavior over different intraday windows;
- `GET SymStatus` dependency on prior Lv1 subscription;
- short locate query behavior with real routes;
- reconnect behavior after DAS frontend disconnect or quote server heartbeat loss.

## v0 Implementation Boundary

The current v0 terminal app implements:

- TCP socket connection to DAS CMD API;
- explicit login with redacted credential handling;
- read-only command allowlist;
- command transcript JSONL;
- raw event JSONL;
- Lv1/T&S/Lv2/TOPLIST/chart subscriptions;
- candidate-symbol market-data capture; account/broker snapshot polling remains future explicit sensitive mode;
- screener candidate generation;
- heartbeat and monitor files;
- clean unsubscribe and final summary.

The first DAS app should not implement:

- order entry;
- order cancellation;
- order replacement;
- locate order placement;
- live trading;
- ML/RL feature promotion;
- historical backfill certification.
