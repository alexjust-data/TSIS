# Trading Activity Stage-8 C++ engine integration and four-shard recertification readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `artifact_role` | `ENGINE_INTEGRATION_AND_BOUNDED_RECERTIFICATION_READOUT` |
| `artifact_status` | `EXECUTED_PASS_WITH_RESTRICTIONS` |
| `execution_date` | `2026-08-11` |
| `scope` | `TRADING_ACTIVITY_BINDING_A_V0_2_STAGE8_ONLY` |
| `semantic_oracle` | `trading_activity_stage8_python_reference_v0_2` |
| `candidate_engine` | `trading_activity_stage8_cpp_native_candidate_v0_1` |
| `broad_materialization_authorized` | `false` |

## 1. Decision

The C++ Stage-8 kernel is integrated behind an explicit engine contract and
passed one bounded production-equivalent probe in each of the four TA-3 shards.
This closes the engine-integration and early shard-audit gate. It does not
authorize resume, a 240-block materialization, Binding B, OOS or canonical
promotion.

Python remains the complete semantic oracle. C++ changes execution only. No
variable, formula, column, column order, dtype, NULL mask, state, PIT rule,
identity metadata, lineage or output grain was changed.

## 2. Explicit engine fingerprint

```text
engine contract = trading_activity_stage8_engine_binding_v0_1
engine name     = cpp
engine id       = trading_activity_stage8_cpp_native_candidate_v0_1
fingerprint     = 7d24178a5b475c36401b4321af95630550185e5ea227dfe3419f08398bb54a0a
```

The composite fingerprint covers:

| Role | SHA-256 |
|---|---|
| engine registry | `f971ea24530f430577c5c5989f0798b3b6d659ff884ea00e3a7871abb0f8434e` |
| Stage-8 runner | `70ec15f717d73f406ced17f696cfb56d6d00fc3b170cdf1efafd842ec8553bc0` |
| Python/C++ adapter | `289f9fe9f27cafc27231df645575cb17e59d7432d1e4d3aa1db9bac78f066d1e` |
| C++ source | `0d62f8ae9c63d59e52b0360b0fec514c8f5afdc19fe7e98f1622a80f772d7848` |
| native `.pyd` binary | `5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4` |

The runner rejects a mismatching expected fingerprint and rejects resume when
the persisted engine fingerprint differs. Engine identity is written to the
pre-manifest, block lineage, run summary, pointer and final manifest. The
Parquet feature schema is unchanged.

## 3. Implementation surface

```text
01_TSIS_DATA_FOUNDATION/scripts/trading_activity_binding_a_baseline_engine.py
01_TSIS_DATA_FOUNDATION/scripts/trading_activity_binding_a_baseline_cpp.py
01_TSIS_DATA_FOUNDATION/scripts/run_trading_activity_binding_a_multisession_pilot.py
01_TSIS_DATA_FOUNDATION/scripts/run_trading_activity_ta3_binding_a.py
01_TSIS_DATA_FOUNDATION/scripts/validate_trading_activity_binding_a_shard_probes.py
01_TSIS_DATA_FOUNDATION/scripts/run_trading_activity_stage8_cpp_four_shard_probe.py
```

The Python path remains available explicitly as `--stage8-engine python`; the
new candidate path is selected explicitly with `--stage8-engine cpp` plus the
expected fingerprint.

## 4. Cycle 1: preserved operational failure

The first four-shard launch used the long historical probe root and failed in
Stage 6 before Stage 8 because a Windows atomic `.sha256` sidecar path exceeded
the usable path length. Shards 0 and 1 failed; shards 2 and 3 were never
launched. This was an infrastructure/path failure, not a semantic or C++
equivalence failure.

```text
plan = TRADING_ACTIVITY_STAGE8_CPP_FOUR_SHARD_PROBE_PLAN_v0_1.json
runtime = D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/probes/stage8_cpp_four_shard_v0_1/operations
status = FAILED_PRESERVED_NO_RESUME
```

No output was deleted or reused. In accordance with the preregistered resume
policy, cycle 2 used a new plan, new run IDs and new compact roots.

## 5. Cycle 2: four-shard PASS

```text
plan = TRADING_ACTIVITY_STAGE8_CPP_FOUR_SHARD_PROBE_PLAN_v0_2.json
plan SHA-256 = b28d7d4230dd005dfe32fb3eed0b4c90a2c98083525ecab596f844bd2c403262
runtime root = D:/TSIS/IO/ta8c2/r
output root = D:/TSIS/IO/ta8c2/o
status = PASS
elapsed = 231.710 seconds
completed shards = 4/4
failed shards = 0
max concurrent workers = 2
```

| Shard | Block | Current state | Multiscale | PIT baseline |
|---:|---|---:|---:|---:|
| 0 | `3244b2db5e3f87198bd321417948efea` | 39,000 | 15,600 | 9,000 |
| 1 | `a13d427087381465634b7cde9671308f` | 39,300 | 15,720 | 9,900 |
| 2 | `1b24fb5e32fb9544ddd60f4644618eb2` | 39,000 | 15,600 | 9,000 |
| 3 | `7379ceaa9bda6ff94fa23dfdcb828b5e` | 39,000 | 15,600 | 9,000 |
| **Total** | **4 blocks** | **156,300** | **62,520** | **36,900** |

## 6. Certification and audit

The strict certification returned:

```text
status = PASS
engine fingerprints = exactly 1, equal to the preregistered C++ fingerprint
current_state schema variants = 1
multiscale_contrast schema variants = 1
pit_baseline_and_surprise schema variants = 1
exact expected row counts = PASS for all shards
formula, missingness and PIT checks = PASS
```

The variable-conformance audit covered four finalized block manifests, found
no missing output roots, no missing expected feature columns and no missing
required metadata. `future_window_used=false` in the single lineage variant.

Evidence hashes:

```text
four_shard_certification.json SHA-256 = e7407f91f2b3070252a91d2cae093c7f7c95f788ba6c38b6ded3223cb31c7c5f
four_shard_conformance.json   SHA-256 = eebcdb984ef82e98d0c8bfff862e7b5ebf6cabe24948538d30cd3187139cf391
```

## 7. Remaining gate

The technical early-audit sequence through four-shard recertification is
complete. The next action is a separate governed human decision on whether to
preregister and launch a new versioned 240-block C++ run from zero. A future
run must not reuse `ba2r2`, mix Python/C++ partitions, or treat these bounded
outputs as institutional data.

SEC PIT remains preserved and parked until the Trading Activity materialization
decision/workstream closes.
