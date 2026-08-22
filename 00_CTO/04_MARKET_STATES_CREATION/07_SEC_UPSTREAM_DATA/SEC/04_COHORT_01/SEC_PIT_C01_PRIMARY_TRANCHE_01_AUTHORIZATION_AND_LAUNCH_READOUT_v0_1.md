# SEC PIT C01 Primary Tranche 01 Authorization and Launch Readout `v0_1`

Date: `2026-08-14`

Status: `RUNNING_NOT_YET_AUDITED`

## Decision

The human authorized the agent to launch only the first part of C01 primary
acquisition after correcting the metadata gate compatibility and operational
monitor. This is a bounded acquisition run, not an authorization for all 824
C01 rows, the full 4,824-row universe, O/S resolution, float resolution or
institutional promotion.

## Frozen authorization

```text
authorization config
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/sec_pit_primary_download_authorization_c01_t01_0250_v0_1_20260814.json
SHA-256 dc991ce03ac0cc05b57c28f8180282c904c8fed7ab2ef8741dc93039dd221560

probe manifest SHA-256
84c9ef29f31b8cbb2ceb04ee04806b8e56da532da30260f055c4fad1961899e9

selection plan SHA-256
c7b2574c5fe3b750ea595e85804be5a11d2dca13224f3b3e7801e3deafd35038

gate matrix SHA-256
05e7f05585e3c45cf8eb058eb136a9ca0c0980c4e1d10526bb5dce26dee1c401
```

The authorization is the exact first `250` rows in governed eligible order.
It contains `127,946` selected documents with a filing-size upper bound of
`132,250,074,097` bytes. The other `499` eligible C01 rows are not authorized;
`70` lifecycle/identity halts and `5` security-class halts remain excluded.

## Launch

```text
started_at_utc       2026-08-14T07:43:20Z
run_id               sec_pit_c01_primary_t01_0250_v0_1_20260814
wrapper_pid           31868 at launch; runtime-only identity
run_root              D:/TSIS/fundamental_context/sec_pit_v0_1/runs/sec_pit_c01_primary_t01_0250_v0_1_20260814
object_root           D:/TSIS/fundamental_context/sec_pit_v0_1/objects
requests_per_second  5
minimum_free_space   200 GiB
concurrency           1
```

The runner writes a premanifest before acquisition, a PID manifest, current
and historical heartbeats, append-only acquisition/performance JSONL, a live
log and a terminal manifest. Content-addressed objects are never overwritten.
Low disk closes as `STOPPED_LOW_DISK` and preserves exact resume state.

Initial verified heartbeat at `2026-08-14T07:43:47Z`:

```text
status=RUNNING stage=PRIMARY_ACQUISITION progress=36/127946
ticker=AAME failed=0 retries=0 http_429=0
output_free_gib=874.286 process_tree_rss_gib=0.699
```

## Operator monitor

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\monitor_authorized_primary_acquisition_v0_2.ps1" -RunRoot "D:\TSIS\fundamental_context\sec_pit_v0_1\runs\sec_pit_c01_primary_t01_0250_v0_1_20260814" -AuthorizationPath "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\sec_pit_primary_download_authorization_c01_t01_0250_v0_1_20260814.json" -IntervalSeconds 10 -Compact -Watch
```

This form reports document progress plus `ticker_ordinal`, exact
`tickers_completed` and countdown `tickers_remaining` against the 250-ticker
authorization. The broader 749-row technically eligible set is not used as the
denominator.

The operator monitors the long run and reports the terminal state. The agent
does not poll it independently after initial launch verification.

## Resume boundary

After a power loss or controlled interruption, rerun the exact launch command
with `--resume` and the same run ID, authorization, probe root, output root,
rate and disk threshold. Resume fails closed on hash drift or a live duplicate
writer and skips URLs already recorded as `FETCHED` with SHA-256 evidence.

## Required terminal audit

Before authorizing any later tranche, verify:

- terminal status and final manifest;
- fetched, skipped, failed, retry and HTTP 429 counts;
- object byte counts and SHA-256 integrity;
- actual compressed bytes and document-size distributions;
- fallback/404 behavior and unresolved accession cases;
- disk/performance summary and clean resume semantics;
- exact scope membership with no admission from the 574 blocked/unapproved C01
  rows.

No downstream O/S or owner-exclusion run is authorized by this launch alone.
