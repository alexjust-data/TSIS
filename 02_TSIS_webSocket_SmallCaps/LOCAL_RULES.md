# Local Rules - 02_TSIS_webSocket_SmallCaps

These rules apply inside:

```text
C:\TSIS_Data\02_TSIS_webSocket_SmallCaps
```

## Authority

This module owns live ingestion and live operation artifacts. It does not own historical Data Foundation truth.

For historical market data, contracts and source-of-truth semantics, defer to:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
C:\TSIS_Data\00_CTO\TSIS_LAB_ARCHITECTURE_v2.md
```

## Path Discipline

Use the canonical module root:

```text
C:\TSIS_Data\02_TSIS_webSocket_SmallCaps
```

Do not create new artifacts under legacy paths such as:

```text
C:\TSIS_Data\v1\WebSocket_SmallCaps
C:\TSIS_Data\01_webSocket_SmallCaps
```

Existing notebook output references to those legacy paths must be treated as historical evidence of an older prototype, not as current authority.

## Data Handling

- `data/raw_ws` is raw capture evidence. Do not rewrite it destructively.
- `data/curated_ws` is derived prototype output. It can be regenerated, but any regeneration must preserve run labels or write a new run label.
- Notebook outputs are evidence, not institutional datasets.
- Large capture files should not be committed or moved casually.
- Secrets and API keys must never be written into notebooks, markdown, JSONL, parquet metadata, logs or screenshots.

## Live Trading Safety

Default work in this module is read-only/data-only.

Do not send live orders, cancels, replaces or broker actions unless the user explicitly requests execution work for a controlled environment.

For DAS/Sage CMD API exploration, default to read-only commands:

- account state
- route status
- short info / locate status queries
- Lv1/Lv2/T&S subscriptions
- chart subscriptions

Order entry, cancels, replaces, locate orders and route actions require an explicit execution scope.

## Documentation Layout

Root files are reserved for module governance:

- `README.md`
- `AGENTS.md`
- `LOCAL_RULES.md`
- `CHANGELOG.md`
- `manifest.yaml`

Vendor/source inventories belong under `01_data_ingestion_live`.

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
