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

Broker-specific local capture work is excluded from Git by default and must stay in ignored local paths unless a sanitized subset is explicitly approved.

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
```

Known legacy references observed in notebooks/scripts:

```text
C:/TSIS_Data/v1/WebSocket_SmallCaps
C:/TSIS_Data/01_webSocket_SmallCaps
```

Those paths are obsolete for this module. Any new code must resolve paths from the canonical module root or from a config/env setting.

## Source Parity Work

The next official workstream is source parity for live-compatible ML/RL:

```text
01_data_ingestion_live/source_parity_audit/
```

Purpose:

- certify what Polygon historical/raw and Polygon WebSocket expose;
- map field-level parity for live-compatible features/state;
- identify fields that are trainable historically and reproducible live;
- identify live-only broker/execution fields that must stay out of historical model inputs unless future live logs support them.

## Operating Principle

The system does not require any broker API to reproduce Polygon historical raw. It requires the model-facing feature/state contract to be reproducible in both:

```text
historical builder from Polygon
live builder from approved live-source adapters
```

ML/RL must consume governed state/features, not raw scanner rows, loose notebook outputs, or broker telemetry without a contract.
