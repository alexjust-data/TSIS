# Event State On-Demand Bounded Candidate Dataset Review Authorization v0.1

Status: `AUTHORIZED_AND_CONSUMED_BY_REVIEW`
Date: `2026-07-27`

```text
review_id = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T000000Z
review_run_id = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T202013Z
reviewed_run = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z
reviewed_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33
execution_authorized = false
market_state_read_authorized = false
event_state_materialization_authorized = false
registry_mutation_authorized = false
official_dataset_promotion_authorized = false
production_authorized = false
downstream_authorized = false
```

This gate authorizes review only. It does not authorize rebuilding Event State,
reading Market State again, mutating the candidate registry entry, promoting an
official dataset, production, or downstream consumption.
