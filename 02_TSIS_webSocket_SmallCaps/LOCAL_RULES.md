# Local Rules - 02_TSIS_webSocket_SmallCaps

These rules apply inside:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
```

## Authority

This module owns live ingestion and live operation artifacts. It does not own historical Data Foundation truth.

For historical market data, contracts and source-of-truth semantics, defer to:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations
C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
E:/TSIS/data/README.md
```

For DAS CMD API capture behavior, defer to:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md
E:/TSIS/data_DAS_live/README.md
```

## Path Discipline

Use the canonical module root:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
```

Use the official DAS live physical root:

```text
E:/TSIS/data_DAS_live
```

Do not create new artifacts under legacy paths such as:

```text
C:/TSIS_Data/v1/WebSocket_SmallCaps
C:/TSIS_Data/01_webSocket_SmallCaps
```

Existing notebook output references to those legacy paths must be treated as historical evidence of an older prototype, not as current authority.

## Data Handling

- `data/raw_ws` is Polygon/Massive raw capture evidence. Do not rewrite it destructively.
- `data/curated_ws` is Polygon/Massive derived prototype output. It can be regenerated, but any regeneration must preserve run labels or write a new run label.
- `E:/TSIS/data_DAS_live` is the official physical root for DAS CMD API live capture payloads.
- Notebook outputs are evidence, not institutional datasets.
- Large capture files should not be committed or moved casually.
- Secrets and API keys must never be written into notebooks, markdown, JSONL, parquet metadata, logs or screenshots.
- Account-state DAS payloads may contain sensitive broker/account telemetry and must not be copied into shared evidence casually.

## Live Trading Safety

Default work in this module is read-only/data-only.

Do not send live orders, cancels, replaces or broker actions unless the user explicitly requests execution work for a controlled environment under a separate execution contract.

For DAS/Sage CMD API exploration and capture, default to read-only commands:

- account state;
- route status;
- short info / locate status queries;
- Lv1/Lv2/T&S subscriptions;
- TopList subscriptions;
- chart subscriptions;
- internal messages if returned.

Order entry, cancels, replaces, locate orders and route actions are blocked in v0.

Blocked command prefixes:

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

## DAS Long-running Run Contract

Every DAS capture run must write progress while running:

- `pre_manifest.json`
- `pid_manifest.json`
- `heartbeat.json`
- `command_transcript.jsonl`
- `events.jsonl`
- `subscription_state.json`
- `capture.log`
- `final_summary.json` if the app exits cleanly

If power is lost, do not overwrite the interrupted run. Preserve flushed JSONL evidence and start a new run id.

## Documentation Layout

Root files are reserved for module governance:

- `README.md`
- `AGENTS.md`
- `LOCAL_RULES.md`
- `CHANGELOG.md`
- `manifest.yaml`

Vendor/source inventories and capture contracts belong under `01_data_ingestion_live`.

Feature contracts belong under `02_realtime_features`.

Execution bridge contracts belong under `05_execution_bridge`.

Risk rules belong under `06_risk_monitor`.

Live logs and exports belong under `07_live_logs` and `08_live_exports` only after their schemas are declared.

## Source Parity Gate

Before ML/RL features are promoted, each model-facing field must declare:

- historical source;
- live source;
- timestamp/cutoff semantics;
- latency/arrival semantics;
- null/missing behavior;
- whether it is trainable, live-only, broker-only or forbidden.

The official place for this audit is:

```text
01_data_ingestion_live/source_parity_audit/
```
DAS v0 uses manual operator login by default: the human logs into DAS Trader / Passport / frontend before launching TSIS. The app must not write credentials. Socket `LOGIN` is only allowed if a future config explicitly enables it and redacts it.

The initial DAS screener denominator covers `premarket`, `regular_market` and `afterhours`, with `market_cap < 100,000,000 USD`, `0.50 <= price <= 20.00 USD`, and minimum volume `>= 300,000 shares` using DAS Lv1 `V` as the preferred source unless revised by contract.


