# RunPreflight Implementation Plan v0.1

Status: EXECUTION_MICRO_PLAN
Date: 2026-07-28
Scope: first executable DATA gate for `BACKTEST_VERTICAL_SLICE_V0_1`.

This is not an architecture chapter. It is the short execution checklist for the first code increment.

## 1. Objective

Implement `RunPreflight` so no market data enters the engine until the run context is resolved and authorized.

`RunPreflight` must fail closed when a run cannot resolve:

```text
dataset
universe
signal/execution/valuation price views
session policy
timezone
missing-data policy
corporate-action policy
candidate dataset authorization
required manifests
```

## 2. Files To Create

```text
src/tsis_backtest/preflight/contracts.py
src/tsis_backtest/preflight/registries.py
src/tsis_backtest/preflight/manifests.py
src/tsis_backtest/preflight/run_preflight.py
tests/unit/test_run_preflight.py
```

## 3. Minimum Contracts

```text
RunDataRequest
PriceViewAuthorization
PriceViewPolicy
CandidateConsumptionPolicy
MissingDataPolicy
CorporateActionPolicy
DatasetDefinition
UniverseDefinition
ResolvedDataContext
MarketDataBar1m
DataPreflightReport
```

## 4. First Fail-Closed Validations

```text
dataset unknown -> DATASET_NOT_FOUND
dataset root missing -> DATASET_ROOT_NOT_FOUND
price view unauthorized -> PRICE_VIEW_NOT_AUTHORIZED
universe unknown -> UNIVERSE_NOT_FOUND
candidate without consumption policy -> CANDIDATE_POLICY_REQUIRED
candidate without validation manifest -> CANDIDATE_VALIDATION_MANIFEST_REQUIRED
candidate validation manifest path missing -> CANDIDATE_VALIDATION_MANIFEST_NOT_FOUND
candidate run purpose not permitted -> CANDIDATE_RUN_PURPOSE_NOT_PERMITTED
requested symbol outside universe -> SYMBOL_NOT_IN_UNIVERSE
invalid date range -> INVALID_DATE_RANGE
```

## 5. Synthetic Fixture First

Use a non-empirical fixture before real data:

```text
fixture_kind = NON_EMPIRICAL_TEST_FIXTURE
symbols = AAA, BBB
session = REGULAR_ONLY
timezone = America/New_York
price_view = quote_guarded_1m
```

No real market claim can be made from this fixture.

## 6. Outputs

On resolved runs, write:

```text
data_manifest.json
universe_manifest.json
data_preflight_report.json
```

On failed runs, write only:

```text
data_preflight_report.json
```

## 7. Done Criteria

This increment is done when:

```text
contracts import cleanly
unit tests pass with synthetic fixtures
fail-closed cases return explicit failure codes
resolved synthetic run writes deterministic JSON manifests
MarketDataBar1m blocks access before available_at
AGENTS.md and CHANGELOG.md are updated
```

## 8. Out Of Scope

```text
real TSIS data fixture selection
Parquet scanning
LT1B membership loading
corporate-action lookup
market replay engine
orders/fills/accounting
fill realism for small caps
full 2005-2026 backtest
```

These come after the synthetic `RunPreflight` contract is executable.

## 9. Update 2026-07-28 - Hardening

Current exact state:

```text
RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED
SYNTHETIC_UNIT_TESTS = PASS, 21 tests
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

Hardening completed:

```text
DATASET_ROOT_NOT_FOUND test
INVALID_DATE_RANGE test
CANDIDATE_RUN_PURPOSE_NOT_PERMITTED test
SYMBOL_NOT_IN_UNIVERSE test
full MissingDataPolicy serialized in data_manifest.json
full CorporateActionPolicy serialized in data_manifest.json
outputs isolated under output_root/run_id
non-empty run output directory rejected with RUN_OUTPUT_NOT_EMPTY
```

Clarification:

```text
Missing-data detection is not implemented yet.
Corporate-action lookup is not implemented yet.
Rows, physical source files and hashes are not populated until the real-data inspector exists.
```
