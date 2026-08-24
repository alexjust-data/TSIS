# Massive SEC acquisition operator runbook v0.1

Status: **READY_FOR_AUTHORIZATION; DO NOT EXECUTE YET**

## 1. Preconditions

Before the first API request:

1. obtain written confirmation that the active Massive plan permits the
   intended endpoints, local retention and TSIS research use;
2. copy the authorization template to a new versioned authorization file;
3. fill all human/license fields without changing hashes, endpoint IDs or
   counts;
4. set status=AUTHORIZED only for authorization_scope=PROBE_ONLY;
5. verify at least 200 GiB remains free on D:/sec_float_pit_MASSIVE;
6. ensure no writer lock is live;
7. set MASSIVE_API_KEY only in the current process environment.

Never place the key in JSON, Markdown, command history, URL, log or manifest.

## 2. Current plan-only evidence

Run ID: massive_sec_probe_plan_20260822_v0_1

Manifest:
C:/TSIS_Data/runtime/massive_sec_acquisition_v0_1/massive_sec_probe_plan_20260822_v0_1/plan_only/final_manifest.json

Result: PLAN_ONLY_NO_NETWORK_NO_D_DRIVE_WRITE.

## 3. Probe launch

Use a new actual authorization path and a new run ID. The command below is a
template and is intentionally not executable as written:

~~~powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_massive_sec_probe.py" --config "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\massive_sec_acquisition_v0_1.json" --target-manifest "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\massive_sec_target_manifest_v0_1.json" --authorization "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\<ACTUAL_PROBE_AUTHORIZATION>.json" --run-id "<NEW_PROBE_RUN_ID>" --execute
~~~

Expected probe scope: first 250 ordered cases, 249 unique CIKs, 997 chains,
4 HTTP workers and a shared 2 requests/second ceiling.

## 4. Monitor

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\monitor_massive_sec_acquisition.ps1" -RunRoot "D:\sec_float_pit_MASSIVE\runs\<RUN_ID>" -Compact -Watch -IntervalSeconds 10
~~~

Monitor from a separate terminal. Success requires a terminal manifest, not
merely an absent process.

## 5. Safe stop

Press Ctrl+C once in the runner terminal. The runner signals all workers,
allows any already-returned page to finish its atomic commit, writes terminal
evidence and releases its writer lock. Do not kill the process unless it is
unresponsive and the incident is documented.

## 6. Resume after power loss or interruption

First inspect:

- pre_manifest.json;
- pid_manifest.json;
- heartbeat_latest.json;
- final_manifest.json, if present;
- tail of acquisition.log;
- current PID state.

Then reuse exactly the same run ID and actual authorization:

~~~powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_massive_sec_probe.py" --config "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\massive_sec_acquisition_v0_1.json" --target-manifest "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\massive_sec_target_manifest_v0_1.json" --authorization "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\<ACTUAL_PROBE_AUTHORIZATION>.json" --run-id "<SAME_RUN_ID>" --resume
~~~

Resume does not continue partial HTTP bytes. It validates committed receipts,
skips complete pages and repeats only the uncommitted in-flight page.

## 7. Offline integrity audit

~~~powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\audit_massive_sec_acquisition.py" --output-root "D:\sec_float_pit_MASSIVE" --run-id "<RUN_ID>" --rebuild-ledgers
~~~

This command performs no network request. It validates CAS and normalized
hashes, request IDs, duplicate work IDs and temporary files, then regenerates
the request ledgers from committed receipts.

## 8. After the probe

Do not start the full run. First persist endpoint-level schema/value samples,
coverage, 429/retry/latency behavior, total raw/normalized bytes, projected
full storage and a worker decision. Only a governed PASS may produce a separate
FULL_AFTER_PROBE_PASS authorization.

8-K text and 13F remain prohibited even if the direct-lane probe passes.
