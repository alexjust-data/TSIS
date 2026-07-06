# 02_TSIS_webSocket_SmallCaps

Status: bootstrap/recovery of the live module.

Owner layer: live ingestion, streaming state, realtime feature preparation, signal routing, execution bridge, risk monitoring and live exports.

This module is the live counterpart of the historical/research stack. It must not redefine Data Foundation semantics from module `01_TSIS_backtest_SmallCaps`. Its job is to ingest live/vendor/broker data, preserve raw evidence, normalize streams, and produce live-compatible state candidates under explicit contracts.

## Current State

As of 2026-07-06 this module is partially initialized.

Active Polygon/Massive prototype evidence exists in:

- `data/raw_ws`: Polygon/Massive WebSocket raw JSONL prototype captures.
- `data/curated_ws`: normalized/parquet/DuckDB artifacts derived from those captures.
- `notebooks`: prototype notebooks for Polygon WebSocket capture and analysis.
- `notebooks/cell_code`: executable notebook support scripts for capture, normalization, partitioning, DuckDB builds, metrics and visual checks.

DAS/Sage CMD API work is governed separately:

- `01_data_ingestion_live/vendor_das`: DAS CMD API source inventory and capture contract.
- `E:/TSIS/data_DAS_live`: physical root for DAS live capture payloads.

Most numbered top-level implementation folders are currently empty scaffolding:

- `02_realtime_features`
- `03_realtime_event_engine`
- `04_signal_router`
- `05_execution_bridge`
- `06_risk_monitor`
- `07_live_logs`
- `08_live_exports`

These folders should be populated only when the relevant contract or service boundary is clear.

## Root Document Policy

The module root should contain only:

- `README.md`
- `AGENTS.md`
- `LOCAL_RULES.md`
- `CHANGELOG.md`
- `manifest.yaml`
- dependency files such as `requirements-websocket.txt`

Planning, source inventory and research documents belong under explicit owner folders:

| Document | Role | Current path |
|---|---|---|
| `00_end_points_polygon.md` | Polygon REST/WebSocket/Flat Files inventory | `01_data_ingestion_live/vendor_polygon/00_end_points_polygon.md` |
| `01_feeds_webSocket.md` | Polygon/Massive WebSocket feed and notebook design | `01_data_ingestion_live/vendor_polygon/01_feeds_webSocket.md` |
| `das_cmdapi_capture_contract_v0_1.md` | DAS read-only capture operating contract | `01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md` |
| `das_cmdapi_data_catalog_v0_1.md` | DAS CMD API data family inventory | `01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md` |
| `02_pipeline_real_time.md` | realtime system architecture note | `docs/architecture/02_pipeline_real_time.md` |
| `02_1_estudio_arquitectura_realtime_50_tickers.md` | 50 ticker capacity study | `docs/capacity_planning/02_1_estudio_arquitectura_realtime_50_tickers.md` |
| `02_2_estudio_arquitectura_realtime_200_tickers.md` | 200 ticker capacity study | `docs/capacity_planning/02_2_estudio_arquitectura_realtime_200_tickers.md` |
| `02_3_estudio_arquitectura_realtime_500_tickers.md` | 500 ticker capacity study | `docs/capacity_planning/02_3_estudio_arquitectura_realtime_500_tickers.md` |

Do not add new loose research files to the root. Put source/vendor evidence under `01_data_ingestion_live`, architecture docs under `docs`, and service code under the numbered service boundary it belongs to.

## Canonical Paths

Canonical module root:

```text
C:/TSIS_Data/02_TSIS_webSocket_SmallCaps
```

Official live data roots:

```text
Polygon/Massive prototype evidence: C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/data/raw_ws
Polygon/Massive curated prototype outputs: C:/TSIS_Data/02_TSIS_webSocket_SmallCaps/data/curated_ws
DAS/Sage CMD API live captures: E:/TSIS/data_DAS_live
```

Known legacy references observed in notebooks/scripts:

```text
C:/TSIS_Data/v1/WebSocket_SmallCaps
C:/TSIS_Data/01_webSocket_SmallCaps
```

Those paths are obsolete for this module. Any new code must resolve paths from the canonical module root or from a config/env setting.

## DAS CMD API Capture

DAS v0 capture is read-only and data-only.

Before implementing or running DAS capture, read:

```text
01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md
01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md
E:/TSIS/data_DAS_live/README.md
```

DAS live runs must write progress continuously under `E:/TSIS/data_DAS_live`, including:

- `pre_manifest.json`
- `pid_manifest.json`
- `heartbeat.json`
- `command_transcript.jsonl`
- `events.jsonl`
- `subscription_state.json`
- `capture.log`
- `final_summary.json` if the app exits cleanly

The DAS smoke test objective is to prove that TSIS can capture every DAS CMD API data family available in read-only/data-only scope, not just one symbol quote.

DAS execution commands such as `NEWORDER`, `REPLACE`, `CANCEL`, `COMPLEXORDER`, `SLNEWORDER`, `SLCANCELORDER` and `SLOFFEROPERATION` are outside v0 and must be blocked.

## Source Parity Work

The next official workstream is source parity for live-compatible ML/RL:

```text
01_data_ingestion_live/source_parity_audit/
```

Purpose:

- certify what Polygon historical/raw and Polygon WebSocket expose;
- certify what DAS/Sage CMD API exposes;
- map field-level parity for live-compatible features/state;
- identify fields that are trainable historically and reproducible live;
- identify live-only broker/execution fields that must stay out of historical model inputs unless future live logs support them.

## Operating Principle

The system does not require DAS/Sage API to reproduce Polygon historical raw. It requires the model-facing feature/state contract to be reproducible in both:

```text
historical builder from Polygon
live builder from Polygon WebSocket and/or DAS/Sage CMD API
```

ML/RL must consume governed state/features, not raw scanner rows, loose notebook outputs, or broker telemetry without a contract.
DAS v0 uses manual operator login by default: the human logs into DAS Trader / Passport / frontend before launching TSIS. The app must not write credentials. Socket `LOGIN` is only allowed if a future config explicitly enables it and redacts it.

The initial DAS screener denominator covers `premarket`, `regular_market` and `afterhours`, with `market_cap < 100,000,000 USD`, `0.50 <= price <= 20.00 USD`, and minimum volume `>= 300,000 shares` using DAS Lv1 `V` as the preferred source unless revised by contract.


