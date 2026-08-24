# Massive SEC download agent handoff v0.2

Status: **PREPARED_NOT_AUTHORIZED**

Date: 2026-08-22  
Heavy output root: D:/sec_float_pit_MASSIVE  
Current action: obtain license/retention evidence and human authorization for
the bounded live probe; do not launch the full run.

## 1. Scope authority

Download authority:

C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/01_MASSIVE_SEC_OBJETIVO_01.md

00_MASSIVE_SEC.md is support only. Do not let it expand or replace the
objective.

Direct endpoints:

- EDGAR index;
- Form 3/3-A;
- Form 4/4-A;
- 8-K structured disclosures;
- disclosure taxonomy.

Conditional and currently unauthorized:

- 8-K text;
- Form 13F.

The config denylist also blocks Massive float and every unrelated ticker,
corporate-action, financial, news and market-data endpoint.

## 2. Exact target

Source:

C:/TSIS_Data/runtime/sec_pit_4824_descending_acquisition_v0_1/preflight_20260813T215254Z/full_universe_acquisition_order.parquet

SHA-256:

1ae6fe0391383fbf83d5e0b800d91db690a386d07a780481f354d9b3850718ee

Cardinality:

- 4,824 ordered cases;
- 4,824 unique tickers;
- 4,626 unique instrument IDs;
- 4,288 unique normalized issuer CIKs;
- zero missing CIK.

Requests deduplicate only by CIK. Every ticker/instrument membership remains in
the pre-manifest membership hash.

## 3. Current verified state

Implemented and locally certified:

- production runner and exact probe wrapper;
- endpoint allowlist and conditional gates;
- Bearer environment-only authentication;
- global adaptive rate limiter;
- raw SHA-256 CAS and deterministic normalized page shards;
- atomic COMMITTED receipts;
- request-ledger rebuild after crash;
- exclusive writer lock and stale same-host takeover on resume;
- heartbeat, PID manifest, log, monitor and offline auditor;
- strict resume hash compatibility.

Verification:

- py_compile PASS;
- Ruff PASS;
- 20/20 Massive-specific tests PASS;
- integrated second-page failure/resume PASS;
- exact plan-only run PASS;
- live Massive requests: zero;
- D-drive writes during preparation: zero.

Plan-only run:

massive_sec_probe_plan_20260822_v0_1

Plan manifest:

C:/TSIS_Data/runtime/massive_sec_acquisition_v0_1/massive_sec_probe_plan_20260822_v0_1/plan_only/final_manifest.json

Planned live probe:

- first 250 cases;
- 249 unique CIKs;
- 997 chains;
- 4 HTTP workers;
- one shared 2 requests/second engineering ceiling;
- 200 GiB hard free-space reserve;
- 870.98 GiB free observed during plan.

## 4. Frozen hashes

| Artifact | SHA-256 |
|---|---|
| config | 871bc7bc3855c62a8c919f434f7195584287baef7f8042747d69c24afa461e35 |
| target manifest | a9c2ce57204329da32ac2956fbeacc8dcd849d417f25754609fcb8cdcfd5e8c5 |
| target parquet | 1ae6fe0391383fbf83d5e0b800d91db690a386d07a780481f354d9b3850718ee |
| objective | c57811026767ae59d785cc95c0137535edefb9203fbc70874ae424681f304eb7 |
| executable component bundle | c515c0f79fc4161a10d09a3fcecae8f57628e88d796c8317b79089f2c073094a |
| pending authorization template | 10d058d86d80fb1efe5b66af24cb1046fef82ab80a1999406071f167cfcce7b7 |

If code or any bound artifact changes, the template is stale and must be
regenerated and human-authorized again.

## 5. Next permitted sequence

1. Read TSIS mandatory governance/hardware/local rules.
2. Read the objective, execution/recovery plan, milestone register, runtime
   contract, operator runbook and preparation/recovery readouts.
3. Obtain written subscription/license/retention confirmation.
4. Copy the pending template to a new versioned authorization JSON.
5. Fill authorized_by, authorized_at_utc, authorization_basis and all license
   evidence fields. Do not change hashes/counts/scope.
6. Set status=AUTHORIZED only for authorization_scope=PROBE_ONLY.
7. Set MASSIVE_API_KEY in the current process environment without printing it.
8. Launch the exact 250-case probe with a new run ID.
9. Monitor from a second terminal.
10. Run the offline audit and complete the probe/storage readout.
11. Stop. Do not run full universe until a separate
    FULL_AFTER_PROBE_PASS authorization exists.

## 6. Probe command template

The placeholder command below must not be run until steps 3–7 are complete:

~~~powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_massive_sec_probe.py" --config "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\massive_sec_acquisition_v0_1.json" --target-manifest "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\massive_sec_target_manifest_v0_1.json" --authorization "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\<ACTUAL_PROBE_AUTHORIZATION>.json" --run-id "<NEW_PROBE_RUN_ID>" --execute
~~~

Monitor:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\monitor_massive_sec_acquisition.ps1" -RunRoot "D:\sec_float_pit_MASSIVE\runs\<RUN_ID>" -Compact -Watch -IntervalSeconds 10
~~~

Offline audit:

~~~powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\audit_massive_sec_acquisition.py" --output-root "D:\sec_float_pit_MASSIVE" --run-id "<RUN_ID>" --rebuild-ledgers
~~~

## 7. Power loss and resume

The durable point is the COMMITTED page receipt, not terminal output or the
append ledger. On restart:

1. verify the old PID is not alive;
2. inspect pre-manifest, PID manifest, latest heartbeat, log and final manifest;
3. use the same run ID, config, target manifest and actual authorization;
4. replace --execute with --resume.

Committed pages are hash-validated and skipped. A page interrupted before its
receipt is fetched again. A receipt missing from the append ledger is recovered
when ledgers rebuild. A live/foreign writer lock blocks takeover.

This is page-level resume, not byte-level HTTP continuation. It does not protect
against physical loss of the only D disk; use UPS and a separate governed
physical backup before promotion.

## 8. Stop conditions

Stop on hash/scope drift, secret leakage, 401/403, identity/schema failure,
pagination escape/loop, sustained 429 pressure, low disk, artifact collision,
duplicate writer, unexplained target/endpoint coverage or absent terminal
evidence.

## 9. Promotion boundary

All downloaded material remains RAW_VENDOR_EVIDENCE_NOT_INSTITUTIONAL until
schema, coverage, temporal semantics, licensing, integrity and downstream
consumption gates pass. No conversation can override this boundary.
