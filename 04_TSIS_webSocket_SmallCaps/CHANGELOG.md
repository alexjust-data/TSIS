## 2026-07-24 | DAS CMDAPI PASS-candidate replay and locate extraction corrected

- Added/recorded the operator-correct flow for this live capture objective: load the PASS rows from `C:/TSIS_Data/data/screener/runs/das_cmdapi_live_20260724T165627Z/candidates.csv` with `--candidate-file`, `--candidate-file-status PASS` and `--skip-screener`.
- This mode does not call `TOPLIST` as a candidate filter and does not append the governed TSIS market-cap universe. Use `--scan-tsis-universe` only when explicitly investigating universe coverage, not when replaying the TSIS screener output.
- Run `das_cmdapi_live_candidate_file_pass_max_readonly_20260724T195551Z` confirmed login, loaded 17 PASS candidates and captured read-only Lv1, T&S, Lv2, chart, `SHORTINFO`, `LDLU`, `SymStatus`, account-state and locate inquiry evidence. It later closed with DAS socket `ConnectionResetError(10054)`, so `final_summary.json` is `FAIL`; treat captured evidence as valid up to the socket close, not as a clean full-session close.
- Derived locate outputs were materialized under `raw_cmdapi/runs/das_cmdapi_live_candidate_file_pass_max_readonly_20260724T195551Z/derived/`: `locate_price_inquiries.csv`, `locate_availability.csv`, `locate_reuse.csv`, `locate_route_min_charge.csv` and `locate_extraction_summary.json`.
- Snapshot extraction found 34/34 `%SLRET` price rows for 17 symbols: 17 on `SAGE` labelled `live_broker_route` and 17 on `TESTSL` labelled `test_route`; no account id, auth data or locate/order token is included in the derived tables.
- Login/account guard hardened: if DAS returns invalid account/password while account-state or locate capture is enabled, the run aborts unless explicitly forced with `--allow-invalid-login-continue`.
- Validation evidence: `unittest` contract suite passed with 15 tests, and candidate-file max-readonly dry-run passed with zero validation failures.

## 2026-07-24 | DAS CMDAPI max read-only universe scan hardened

- Preserved the existing DAS scanner behavior: seed symbols plus `SB TOPLIST` remain part of the candidate source.
- Added opt-in `--scan-tsis-universe` so the screener also appends the governed TSIS market-cap reference universe when DAS `TOPLIST` is empty or incomplete.
- Added explicit `--allow-large-scan` to permit evaluated-symbol counts above the default 100-symbol contract cap; without that flag, the 100-symbol cap remains enforced.
- Added CLI wait controls for screener/query/toplist/full-capture timing and active-only reference filtering by default.
- `--max-readonly` still requests the previous read-only market/account/locate scope: session setup, TOPLIST, Lv1/T&S/Lv2/charts, `SHORTINFO`, `LDLU`, `SymStatus`, account state, route status, `GET LOCATES`, `SLReuseQuery`, `SLRouteMinCharge`, `SLAvailQuery` and `SLPRICEINQUIRE`.
- Broker safety unchanged: order, cancel, replace, complex-order and locate-order prefixes remain blocked: `NEWORDER`, `REPLACE`, `CANCEL`, `COMPLEXORDER`, `SLNEWORDER`, `SLCANCELORDER`, `SLOFFEROPERATION`.
- Login handling now aborts by default when DAS returns invalid account/password and account-state or locate capture is enabled; `--allow-invalid-login-continue` is required to force a degraded run.
- Current operator-directed DAS CMDAPI data root is `C:/TSIS_Data/data` when supplied through `--data-root`; raw audit files write to `raw_cmdapi/runs/<run_id>` and screener files to `screener/runs/<run_id>` under that root.
- Validation evidence: `unittest` contract suite passed with 13 tests, and dry-run `das_cmdapi_dry_run_tsis_universe_max_readonly_20260724T_test` passed with zero validation failures.

## 2026-07-22 | root path migration | live module moved to 04_TSIS_webSocket_SmallCaps

- Canonical root is now `C:/TSIS_Data/04_TSIS_webSocket_SmallCaps`.
- Legacy root `C:/TSIS_Data/02_TSIS_webSocket_SmallCaps` must resolve through `C:/TSIS_Data/PATH_MIGRATION_2026_07_22.md`.
- Upstream Data Foundation root is now `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION`.
- No live service behavior, broker command authority or production capture scope changed.

# Changelog - 04_TSIS_webSocket_SmallCaps

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
