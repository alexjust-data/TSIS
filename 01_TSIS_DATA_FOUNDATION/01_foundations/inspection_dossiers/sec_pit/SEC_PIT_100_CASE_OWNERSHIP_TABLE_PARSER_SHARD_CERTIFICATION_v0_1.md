# SEC PIT 100-case ownership table parser shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_RERUN_AUTHORIZED`

Date: `2026-08-12`

Scope: bounded production-equivalent owner-exclusion probe, one eligible
instrument per each of the four governed shards. This certification authorizes
only a new versioned rerun of the 99 eligible cases. It does not authorize the
4,824-instrument scale.

## Blocker taxonomy finding

The v0.5 99-case result reported `AMENDMENT_FAMILY_UNRESOLVED` in 38 cases.
Inspection of the causal baseline ledger and 123 locally available baseline
documents showed that the label was overbroad:

- only ADMP, AYRO, ETAK, OMCC and VLCN had a detected partial amendment;
- the other 33 cases primarily had ownership tables whose header families were
  not recognized by the structured parser;
- across the affected candidate rows, the resolver recorded 47 `10-K`, 55
  `DEF 14A`, seven `20-F`, four `10-K/A`, eight partial `10-K/A`, and two
  `20-F/A` documents without extracted ownership rows.

The first correction therefore targets generic table extraction and causal date
binding, not ticker-specific amendment rules.

## Change under certification

`ownership_v2.py` now:

- recognizes `Share Ownership`, `Security Ownership`, `Shares Beneficially
  Owned`, and `Beneficial Owner / Number of Shares ... Owned` table families;
- binds `measurement_at` to the selected table's local ownership passage;
- rejects unrelated award, compensation and equity-plan `as of` dates;
- retains currently owned/issued shares as the owner-exclusion amount when a
  table separately reports shares acquirable within 60 days;
- takes `reported_percent` from the final percentage column rather than an
  intermediate numeric column;
- remains fail-closed when the table date, class, identity interval or overlap
  cannot be resolved.

No ticker name, CIK or accession is hard-coded in the implementation.

## Evidence roots

- Diagnostic parser probe, superseded after date binding:
  `C:/TSIS_Data/runtime/sec_pit_100_case_ownership_parser_shard_probe_v0_1`
- First integrated date probe, invalidated after readable-value audit found the
  percentage-column defect:
  `C:/TSIS_Data/runtime/sec_pit_100_case_ownership_parser_shard_probe_v0_2`
- Final certified four-shard probe:
  `C:/TSIS_Data/runtime/sec_pit_100_case_ownership_parser_shard_probe_v0_3`
- Immutable local acquisition ledger:
  `C:/TSIS_Data/runtime/sec_pit_100_case_scale_gate_v0_1/bounded_probe_authorized_v0_4_20260812T0530Z/combined_acquisition_ledger.jsonl`
- O/S dependency:
  `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_5`

All final probes used ownership component SHA-256
`3c9b2248dcba41a367f59be221908e577752ffffb22d40da8062fbd77745f66b`
and made zero network requests.

## Variable-by-variable shard audit

| Shard | Ticker | Baseline result | Daily float | Expected behavior |
|---:|---|---|---:|---|
| 0 | ADMP | no causal complete baseline | 0/5 | `BASELINE_DOCUMENT_PARTIAL` |
| 1 | ATYR | accession `0000950170-25-041992` | 5/5 | calculated from explicit 2025-03-01 ownership date |
| 2 | CYTO | content candidates present, identity not admitted | 0/5 | fail-closed on `INSTRUMENT_INTERVAL_CONFLICT` |
| 3 | ADTX | tables extracted, dates unresolved and identity conflict | 0/5 | fail-closed; compensation dates rejected |

ATYR's readable values are:

- O/S as known: `97,986,634`;
- supported currently issued management shares: `1,400,094`;
- shares acquirable within 60 days: not subtracted from current O/S;
- owner-exclusion float: `96,586,540`;
- float percent: `98.571138%`;
- filing-reported aggregate percentage: `3.92%`;
- five bounded sessions: all `CALCULATED`.

The four probes also passed stable schema/order, uniqueness at
`(instrument_id, session_date)`, causal availability, explicit NULL/blocker
semantics, identical component hashes, readable-value inspection and zero
network resolution.

## Test gate

- focused ownership/parser/baseline suite: `24 passed`;
- complete `test_sec_pit*.py` suite from the Data Foundation module root:
  `200 passed`.

An initial root-level invocation failed collection because three historical
tests import `scripts.sec_pit` relative to the Data Foundation module root. It
executed no tests and is not counted as evidence. The corrected module-root run
is the authoritative PASS.

## Gate decision

The ownership table/date implementation is authorized for a new, immutable
99-case rerun. The rerun must:

1. use the same config, selection plan, acquisition ledger and O/S v0.5 inputs;
2. use a new output root and run identity;
3. execute no network requests;
4. not resume or mix v0.1, v0.2, v0.3, v0.4 or v0.5 owner outputs;
5. publish before/after blocker and coverage deltas;
6. keep unresolved date, class, identity and overlap cases as NULL.

Scale to 4,824 instruments remains `NOT_GRANTED` pending the 99-case coverage
readout and subsequent blocker loops.
