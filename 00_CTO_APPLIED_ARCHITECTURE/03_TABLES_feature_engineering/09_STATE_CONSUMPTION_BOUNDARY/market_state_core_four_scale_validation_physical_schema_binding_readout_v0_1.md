# Market State Core-Four Scale-Validation Physical Schema Binding Readout v0.1

Gate: `market_state_core_four_scale_validation_physical_schema_binding_clarification_v0_1`
Date: `2026-07-30`
Status: `CLOSED_PASS_SCHEMA_PROVENANCE_AND_RUNTIME_CONTENT_AUTHORITY_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ`

```text
case_count = 15
failed_cases = 0
structural schema authority = PHYSICAL_SCHEMA_CONTRACT.json
structural schema columns = 40
schema mismatches observed by bounded execution = 0
profile provenance parquet SHA-256 = b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2
current bounded runtime content SHA-256 = bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68
hashes interchangeable = false
parquet opened by binding gate = false
physical rows read by binding gate = 0
```

`b1841f...` remains the provenance reference of the promoted profile and its
historical Scale C evidence. It is not authority for selecting the current
runtime artifact.

`bc033c...` is the current bounded runtime content authority for the BT-GATE-014
handoff. Its physical structure matched all 40 fields of the governed schema
during the recorded single-use execution.

No historical profile artifact was edited. This clarification makes
BT-GATE-014 contract and implementation work ready, but does not authorize the
backtester's physical execution.
