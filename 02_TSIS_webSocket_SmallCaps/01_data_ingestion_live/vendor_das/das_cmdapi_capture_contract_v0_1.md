# DAS CMD API Capture Contract v0_1

Status: draft operating contract  
Owner module: `02_TSIS_webSocket_SmallCaps`  
Source/vendor: DAS/Sage CMD API  
Physical live data root: `E:/TSIS/data_DAS_live`  
Default mode: read-only / data-only

## Menu

- [Purpose](#purpose)
- [Authority](#authority)
- [Non-negotiable Rules](#non-negotiable-rules)
- [Manual Operator Login Mode](#manual-operator-login-mode)
- [Physical And Code Roots](#physical-and-code-roots)
- [Run File Contract](#run-file-contract)
- [Power Loss And Resume Semantics](#power-loss-and-resume-semantics)
- [Command Allowlist](#command-allowlist)
- [Command Blocklist](#command-blocklist)
- [Data Families To Capture](#data-families-to-capture)
- [Smoke Test Objective](#smoke-test-objective)
- [Screener Contract](#screener-contract)
- [Secrets And Redaction](#secrets-and-redaction)
- [Capacity Limits](#capacity-limits)
- [Source Parity Boundary](#source-parity-boundary)
- [Implementation Boundary](#implementation-boundary)
- [Open Evidence Gaps](#open-evidence-gaps)

## Purpose

This contract defines how TSIS captures DAS CMD API data in v0.

The goal is to preserve every read-only/data-only payload that DAS CMD API can expose, without converting the ingestion module into an execution bridge and without treating broker telemetry as model-ready state.

This document must be read before implementing or running any DAS CMD API capture command in TSIS.

## Authority

This contract governs DAS live capture behavior for:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
E:/TSIS/data_DAS_live
```

It does not redefine Data Foundation semantics, historical OHLCV truth, quote-guarded overlays or model-facing feature contracts.

For historical data meaning, defer to:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations
E:/TSIS/data/README.md
```

## Non-negotiable Rules

1. DAS CMD API capture v0 is read-only and data-only.
2. DAS live payloads are stored under `E:/TSIS/data_DAS_live`.
3. DAS live payloads are not stored under `data/raw_ws`; that path is Polygon/Massive WebSocket prototype evidence.
4. Every long-running DAS capture run must write progress while running.
5. Empty DAS responses, DAS errors, disconnects and no-data observations are valid evidence and must be logged.
6. Credentials, account ids, passwords, API keys and broker secrets must never be written to markdown, JSONL, parquet metadata, logs, screenshots or manifests.
7. Order entry, cancels, replaces, complex orders and locate actions are blocked in v0.
8. No DAS field becomes model-facing until source parity and feature/state contracts approve it.

## Manual Operator Login Mode

The default TSIS DAS v0 operating mode is manual operator login.

The human operator logs into DAS Trader / Passport / frontend manually before launching the TSIS terminal app. The app must record that it is running in `manual_operator_login` mode in `pre_manifest.json` and `pid_manifest.json`.

In this mode, the app must not store, print or infer credentials. It should not send a socket `LOGIN` command unless a future run config explicitly enables `socket_login_enabled=true`.

Important limitation:

- manual frontend login may open the CMD API port and allow quote commands;
- some CMD API socket sessions may still require explicit socket login for protected account-state commands;
- if DAS returns login-required, no-response or permission errors, those outcomes are captured as evidence rather than hidden.

The smoke test must distinguish:

- command available and returned data;
- command available but returned no data;
- command blocked by permission/login/session state;
- command failed due to market/session timing.
## Physical And Code Roots
Code, docs and contracts live under:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
```

DAS live data lives under:

```text
E:/TSIS/data_DAS_live
```

Recommended physical layout:

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

The default app config should allow overriding the data root, but the default and official TSIS root is `E:/TSIS/data_DAS_live`.

## Run File Contract

Every capture run must create a new run directory before opening market subscriptions.

Required files:

| File | Required timing | Contract |
| --- | --- | --- |
| `pre_manifest.json` | Before socket connection/subscriptions | Declares intended run id, config, data root, command allowlist, blocklist version, symbols, channels and redaction policy. |
| `pid_manifest.json` | After process starts | Declares host, process id, user-visible start time, Python/app version and active output paths. |
| `heartbeat.json` | Refreshed while running | Atomic progress file with stage, current symbols/channels, line counts, bytes written, last event time and last error. |
| `command_transcript.jsonl` | Continuously | One JSON object per command/response block, including sent command with redaction, timestamps, raw response text, response line count and status. |
| `events.jsonl` | Continuously | One JSON object per DAS line/event, preserving raw line plus TSIS metadata and parser classification. |
| `subscription_state.json` | After subscribe/unsubscribe changes | Current active channels and symbols. |
| `capture.log` | Continuously | Human-readable operational log. |
| `final_summary.json` | Only on clean finish | Final counts, status, start/end times, files, bytes, channels, symbols, errors and completeness notes. |

The app may create additional derived files only after their contract is documented.

## Power Loss And Resume Semantics

The critical evidence files are `command_transcript.jsonl` and `events.jsonl`.

They must be flushed during the run so that a power loss preserves already written data. A missing `final_summary.json` means the run did not close cleanly; it does not invalidate already flushed JSONL evidence.

After an interrupted run:

1. Do not overwrite the interrupted run directory.
2. Treat it as `INCOMPLETE` unless a valid `final_summary.json` says otherwise.
3. Start a new run id for the next attempt.
4. Use the previous JSONL files as evidence, not as a mutable working file.
5. If a recovery/index step is needed, write a separate recovery manifest.

## Command Allowlist

The v0 app may send only commands in the read-only/data-only allowlist.

Session commands:

```text
LOGIN <user> <password> <account> 0  # only when explicit socket_login_enabled=true
ECHO OFF
CLIENT
ReturnFullLv1 YES
QUIT
```

Market data commands:

```text
SB <symbol> Lv1
UNSB <symbol> Lv1
SB <symbol> tms
UNSB <symbol> tms
SB <symbol> Lv2
UNSB <symbol> Lv2
SB TOPLIST
UNSB TOPLIST
SB <symbol> DAYCHART <start> <end>
UNSB <symbol> DAYCHART
SB <symbol> MINCHART <start> <end> 1
UNSB <symbol> MINCHART
```

Symbol and short-side read commands:

```text
GET SHORTINFO <symbol>
GET LDLU <symbol>
GET SymStatus <symbol>
```

Account and broker-state read commands:

```text
GET BP
GET AccountInfo
GET POSITIONS
GET ORDERS
GET TRADES
GET ROUTESTATUS
GET LOCATES
GET INTMSGS
```

Short locate read-only query candidates:

```text
SLPRICEINQUIRE <symbol> <shares> <route>
SLAvailQuery <account> <symbol>
SLReuseQuery <symbol|ALL>
SLRouteMinCharge <route|ALLROUTE>
```

Short locate read-only queries require an explicit config flag in v0 because they touch broker locate services, even when they do not place locate orders.

## Command Blocklist

The v0 app must hard-block these command prefixes before sending anything to the socket:

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

The block must be case-insensitive and must run before network send.

If future execution work is requested, it belongs under an execution bridge contract, not under this source-ingestion contract.

## Data Families To Capture

The phrase "capture all DAS data" means all DAS CMD API data available to the current account/session in read-only/data-only scope.

v0 data families:

| Family | DAS commands/responses | Capture requirement |
| --- | --- | --- |
| Session/auth | `LOGIN`, `CLIENT`, server banners | Preserve connection status and redacted login outcome. |
| Level 1 quotes | `SB Lv1`, `$Quote`, `$LDLU` side effects | Capture raw lines and parsed fields when possible. |
| Time and sales | `SB tms`, `$T&S` | Capture every raw print line received. |
| Level 2 book | `SB Lv2`, `$Lv2` | Capture raw lines or no-response evidence. |
| Top lists | `SB TOPLIST`, `$TopLst` | Capture list payload and refresh behavior. |
| Daily bars | `SB DAYCHART`, `$Bar` | Capture DAS daily chart bars as DAS source evidence. |
| Minute bars | `SB MINCHART`, `$Bar` | Capture DAS minute chart bars as DAS source evidence, not canonical TSIS 1m. |
| Short info | `GET SHORTINFO`, `$SHORTINFO`, `$STINFOEX` | Capture short-side metadata returned by DAS. |
| Trading bands/status | `GET LDLU`, `GET SymStatus`, `$LDLU`, `$SymStatus`, `$IssueStatus` | Capture status, SSR and limit bands. |
| Buying power | `GET BP` | Capture with sensitive handling. |
| Account info | `GET AccountInfo` | Capture with sensitive handling. |
| Positions | `GET POSITIONS`, `#POS`, `%POS`, `#POSEND` | Capture broker-state snapshot. |
| Orders | `GET ORDERS`, `#Order`, `%ORDER`, `#OrderEnd` | Capture broker-state snapshot. |
| Trades | `GET TRADES`, `#Trade`, `%TRADE`, `#TradeEnd` | Capture broker-state snapshot. |
| Route status | `GET ROUTESTATUS`, `$RouteStatus` | Capture route state. |
| Locates | `GET LOCATES`, `#SLOrder`, `%SLOrder`, `#SLOrderEnd` | Capture locate state only. |
| Internal messages | `GET INTMSGS`, `$INTMSG` | Capture internal broker/API messages if returned. |
| Locate queries | `SLPRICEINQUIRE`, `SLAvailQuery`, `SLReuseQuery`, `SLRouteMinCharge` | Optional read-only queries with explicit enable flag. |

## Smoke Test Objective

The smoke test is not a single-symbol quote demo.

The smoke test objective is:

```text
Prove that TSIS can capture every DAS CMD API data family available in read-only/data-only scope and persist it safely under E:/TSIS/data_DAS_live.
```

A smoke run may use one or a small number of symbols to stay within capacity limits, but it must exercise every read-only family listed in this contract, including no-response and error observations.

Minimum smoke output:

- one valid `pre_manifest.json`;
- one valid `pid_manifest.json`;
- live `heartbeat.json` updates;
- non-empty `command_transcript.jsonl`;
- `events.jsonl` with raw DAS lines or explicit no-data events;
- `subscription_state.json`;
- `capture.log`;
- `final_summary.json` if the app exits cleanly.

Smoke PASS means the capture mechanism is operational. It does not certify the fields as model-ready.

## Screener Contract

The screener selects symbols before scarce DAS subscriptions are consumed.

Screener v0 inputs may include:

- manual symbol list;
- TSIS small-cap universe;
- DAS `SB TOPLIST` output.

Screener v0 evidence should write:

```text
E:/TSIS/data_DAS_live/screener/runs/<run_id>/screener_manifest.json
E:/TSIS/data_DAS_live/screener/runs/<run_id>/candidates.jsonl
E:/TSIS/data_DAS_live/screener/runs/<run_id>/candidates.csv
```

Initial denominator filters:

| Filter | Initial rule |
| --- | --- |
| Market cap | `market_cap < 100,000,000 USD` |
| Price | `0.50 <= price <= 20.00 USD` |
| Volume | require `min_volume_shares >= 300,000`; preferred source is DAS Lv1 field `V`; if unavailable, record `null`/`unavailable` rather than inventing volume. |
| Session coverage | evaluate candidates across `premarket`, `regular_market` and `afterhours`. |

Screener filters may also include `tradesAllDay`, `RVOL`, spread, SSR, shortable status, locate availability, LDLU/status and TopList membership.

Market cap is not expected to come from DAS CMD API v0 unless DAS exposes it in a tested payload. The screener should source market cap from a governed TSIS universe/reference source and record that lineage in `screener_manifest.json`.

## Secrets And Redaction

The app must redact at least:

- username;
- password;
- account id;
- API keys/tokens;
- broker secrets;
- local private credential file content.

`LOGIN` commands in `command_transcript.jsonl` must be stored only in redacted form.

Account-state payloads may contain sensitive financial information. They can be captured locally as broker-state evidence, but must not be copied into shared docs, screenshots or public artifacts.

## Capacity Limits

Manual default DAS limits observed:

| Item | Default limit | Applies to |
| --- | ---: | --- |
| Level 1 symbols | 100 | `SB <symbol> Lv1` |
| Time and sales symbols | 50 | `SB <symbol> tms` |
| Level 2 symbols | 10 | `SB <symbol> Lv2` |
| Chart symbols | 50 | `SB <symbol> DAYCHART/MINCHART` |
| Locate inquiry interval | 3 seconds | `SLPRICEINQUIRE` |

The screener and capture app must respect these limits by design.

## Source Parity Boundary

DAS live data is source evidence.

It is not automatically:

- a Data Foundation dataset;
- a canonical 1m source;
- a model feature table;
- a label table;
- a training source;
- a production execution system.

Before model-facing use, each field must pass the official source parity audit:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit
```

## Implementation Boundary

v0 should implement:

- DAS TCP client;
- read-only command allowlist;
- hard command blocklist;
- redacted login handling;
- streaming JSONL writes;
- heartbeat and monitor files;
- clean unsubscribe/quit;
- smoke test runner covering all read-only data families;
- screener candidate output.

v0 should not implement:

- live order entry;
- cancel/replace;
- locate orders;
- execution strategy;
- ML/RL training;
- feature promotion;
- historical data certification.

## Open Evidence Gaps

These need market-hours validation:

- full `$TopLst` payload shape;
- Lv2 response shape with valid entitlement and active symbol;
- `MINCHART` behavior over intraday ranges;
- whether `GET SymStatus` requires prior Lv1 subscription in all sessions;
- behavior of read-only locate queries by route;
- reconnect behavior after DAS frontend or quote-server interruption.



