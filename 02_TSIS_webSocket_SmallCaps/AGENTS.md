# AGENTS - 02_TSIS_webSocket_SmallCaps

This file gives agent-specific instructions for work inside the live module.

## First Reads

Before making changes in this module, read:

1. `README.md`
2. `LOCAL_RULES.md`
3. `CHANGELOG.md`
4. `manifest.yaml`
5. `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`

If the work touches Data Foundation semantics, also read the relevant contract from:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations
```

If the work touches DAS/Sage CMD API, DAS live capture, DAS screeners or DAS source parity, also read:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md
E:/TSIS/data_DAS_live/README.md
```

## Current Module Reality

The module is not a mature service tree yet.

Polygon/Massive prototype artifacts currently live in:

- `data/raw_ws`
- `data/curated_ws`
- `notebooks`
- `notebooks/cell_code`

DAS/Sage CMD API live payloads must live in:

```text
E:/TSIS/data_DAS_live
```

Source and documentation evidence is organized in:

- `01_data_ingestion_live/vendor_polygon`
- `01_data_ingestion_live/vendor_das`
- `01_data_ingestion_live/source_parity_audit`
- `docs/architecture`
- `docs/capacity_planning`

Most numbered service folders are placeholders. Do not assume that an empty folder has an implemented contract.

## Do Not

- Do not add loose research/planning documents to the module root.
- Do not move documents without updating references, `README.md`, `manifest.yaml`, and `CHANGELOG.md`.
- Do not treat notebook prototype outputs as institutional datasets.
- Do not overwrite raw captures.
- Do not write API keys, account credentials or broker secrets to disk.
- Do not write DAS live payloads under `data/raw_ws`; use `E:/TSIS/data_DAS_live`.
- Do not issue broker order commands unless explicitly asked under a separate execution scope.
- Do not train ML/RL directly from scanner rows, DAS live events or raw live events without a governed state/feature contract.

## DAS Capture Rules

DAS CMD API v0 is read-only/data-only.

Every long-running DAS capture run must write:

- `pre_manifest.json`
- `pid_manifest.json`
- `heartbeat.json`
- `command_transcript.jsonl`
- `events.jsonl`
- `subscription_state.json`
- `capture.log`
- `final_summary.json` if the app exits cleanly

A power loss may leave no `final_summary.json`; already flushed JSONL evidence remains valid and must not be overwritten.

The DAS smoke test objective is to capture every DAS CMD API data family available in read-only/data-only scope, including no-response and error observations.

Hard-blocked v0 command prefixes:

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

## Preferred Work Pattern

For audits:

1. inventory existing files;
2. identify canonical and legacy paths;
3. read schemas and manifests from raw/curated runs;
4. preserve source references with file paths and line references where useful;
5. write an audit document under the correct module area;
6. update `CHANGELOG.md`.

For source parity work:

```text
01_data_ingestion_live/source_parity_audit/
```

For code that reads/writes module data:

- resolve code paths from the canonical module root;
- use `E:/TSIS/data_DAS_live` for DAS live payloads;
- avoid hardcoded legacy roots;
- accept run labels as parameters;
- write new outputs under a new run label unless explicitly regenerating a known prototype.

## Known Issue To Watch

Some prototype notebooks reference older roots:

```text
C:/TSIS_Data/v1/WebSocket_SmallCaps
C:/TSIS_Data/01_webSocket_SmallCaps
```

Those references must be audited before any service extraction or replay. Do not mass-edit notebook outputs unless the task is explicitly a notebook migration.
DAS v0 uses manual operator login by default: the human logs into DAS Trader / Passport / frontend before launching TSIS. The app must not write credentials. Socket `LOGIN` is only allowed if a future config explicitly enables it and redacts it.

The initial DAS screener denominator covers `premarket`, `regular_market` and `afterhours`, with `market_cap < 100,000,000 USD`, `0.50 <= price <= 20.00 USD`, and minimum volume `>= 300,000 shares` using DAS Lv1 `V` as the preferred source unless revised by contract.


