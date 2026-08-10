# SEC PIT Fundamental Evidence Dataset Contract v0_1

## Identity

```text
dataset_family = sec_pit_fundamental_evidence
schema = sec_pit_source_observations_v0_1
status = experimental_one_ticker
canonical_promotion = not_authorized
```

## Sources

Primary authority is the original SEC EDGAR accession. SEC submissions and
Company Facts accelerate discovery and extraction but do not replace the
original filing when footnotes, class identity or amendments matter.

## Physical layers

```text
objects/sha256/...       compressed content-addressed evidence
runs/<run_id>/           pre-manifest, PID, heartbeat, logs and final manifest
filing_inventory         filing metadata and role candidates
source_observations      neutral extracted evidence
daily_os_state           experimental PIT O/S resolution
daily_float_state        experimental owner-exclusion estimate or blocked state
daily_tradability_state experimental eligibility estimate or blocked state
```

Default heavy root:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1
```

Resolved daily outputs are governed by sec_pit_resolved_daily_states_schema_contract_v0_1.md.

## Admission boundaries

The dataset does not authorize:

```text
exact historical daily float claims
scanner production consumption
full 4,821-instrument acquisition
canonical Fundamental Context promotion
```

Scale-out requires the one-ticker readout, optimized 50-ticker replay,
storage distribution, coverage gates and an explicit human decision.

