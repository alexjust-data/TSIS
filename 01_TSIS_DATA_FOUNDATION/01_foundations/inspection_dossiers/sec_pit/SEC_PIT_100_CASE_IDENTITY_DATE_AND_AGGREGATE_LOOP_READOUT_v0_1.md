# SEC PIT 100-case identity, date and aggregate loop readout v0.1

Status: `V0_9_SYSTEM_PASS_AGGREGATE_RERUN_AUTHORIZED`

Date: `2026-08-12`

## Authoritative v0.9 result

Evidence root: `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_9`

The immutable no-network batch completed 99/99 O/S cases and 99/99 owner
cases with zero execution failures. The authoritative audit artifacts are:

- `owner_result_audit_v0_1.json`: `PASS`;
- `certification_v0_2/certification.json`:
  `SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING`;
- `scale_gate_summary_v0_1/summary.json`:
  `COMPLETE_SYSTEM_AUDIT_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING`.

An initial certification invocation pointed at `runs` rather than the parent
root and attempted to resolve `runs/runs`. It evaluated no cases. The valid
certification is explicitly v0.2.

Coverage changed from v0.7 to v0.9 as follows:

| Metric | v0.7 | v0.9 |
|---|---:|---:|
| O/S full cases | 56/99 | 56/99 |
| Float full cases | 13/99 | 17/99 |
| Float non-NULL sessions | 65/495 | 85/495 |
| Baseline document partial cases | 27 | 9 |
| Instrument interval conflict cases | 26 | 24 |

The four newly calculated cases are ASPN, ATMC, ATMV and ENFY. No previously
calculated v0.7 case regressed. Readable review confirmed explicit baseline
accessions, measurement dates earlier than availability, causal O/S anchors,
aggregate suppression of atomic management rows, no intervening split blocker
and five calculated sessions per case.

Scale to 4,824 remains `NOT_GRANTED` because 17/99 float coverage is still
insufficient.

## Next blocker family: aggregate management language

The remaining baseline audit found valid management aggregates expressed as:

- `Executive Officers and Directors as Group`;
- `Directors and officers as a group`;
- `All Directors, Director Nominees and NEOs as a Group`.

The resolver now classifies an aggregate semantically only when the holder cell
contains a director role, an officer/NEO role and `as [a] group`. A section
header without `as group` is not an aggregate. No ticker, CIK or accession is
hard-coded.

## Production-equivalent probe

Evidence root:
`C:/TSIS_Data/runtime/sec_pit_100_case_aggregate_language_shard_probe_v0_1`

All probes used ownership parser SHA-256
`99a6687f0501ea7f2a8fb9edb8ccec4d28bd707489d3bb731116ad7b924c84a9`,
the same runner hash and zero network requests.

| Shard | Ticker | Result |
|---:|---|---|
| 0 | SMIT | baseline selected; NULL on holder overlap |
| 1 | PTE | baseline selected; 5/5 calculated |
| 2 | CYCC | baseline selected; NULL on post-baseline event |
| 3 | ADTX | prior identity/partial blockers preserved |

VLCN was added as a bounded language control: its `Director Nominees and NEOs`
aggregate selected a baseline and correctly remained NULL on holder overlap.

PTE readable values are O/S `7,376,231`, excluded shares `259,197`, float
`7,117,034` and float percent `96.48605093848064%`.

## Test and gate decision

- focused parser/baseline/float suite: `38 passed`;
- complete SEC PIT suite: `210 passed`.

A fresh immutable 99-case no-network rerun is authorized. It must not resume or
mix v0.8/v0.9 outputs, must persist one component-hash set across every case
and must preserve all downstream identity, class, overlap, split, O/S and
post-baseline blockers as explicit NULL states.

## Authoritative v0.10 result

Evidence root: `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_10`

The authorized aggregate-language rerun completed 99/99 O/S and 99/99 owner
cases, with zero execution failures and zero network requests. The result audit,
certification and scale-gate summary all passed their system gates.

| Metric | v0.9 | v0.10 |
|---|---:|---:|
| O/S full cases | 56/99 | 56/99 |
| Float full cases | 17/99 | 19/99 |
| Float non-NULL sessions | 85/495 | 95/495 |
| Amendment-family blocker cases | 20 | 20 |
| Instrument-interval conflict cases | 24 | 24 |

MULN and PTE became newly calculated and no v0.9 calculated case regressed.
The next loop is governed by
`SEC_PIT_OWNERSHIP_HTML_WHITESPACE_SHARD_CERTIFICATION_v0_1.md`, which proves
that a material part of the remaining amendment-family bucket is SEC HTML table
normalization rather than missing acquisition.

## Authoritative v0.11 result

Evidence root: `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_11`

The immutable no-network batch completed 99/99 O/S and 99/99 owner cases with
zero execution failures. The owner result audit is `PASS`, the four-shard
certification is `SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING`, and the scale
summary is `COMPLETE_SYSTEM_AUDIT_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING`.

| Metric | v0.10 | v0.11 |
|---|---:|---:|
| O/S full cases | 56/99 | 56/99 |
| Float full cases | 19/99 | 20/99 |
| Float non-NULL sessions | 95/495 | 100/495 |
| Amendment-family blocker cases | 20 | 6 |
| Instrument-interval conflict cases | 24 | 25 |

AIEV is the sole newly calculated case; no v0.10 calculated case regressed.
Its five sessions use O/S `70,724,664`, aggregate management `114,200`, float
`70,610,464` and `99.838529%`.

The reduction from 20 to six amendment-family blockers is more important than
the single direct coverage gain: fourteen cases now pass table extraction and
expose their actual downstream blocker. The increase in split, class, identity,
overlap and post-baseline blocker counts is therefore a taxonomy refinement,
not evidence that previously calculated cases degraded.

The six residual amendment-family cases are BASI, BPT, KXIN, NAT, OSG and SAIH.
They require a separate bounded layout/family analysis. Scale to 4,824 remains
`NOT_GRANTED`; the current owner-float full-case coverage is `20/99 = 20.20%`.
