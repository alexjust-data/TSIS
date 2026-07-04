# AGENTS - 02_TSIS_webSocket_SmallCaps

This file gives agent-specific instructions for work inside the live module.

## First Reads

Before making changes in this module, read:

1. `README.md`
2. `LOCAL_RULES.md`
3. `CHANGELOG.md`
4. `manifest.yaml`
5. `C:\TSIS_Data\00_CTO\TSIS_LAB_ARCHITECTURE_v2.md`

If the work touches Data Foundation semantics, also read the relevant contract from:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
```

## Current Module Reality

The module is not a mature service tree yet.

Active artifacts currently live in:

- `data/raw_ws`
- `data/curated_ws`
- `notebooks`
- `notebooks/cell_code`

Source and documentation evidence is organized in:

- `01_data_ingestion_live/vendor_polygon`
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
- Do not issue broker order commands unless explicitly asked.
- Do not train ML/RL directly from scanner rows or raw live events without a governed state/feature contract.

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

- resolve paths from the canonical root;
- avoid hardcoded legacy roots;
- accept run labels as parameters;
- write new outputs under a new run label unless explicitly regenerating a known prototype.

## Known Issue To Watch

Some prototype notebooks reference older roots:

```text
C:\TSIS_Data\v1\WebSocket_SmallCaps
C:\TSIS_Data\01_webSocket_SmallCaps
```

Those references must be audited before any service extraction or replay. Do not mass-edit notebook outputs unless the task is explicitly a notebook migration.
