# DAS CMD API Capture Contract v0_1

Status: draft operating contract  
Owner module: `04_TSIS_webSocket_SmallCaps`  
Source/vendor: DAS/Sage CMD API  
Physical live data root: default `E:/TSIS/data_DAS_live`; current operator override `C:/TSIS_Data/data` when supplied through `--data-root`  
Default mode: read-only / data-only

## Menu

- [Purpose](#purpose)
- [Authority](#authority)
- [Non-negotiable Rules](#non-negotiable-rules)
- [Terminal Prompt Socket Login Mode](#terminal-prompt-socket-login-mode)
- [Physical And Code Roots](#physical-and-code-roots)
- [Data Storage Architecture](#data-storage-architecture)
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
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps
E:/TSIS/data_DAS_live
C:/TSIS_Data/data  # current operator-directed read-only capture root when passed as --data-root
```

It does not redefine Data Foundation semantics, historical OHLCV truth, quote-guarded overlays or model-facing feature contracts.

For historical data meaning, defer to:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations
E:/TSIS/data/README.md
```

## Non-negotiable Rules

1. DAS CMD API capture v0 is read-only and data-only.
2. DAS live payloads are stored under the configured DAS data root. Default contract root is `E:/TSIS/data_DAS_live`; the current operator-directed read-only run root is `C:/TSIS_Data/data` when passed as `--data-root`.
3. DAS live payloads are not stored under `data/raw_ws`; that path is Polygon/Massive WebSocket prototype evidence.
4. Every long-running DAS capture run must write progress while running.
5. Empty DAS responses, DAS errors, disconnects and no-data observations are valid evidence and must be logged.
6. Credentials, account ids, passwords, API keys and broker secrets must never be written to markdown, JSONL, parquet metadata, logs, screenshots or manifests.
7. Order entry, cancels, replaces, complex orders and locate actions are blocked in v0.
8. No DAS field becomes model-facing until source parity and feature/state contracts approve it.

## Terminal Prompt Socket Login Mode

The default TSIS DAS v0 operating mode is terminal-prompt socket login.

The human operator launches the TSIS terminal app. The app asks for DAS username, password and account in the terminal, opens the DAS CMD API socket, sends `LOGIN <user> <password> <account> 0`, and stores only the redacted command in `command_transcript.jsonl`.

Credentials must remain in process memory only. They must not be written to markdown, JSONL, manifests, logs, screenshots, config files or shell history. `pre_manifest.json` must record that terminal credential prompting was used and that credentials were not written to disk.

The checked-in/example config keeps `socket_login_enabled=false` so LOGIN cannot be sent by generic command validation. The terminal app enables socket login only inside the live capture runtime after prompting the operator.

Important limitation:

- DAS frontend/Passport state can still affect CMD API permissions;
- if DAS returns login-required, no-response or permission errors, those outcomes are captured as evidence rather than hidden;
- protected broker/account-state commands are not part of the default candidate-symbol capture path in v0.

The smoke test must distinguish:

- command available and returned data;
- command available but returned no data;
- command blocked by permission/login/session state;
- command failed due to market/session timing.

## Physical And Code Roots
Code, docs and contracts live under:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps
```

DAS live data default/legacy contract root:

```text
E:/TSIS/data_DAS_live
```

Current operator-directed DAS CMDAPI read-only capture root:

```text
C:/TSIS_Data/data
```

The app config and CLI may override the data root. For the 2026-07-24 max read-only pull, `--data-root C:/TSIS_Data/data` is the intended physical root. This does not promote the capture to Data Foundation authority.

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
| `candidate_registry.jsonl` | Continuously / after screener decisions | One JSON object per evaluated or passing ticker, linking screener decision, capture plan, raw refs and normalized paths. |
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
LOGIN <user> <password> <account> 0  # terminal app only; credentials prompted and transcript redacted
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
| Level 3 / market-by-order depth | Not certified in v0 | Do not promise or capture as L3 until a DAS command/payload is documented, allowlisted, parsed and smoke-tested. |
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
Prove that TSIS can capture every DAS CMD API data family available in read-only/data-only scope and persist it safely under the configured DAS data root.
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
- DAS `SB TOPLIST` output;
- governed TSIS market-cap reference/universe.

The scanner must preserve the previous behavior and add new sources cumulatively: seed symbols and `TOPLIST` remain candidates, and `--scan-tsis-universe` appends the governed TSIS reference universe when `TOPLIST` is empty or incomplete.

Default screener v0 is capped at `100` evaluated symbols per run, matching the observed DAS Level 1 default limit. A larger evaluated-symbol scan requires explicit `--allow-large-scan`; this only expands the serial read-only screener pass and does not raise active Lv1/T&S/Lv2/chart subscription limits or permit any execution command.

The terminal app must print the screener process live: TOPLIST status, candidate universe size, and one PASS/FAIL line per evaluated symbol including price, volume, market cap, session and failure reasons. The persisted JSONL/CSV evidence remains the audit source of truth.

Screener v0 evidence should write:

```text
<configured_das_data_root>/screener/runs/<run_id>/screener_manifest.json
<configured_das_data_root>/screener/runs/<run_id>/candidates.jsonl
<configured_das_data_root>/screener/runs/<run_id>/candidates.csv
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

The full-capture app must respect active subscription limits by design. `--allow-large-scan` may evaluate more symbols serially in the screener, but it does not raise active subscription limits for full capture.

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
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/01_data_ingestion_live/source_parity_audit
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
