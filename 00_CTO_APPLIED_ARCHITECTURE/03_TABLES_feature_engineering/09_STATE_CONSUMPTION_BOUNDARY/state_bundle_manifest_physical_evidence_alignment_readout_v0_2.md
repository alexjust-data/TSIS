# StateBundle Manifest Physical Evidence Alignment Readout v0.2

Gate: `state_bundle_manifest_physical_evidence_alignment_v0_2`
Date: `2026-07-30`
Status: `CLOSED_PASS_PHYSICAL_EVIDENCE_ALIGNED_READY_FOR_BOUNDED_READ_AUTHORIZATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ`

## Result

```text
case_count = 22
blocking_findings = 0
restricted_findings = 2
physical_read_authorization_ready = true
authorization_to_read_issued = false
```

The accepted provider v0.1.2 control-plane artifacts now align with one exact
Market State scale-validation candidate, its 120 requested contexts, 104
represented row identities, 16 unavailable contexts, replay-availability
sidecar and governed metadata hash chain.

This closure proves metadata alignment only. It does not open the candidate
parquet, deliver rows or authorize `StateReplayFeed` or backtest consumption.

## Preserved Restrictions

```text
candidate dataset only
partial coverage remains visible
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

## Next Gate

```text
bounded_state_bundle_read_and_replay_authorization_v0_1
```
