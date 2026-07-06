# Changelog - 02_TSIS_webSocket_SmallCaps

## 2026-07-06

### DAS CMD API capture contract baseline

- Added `01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md`.
- Added `01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md` as the DAS read-only data family inventory.
- Added `01_data_ingestion_live/vendor_das/README.md` and linked the capture contract before the catalog.
- Added `E:/TSIS/data_DAS_live/README.md` as the physical live data plane README for DAS CMD API payloads.
- Declared that DAS live payloads must live under `E:/TSIS/data_DAS_live`, not under `data/raw_ws`.
- Declared DAS v0 as read-only/data-only with hard-blocked execution command prefixes.
- Declared mandatory long-running run files: `pre_manifest.json`, `pid_manifest.json`, `heartbeat.json`, `command_transcript.jsonl`, `events.jsonl`, `subscription_state.json`, `capture.log`, and `final_summary.json` on clean exit.
- Updated `README.md`, `AGENTS.md`, `LOCAL_RULES.md`, `manifest.yaml`, and `01_data_ingestion_live/README.md` so future agents inherit the same DAS contract.
- Updated `manifest.yaml` to point to `TSIS_LAB_ARCHITECTURE_v3.md` and to declare the DAS live physical data root.
## 2026-07-03

### Governance bootstrap

- Created initial module governance docs:
  - `README.md`
  - `AGENTS.md`
  - `LOCAL_RULES.md`
  - `CHANGELOG.md`
- Classified the module as bootstrap/recovery state rather than production service state.
- Identified active artifact areas:
  - `data/raw_ws`
  - `data/curated_ws`
  - `notebooks`
  - `notebooks/cell_code`
- Identified placeholder service folders:
  - `01_data_ingestion_live`
  - `02_realtime_features`
  - `03_realtime_event_engine`
  - `04_signal_router`
  - `05_execution_bridge`
  - `06_risk_monitor`
  - `07_live_logs`
  - `08_live_exports`
  - `configs`
  - `monitoring`
  - `runtime`
  - `src`
  - `tests`
- Documented that loose root markdown files are useful but should be migrated into explicit documentation folders after link/reference audit.

### Known issues

- `notebooks/cell_code/_ws_common.py` references:

```text
C:\TSIS_Data\01_webSocket_SmallCaps
```

- Notebooks contain older references to:

```text
C:\TSIS_Data\v1\WebSocket_SmallCaps
```

These paths are not the canonical current module root and must be corrected or treated as legacy evidence before further service extraction.

### Next intended work

- Create `01_data_ingestion_live/source_parity_audit/`.
- Build a field-level Polygon historical/raw vs Polygon WebSocket vs DAS/Sage CMD API parity audit.
- Produce a live-compatible feature/state matrix for ML/RL.

### Manifest bootstrap

- Initialized `manifest.yaml` with canonical root, active artifact paths, placeholder paths, loose root document migration targets and known legacy path references.

### Documentation relocation and path cleanup

- Created documentation owner folders:
  - `01_data_ingestion_live/vendor_polygon`
  - `01_data_ingestion_live/source_parity_audit`
  - `docs/architecture`
  - `docs/capacity_planning`
- Moved loose root planning documents into their owner folders.
- Added README files to the new documentation folders.
- Updated `README.md`, `AGENTS.md`, and `manifest.yaml` to reflect the migrated structure.
- Updated `notebooks/cell_code/_ws_common.py` so `PROJECT_ROOT` resolves from `TSIS_WS_ROOT` or from the module location instead of the obsolete `C:\TSIS_Data\01_webSocket_SmallCaps` path.

### Remaining legacy evidence

- Prototype notebooks still contain historical output/path references to `C:\TSIS_Data\v1\WebSocket_SmallCaps`. These remain untouched as evidence until a notebook migration is explicitly performed.


