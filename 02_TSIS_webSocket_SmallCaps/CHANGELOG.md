# Changelog - 02_TSIS_webSocket_SmallCaps

## 2026-07-06

### Local broker integration exclusion

- Declared broker-specific local integration artifacts as ignored by default in `.gitignore`.
- Removed local broker integration docs, scaffolds, configs and tests from the Git index while preserving local files on disk.
- Public module docs now avoid pointing to ignored local broker paths.

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
- Build a field-level Polygon historical/raw vs live-source adapter parity audit.
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
