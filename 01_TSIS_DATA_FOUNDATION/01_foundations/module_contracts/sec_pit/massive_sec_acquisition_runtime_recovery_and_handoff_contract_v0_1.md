# Massive SEC acquisition runtime, recovery and handoff contract v0.1

Status: **PROVISIONAL_CONTROL_PLANE_CERTIFIED; LIVE_VENDOR_PROBE_PENDING**

## Contract

A Massive SEC acquisition is resumable only when all of these identities remain
unchanged:

- run ID;
- config and target-manifest SHA-256;
- frozen target data SHA-256;
- objective SHA-256;
- component-bundle SHA-256;
- endpoint-spec hash;
- execution mode;
- output root;
- target-group membership hash;
- authorization-file SHA-256.

Resume must fail closed on drift.

## Durable topology

~~~text
D:/sec_float_pit_MASSIVE/
  locks/massive_sec_acquisition.lock
  objects/sha256/<aa>/<bb>/<sha>.json.gz
  datasets/<endpoint>/pages/<prefix>/<work_id>.jsonl.gz
  runs/<run_id>/
    pre_manifest.json
    pid_manifest.json
    heartbeat_latest.json
    heartbeat.jsonl
    acquisition.log
    receipts/<endpoint>/<work_id>.json
    request_ledger.jsonl
    request_ledger.parquet
    error_ledger.jsonl
    error_ledger.parquet
    endpoint_summary.json
    final_manifest.json
    audit_manifest.json
~~~

## Commit authority

receipts/<endpoint>/<work_id>.json with status=COMMITTED is authoritative only
if raw and normalized files exist and both recomputed hashes match. Ledger rows
alone cannot mark completion.

The canonical work ID is SHA-256 over endpoint ID plus sanitized page URL.
Credentials are removed before identity, logging or persistence.

## Recovery

1. Confirm there is no live writer.
2. Read pre-manifest, PID, latest heartbeat, final manifest and log.
3. Run the offline auditor when artifact integrity is uncertain.
4. Reuse exactly the run ID, config, target manifest and authorization.
5. Start with --resume; do not create a replacement run for the same
   interrupted acquisition.
6. The runner validates every encountered receipt and skips only valid commits.
7. Rebuild ledgers from receipts during finalization or with the offline auditor.

Same-host stale locks may be evidence-preservingly archived by resume. Foreign
locks require human investigation.

## Handoff minimum

A new agent must be able to continue from repository and run artifacts alone.
The handoff must include current milestone, exact command, run ID, hashes,
expected status, last heartbeat age, live PID check, committed/resumed/error
counts, stop reason, next gate and prohibited actions.

## Promotion boundary

Raw/normalized vendor artifacts remain
RAW_VENDOR_EVIDENCE_NOT_INSTITUTIONAL. Completeness, schema, temporal semantics
and licensing must pass separate certification before any downstream
consumption.
