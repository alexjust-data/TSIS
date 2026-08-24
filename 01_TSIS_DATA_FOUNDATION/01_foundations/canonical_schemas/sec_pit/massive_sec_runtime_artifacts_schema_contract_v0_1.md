# Massive SEC runtime artifacts schema contract v0.1

Status: **IMPLEMENTED**

## Pre-manifest required identity

run_id, status, created_at_utc, script/component hashes, command, host/PIDs,
git identity, execution mode, config/target/objective/authorization hashes,
target counts and membership hash, endpoint IDs/spec hash, chain count, worker
and rate settings, output/run roots, telemetry paths, free-space reserve,
resume/overwrite/success policies and exact resume command.

## COMMITTED receipt required identity

| Field | Rule |
|---|---|
| status | exactly COMMITTED |
| endpoint_id, work_id | required |
| target_cik | nullable |
| sanitized_url | no credential query |
| request_id | non-empty |
| retrieved_at_utc | UTC timestamp |
| raw_sha256, normalized_sha256 | 64-char content hashes |
| raw_object_path, normalized_path | existing files |
| raw_bytes, result_count | non-negative integers |
| next_url | nullable governed URL |
| http_status | 200 for committed v0.1 pages |
| attempts, retry_count, http_429_count | non-negative integers |
| elapsed_seconds | non-negative |
| observed_fields | sorted field-name array |

## Heartbeat

Required operational fields include run/status/stage/timestamp, wrapper and
active PIDs/aliveness, elapsed time, progress/current item, chain/page/row
counters, retry/429/rate counters, process/system CPU, RSS, memory/pagefile,
I/O rates and output free GiB.

## Final manifest

Must add terminal status, ended_at_utc, exit code/failure reason, counters,
ledger/error summaries, endpoint-summary path, resource peaks, resume
instructions and promotion_state.

Terminal status alone is not integrity certification. audit_manifest.json must
recompute artifact hashes and receipt/ledger invariants.
