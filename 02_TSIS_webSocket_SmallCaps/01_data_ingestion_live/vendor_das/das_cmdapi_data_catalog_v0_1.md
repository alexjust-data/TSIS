# DAS CMD API Data Catalog v0_1

Status: draft source inventory  
Owner module: `02_TSIS_webSocket_SmallCaps`  
Physical live data root: `E:/TSIS/data_DAS_live`  
Contract reference:

- `C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md`

Reference evidence:

- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/CMD API Manual.pdf`
- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/DAS_CMD_API_First_Connection.ipynb`
- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/das_cmdapi_full_readonly_dump_SOXS_20260703_105830.json`
- `C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/DasTrades_API/das_cmdapi_transcript_SOXS_*.json`

## Menu

- [Purpose](#purpose)
- [Core Rule](#core-rule)
- [Physical Data Layout](#physical-data-layout)
- [Long-running Capture Requirements](#long-running-capture-requirements)
- [Authentication And Session Data](#authentication-and-session-data)
- [Market Data Streams](#market-data-streams)
  - [Level 1 Quotes](#level-1-quotes)
  - [Time And Sales](#time-and-sales)
  - [Level 2 Book](#level-2-book)
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

DAS live captures must be stored under:

```text
E:/TSIS/data_DAS_live
```

Code, documentation, source parity notes and service wrappers belong under:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
```

Do not store DAS live payloads under `data/raw_ws`; that path is preserved for the existing Polygon/Massive WebSocket prototype.

## Core Rule

Default DAS work in TSIS is read-only and data-only.

The first application must capture live market, account-state and broker-state evidence. It must not send orders, cancels, replaces, locate orders, route actions or execution commands.

Secrets, usernames, passwords, account ids and broker credentials must not be written to markdown, JSONL, parquet metadata, logs, screenshots or manifests.

## Physical Data Layout

Recommended root:

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
        subscription_state.json
        capture.log
        final_summary.json
  screener/
    runs/
      <run_id>/
        screener_manifest.json
        candidates.jsonl
        candidates.csv
  catalog/
    das_cmdapi_command_catalog_v0_1.json
    das_cmdapi_field_inventory_v0_1.md
```

The raw JSONL files should preserve the original DAS text lines and add TSIS wrapper metadata such as receive timestamp, command context, socket session id, subscription id, symbol, parser version and raw line hash.

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
| `subscription_state.json` | Current subscribed symbols and channels. |
| `capture.log` | Human-readable run log. |
| `final_summary.json` | Final counts and status if the app exits cleanly. |

If power is lost, `final_summary.json` may be missing, but all flushed JSONL lines already written remain valid evidence.

## Authentication And Session Data

Manual operator login is the default operating mode for TSIS DAS v0. The human logs into DAS Trader / Passport / frontend before launching the app. The app must not store or print credentials. Socket `LOGIN` is only allowed when explicitly enabled by future config and must be redacted.
Observed flow:

```text
LOGIN <user> <password> <account> 0  # optional only when explicit socket_login_enabled=true
ECHO OFF
CLIENT
ReturnFullLv1 YES
```

Important behavior:

- DAS frontend login/passport does not automatically authenticate every CMD API socket session.
- Each socket session should explicitly login if account-state or protected commands are needed.
- Quote-only commands may work without API logon if DAS is configured with disabled logon check, but TSIS should not rely on that.
- Credentials must come from environment variables or a private file that is never committed or logged.

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
The screener should decide what symbols are worth subscribing to before the capture app consumes scarce Lv1/T&S/Lv2 slots.

Recommended flow:

1. Build seed universe:
   - manual symbol list;
   - existing TSIS small-cap universe;
   - optional DAS `SB TOPLIST` output.
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
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit
```

## Current Evidence Gaps

The following need market-hours testing:

- full `$TopLst` symbol payload shape;
- Lv2 response shape for a symbol with entitlement and active book;
- `MINCHART` behavior over different intraday windows;
- `GET SymStatus` dependency on prior Lv1 subscription;
- short locate query behavior with real routes;
- reconnect behavior after DAS frontend disconnect or quote server heartbeat loss.

## v0 Implementation Boundary

The first DAS app should implement:

- TCP socket connection to DAS CMD API;
- explicit login with redacted credential handling;
- read-only command allowlist;
- command transcript JSONL;
- raw event JSONL;
- Lv1/T&S/Lv2/TOPLIST/chart subscriptions;
- account/broker snapshot polling;
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











