# SEC PIT 100-case O/S multi-evidence shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_RERUN_AUTHORIZED`

Date: `2026-08-12`

Scope: bounded production-equivalent O/S probe, one eligible instrument per each
of the four governed shards. This certification does not authorize the 4,824
instrument scale.

## Change under certification

The primary-document text extractor now supports four additional SEC cover-page
sentence families observed in the stratified sample and rejects `issuable` or
`reserved` contexts as O/S anchors. A primary observation may also be promoted
when the official SEC Company Facts API agrees exactly on accession,
measurement date and value, but only for a single or unnumbered common-equity
class with a passing security-class gate. Multiclass cases and value conflicts
remain fail-closed.

Policies:

- `class_os_exact_dual_extraction_agreement_v0_3`
- `sec_companyfacts_primary_os_reconciliation_v0_1`
- `class_os_primary_companyfacts_exact_agreement_v0_4`
- `class_os_multi_evidence_reconciliation_v0_4`

## Evidence roots

- Primary-only parser probe:
  `C:/TSIS_Data/runtime/sec_pit_100_case_os_parser_shard_probe_v0_1`
- Official Company Facts acquisition/reconciliation:
  `C:/TSIS_Data/runtime/sec_pit_companyfacts_os_parser_shard_probe_v0_1/runs/sec_pit_companyfacts_os_parser_shard_probe_v0_1_20260812T1030Z`
- Final integrated no-network probe:
  `C:/TSIS_Data/runtime/sec_pit_100_case_os_parser_shard_probe_v0_3`
- Eligible 99-case official Company Facts acquisition:
  `C:/TSIS_Data/runtime/sec_pit_100_case_companyfacts_v0_2/runs/sec_pit_100_case_companyfacts_v0_2_20260812T1150Z`

The bounded Company Facts acquisition completed four requests, produced 437 fact
rows, persisted content hashes and telemetry, and reported one explicit value
conflict. The subsequent 99-case acquisition completed 99/99 case summaries,
reused 31 byte-and-SHA-verified responses, made 68 new requests, persisted 10,158
fact observations, and classified BPT's HTTP 404 as the explicit
`COMPANYFACTS_NOT_AVAILABLE` state.

## Variable-by-variable shard audit

| Shard | Ticker | Result | Daily O/S | Value used | Evidence state |
|---:|---|---|---:|---:|---|
| 0 | ADMP | PASS | 5/5 | 9,359,133 | exact primary text + SEC Company Facts |
| 1 | ASNA | PASS | 5/5 | 9,986,423 | exact primary text + SEC Company Facts |
| 2 | ANTH | EXPECTED NULL | 0/5 | NULL | `COMPANYFACTS_OS_VALUE_CONFLICT` |
| 3 | ADTX | PASS | 5/5 | 559,444 | primary text + inline XBRL; Company Facts agrees |

All four cases passed:

- stable O/S output schema and column order;
- grain uniqueness on `(instrument_id, session_date)`;
- causal anchor availability (`eligible_from_session <= session_date`);
- explicit NULL and blocker semantics;
- identical component hashes across the integrated probes;
- readable value inspection;
- zero network requests during integrated resolution.

ANTH is a required fail-closed control. Its filing text and Company Facts disagree
for the same accession and measurement date; no anchor is promoted.

## Gate decision

The corrected O/S implementation is authorized for a new versioned rerun of the
99 eligible cases. The rerun must use the immutable raw Company Facts observation
artifact, record its SHA-256 in every O/S run identity, and recompute the
reconciliation locally against primary observations produced by the same parser
version. It must not resume or mix outputs from v0.1, v0.2 or v0.3.

Scale to all 4,824 instruments remains `NOT_GRANTED` pending the resulting
coverage audit and the remaining ownership-baseline blockers.
