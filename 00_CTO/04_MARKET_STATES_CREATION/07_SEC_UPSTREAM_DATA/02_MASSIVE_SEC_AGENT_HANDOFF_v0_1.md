# Massive SEC Download Agent Handoff v0.1

Status: `PREPARATION_AUTHORITY`

Purpose: give a new agent the minimum complete context required to design,
implement, probe, monitor and audit the Massive SEC acquisition without
duplicating existing data or contaminating the SEC PIT pipeline.

This document does not authorize a long run. The executable allowlist and
denylist live in `01_MASSIVE_SEC_OBJETIVO_01.md` and remain authoritative.

## 1. Read first

Read the handoff package in this order:

1. `README.md` in the ZIP; its canonical repository source is
   `02_MASSIVE_SEC_AGENT_HANDOFF_v0_1.md`.
2. `01_OBJECTIVE/01_MASSIVE_SEC_OBJETIVO_01.md`.
3. `02_MAPS/SEC_UPSTREAM_README.md`.
4. `03_CONTRACTS/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`.
5. `03_CONTRACTS/SEC_PIT_LIFECYCLE_SOURCE_SELECTION_POLICY_v0_2.md`.
6. `03_CONTRACTS/MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_CONTRACT_v0_1.md`.
7. `04_OPERATIONS/LONG_RUNNING_OPERATIONS_CONTRACT.md`.
8. `05_GOVERNANCE/TSIS_HARDWARE_OPTIMIZATION_PROMPT.md` before sizing workers,
   memory, IO or concurrency.
9. The remaining package files only when their topic becomes relevant.

The broad research inventory `00_MASSIVE_SEC.md` is intentionally not bundled.
It describes many Massive products that are outside the authorized acquisition
and could be mistaken for an allowlist.

Historical documents may still cite the former folder name
`07_UPSTREAM_DATA`. Its active migrated replacement is
`07_SEC_UPSTREAM_DATA`; never recreate the old path to satisfy a stale link.

## 2. Scope boundary

The current Massive SEC agent may prepare and, after the corresponding human or
governed authorization, acquire:

```text
DIRECTLY IN SCOPE
- EDGAR Index
- Form 3 / 3-A
- Form 4 / 4-A
- 8-K Disclosures
- one versioned Disclosure Taxonomy

CONDITIONAL
- 8-K Text after the 250-case size/coverage gate
- 13F after the multi-quarter CUSIP/filter gate
```

It may not download non-SEC families in the same run. `Massive Float` is absent
from G:, but belongs to a future separate non-SEC run. All Tickers, Ticker
Overview, Ticker Events, Splits and Balance Sheets already exist and must not be
duplicated.

## 3. Where every artifact belongs

| Artifact | Canonical location | Agent permission |
|---|---|---|
| Architectural decisions and acquisition scope | `C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/MASSIVE_SEC/` | Read for context. Add a versioned Massive SEC contract only if the implementation introduces new semantics. |
| Main objective and handoff | `C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/` | Read as authority. Do not broaden the allowlist. |
| Executable Python and PowerShell | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/` | Create or modify only the required `massive_sec_*` implementation; existing SEC runners are reference code, not download targets. |
| Unit/integration tests | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/` | Create `test_massive_sec_*.py`; network must be mocked except explicit smoke tests. |
| Runtime configs and authorization | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/` | Create versioned `massive_sec_*.json`; never store credentials. |
| Operational contracts | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/sec_pit/` | Read existing SEC contracts; add a versioned Massive SEC contract when required. Do not rewrite unrelated contracts. |
| Canonical schemas | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/sec_pit/` | Add only endpoint schemas produced by this acquisition. |
| Validators | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/validators/sec_pit/` | Add only validators required by this acquisition. |
| Versioned readouts | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/` | Write only small probe/certification readouts; no raw payloads. |
| Lightweight orchestration runtime | `C:/TSIS_Data/runtime/massive_sec_acquisition_v0_1/<run_id>/` | Write control artifacts, launch logs and small manifests only. |
| Heavy Massive SEC data | `HUMAN_PROVIDED_OUTPUT_ROOT` | **Blocked until the human supplies the exact absolute path.** Freeze it in config/pre-manifest and write only after preflight and authorization. |
| Existing direct-SEC CAS | `D:/TSIS/fundamental_context/sec_pit_v0_1/objects/` | Read-only reconciliation if needed. Never write Massive responses here. |

The agent must not choose the heavy-data root. The human will provide it. That
exact path must then pass path-length, free-space, containment and collision
preflight before implementation treats it as active.

## 4. Expected heavy-data topology

```text
HUMAN_PROVIDED_OUTPUT_ROOT/
├── objects/                 content-addressed raw response bodies
├── datasets/
│   ├── edgar_index/
│   ├── form_3/
│   ├── form_4/
│   ├── disclosure_taxonomy/
│   ├── eight_k_disclosures/
│   ├── eight_k_text/        conditional
│   └── form_13f/            conditional
└── runs/<run_id>/
    ├── pre_manifest.json
    ├── pid_manifest.json
    ├── heartbeat_latest.json
    ├── heartbeat.jsonl
    ├── acquisition.log
    ├── request_ledger.parquet
    ├── error_ledger.parquet
    ├── endpoint_summary.json
    └── final_manifest.json
```

Raw responses are immutable. Normalized tables never replace raw responses.
The request ledger must map every normalized row or object to endpoint,
parameters, request ID, retrieval time, response hash and source accession when
available.

Until `HUMAN_PROVIDED_OUTPUT_ROOT` has been replaced by an exact human-supplied
absolute path in a versioned config and pre-manifest, network acquisition is
blocked. A script must reject the literal placeholder.

## 5. Minimum implementation surface

Prefer reusing existing SEC PIT telemetry, authorization and storage patterns.
Do not copy old runners and edit them blindly.

Expected new entrypoints/modules:

```text
scripts/sec_pit/massive_sec_client.py
scripts/sec_pit/massive_sec_models.py
scripts/sec_pit/massive_sec_storage.py
scripts/sec_pit/massive_sec_telemetry.py
scripts/sec_pit/run_massive_sec_probe.py
scripts/sec_pit/run_massive_sec_acquisition.py
scripts/sec_pit/audit_massive_sec_acquisition.py
scripts/sec_pit/monitor_massive_sec_acquisition.ps1

tests/test_massive_sec_client.py
tests/test_massive_sec_authorization.py
tests/test_massive_sec_storage.py
tests/test_massive_sec_resume.py
tests/test_massive_sec_scope_gate.py
```

Names may be refined before implementation, but their responsibilities must
remain separated. The monitor cannot be embedded only in the runner.

## 6. Secrets and provider access

```text
API key source       = environment variable MASSIVE_API_KEY
API key in configs   = prohibited
API key in logs      = prohibited
API key in manifests = prohibited
API key in ZIP       = prohibited
```

The license/retention terms must be recorded before the first production
request. If retained use after subscription expiry is not contractually clear,
the long acquisition is blocked.

## 7. Mandatory gates

Before any long run:

```text
implementation + unit tests
-> no-network scope/identity test
-> bounded endpoint probe using production runner
-> schema and sample-row audit
-> requests/bytes/storage projection
-> resume and duplicate-writer test
-> versioned certification readout
-> human or governed authorization
-> long run
```

For the 8-K Text and 13F families, the endpoint-specific gates in the objective
are additional and cannot be bypassed by a successful generic probe.

## 8. Required runtime behavior

The runner must fail closed on:

```text
- endpoint outside the allowlist
- target outside the frozen CIK/instrument set
- authorization/config/hash drift on resume
- duplicate live writer for the same run/output
- unexpected schema or pagination loop
- response without auditable request identity
- output path collision or overwrite request
- insufficient output free space
- missing or stale credential without exposing it
```

Retries must use bounded exponential backoff with jitter. HTTP status, retry
count and terminal reason must remain in the request ledger. A restart uses the
same run ID and `--resume`; it may not silently create a new scope.

## 9. Definition of done for preparation

Preparation is complete only when the agent leaves:

```text
- code and tests in their canonical Data Foundation paths;
- explicit endpoint/schema contracts;
- exact target and authorization config;
- short production-equivalent probe;
- live monitor command;
- storage/request/byte projection;
- certification readout;
- exact full-run command, not launched;
- exact resume and safe-stop instructions;
- Graphify refresh or pending queue entry;
- Git diff restricted to the intended files.
```

The human launches or explicitly authorizes the long run. This handoff alone is
not that authorization.

## 10. Package integrity and authority

The ZIP contains copies for portable review. Canonical files remain at the
source paths recorded in `PACKAGE_SOURCE_PATHS.csv`. The agent must edit the
canonical repository files, not the copies inside an extracted ZIP.

`PACKAGE_FILE_MANIFEST.csv` records size and SHA-256 for every packaged payload
file, including `PACKAGE_SOURCE_PATHS.csv`; it excludes only itself because a
file cannot contain its own stable hash. No market data, raw SEC/Massive
payload, runtime log or credential belongs in the package.
