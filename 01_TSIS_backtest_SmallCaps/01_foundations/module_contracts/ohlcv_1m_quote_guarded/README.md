# OHLCV 1m Quote-Guarded Governance

## Role

This folder centralizes the institutional documentation for the
`ohlcv_1m_quote_guarded_v0_1` workstream.

The workstream exists to address raw one-minute bars whose OHLC components are
incompatible with the observed quote book during extended-hours market data
review.

This folder is the entry point for the topic. It prevents the decision trail
from being scattered across generic `module_contracts/`, dataset contracts,
validators, policies and inspection dossiers without a single map.

## Current Documents

- `ohlcv_1m_quote_guarded_single_reading_v0_1.md`
  - consolidated human reading for the complete workstream;
  - explains the problem, source evidence, proposed architecture, documentation
    surfaces, pipeline stages, consumer rules and open gates.
- `ohlcv_1m_quote_guarded_repair_runbook_v0_1.md`
  - executable runbook for the manifest-first repair audit;
  - records the full-universe command, smoke command, resumability model,
    promoted outputs and exact repair semantics.
- `ohlcv_1m_quote_guarded_live_supervision_validation_protocol_v0_1.md`
  - operational protocol for long-running v0_2 full-universe jobs;
  - records the live-run issue, supervisor, validator, terminal layout,
    restart rules and validation invariants.

## Governed Concept

Planned dataset identity:

```text
ohlcv_1m_quote_guarded_v0_1
```

Planned role:

```text
derived quote-guarded one-minute OHLC view
```

Core storage model:

```text
raw ohlcv_1m + repair_manifest = ohlcv_1m_quote_guarded view
```

This workstream does not duplicate the complete 20-year OHLCV 1m universe into
a second corrected tree. The first governed artifact is a repair overlay:

- raw bars remain immutable under `E:/TSIS/data/ohlcv_1m`;
- the repair run reads quotes from `D:/quotes` while E-root quotes parity is
  still pending;
- only affected ticker-minutes are written into repair shards/manifests;
- loaders apply the delta in memory and return a quote-guarded view;
- no raw parquet is hand-edited or overwritten.

Active v0_2 run shards live under:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838/repair_shards/
```

Each shard is a ticker-month repair manifest. A high `repair_rows` count means
the manifest found many affected rows, including VWAP-invalid rows. It does not
mean the run created that many full replacement bars.

It is not:

- a replacement for `ohlcv_1m_raw_v0_1`;
- an executed trade reconstruction;
- a real VWAP reconstruction;
- a live feed;
- an execution simulator input;
- or a final Polygon-trades-rebuilt layer.

Executable surfaces:

- `scripts/inspection/minute/build_ohlcv_1m_quote_guarded_repairs.py`
- `scripts/run_ohlcv_1m_quote_guarded_repair.ps1`
- `scripts/inspection/minute/build_ohlcv_1m_quote_guarded_repairs_v0_2.py`
- `scripts/run_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
- `scripts/monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
- `scripts/supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
- `scripts/validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
- `src/data/ohlcv_1m_quote_guarded.py`

## Live Run Supervision And Validation

Full-universe v0_2 runs are long-lived ticker-worker jobs. They must be
supervised through telemetry, not by manually inspecting raw folders.

Operational controls:

- `monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
  - read-only live status surface for humans;
  - shows started ticker status, month progress, shard count and latest
    heartbeats.
- `supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
  - long-running watchdog for one `RunRoot`;
  - does not mutate raw data;
  - restarts the v0_2 runner only when no matching runner process is visible,
    no final summary exists and output telemetry is stale.
- `validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1`
  - independent validation loop over persisted run artifacts;
  - writes reports under `<RunRoot>/validation/`;
  - validates JSON readability, stable shard readability, summary-vs-shard row
    totals and quote-envelope invariants on sampled stable shards.

During an active run the validator intentionally ignores very recent shards by
age threshold. This avoids false failures while a parquet file is still being
written.

## Companion Surfaces To Create

The complete foundation package should eventually include:

- `canonical_schemas/ohlcv_1m/ohlcv_1m_quote_guarded_schema_contract.md`
- `contract_registry/dataset_contracts/ohlcv_1m_quote_guarded_dataset_contract_v0_1.md`
- `data_consumption_policies/ohlcv_1m_quote_guarded_consumption_policy.md`
- `dataset_registry/ohlcv_1m/ohlcv_1m_quote_guarded_registry_entry.yaml`
- `validators/ohlcv_1m/ohlcv_1m_quote_guarded_validators.md`
- `inspection_dossiers/1m_quote_guarded/`
- `data_quality_report/families/ohlcv_1m_quote_guarded_quality_report_v0_1.md`

## Operational Outputs

Heavy run outputs should not live in `01_foundations`.

Exploratory and audit runs should live under:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/ohlcv_1m_quote_guard_audit/<run_id>/
```

Promoted data-foundation outputs, if created, should live under:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/
```

The promoted artifact remains a manifest/overlay unless a later contract
explicitly creates a physical corrected tree. The expected promoted artifact is
the institutional list of affected minutes and their quote-guarded OHLC
replacement fields, not a full-market parquet copy.

## Maintenance Rule

Update this folder when:

- the quote-guarded protocol changes;
- the dataset identity changes;
- the repair manifest layout changes;
- a pilot or full audit run is promoted;
- DAS, event engines or backtests start consuming the layer;
- extended-hours trades become available and supersede the quote-guarded
  provisional repair semantics.
- consumers bypass the official loader/API and hand-edit raw bars.
