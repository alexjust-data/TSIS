# Wake-up oracle calibration protocol v0.1

Status: `DRAFT_DEVELOPMENT_ONLY_NOT_FROZEN`

## Purpose

Calibrate the label oracle independently of Binding A and Binding B using the
2,400 frozen TA-3 development sessions and raw eligible RTH trade evidence.

## Discovery grid

```text
dormancy windows = 900, 1800, 3600 seconds
confirmation horizons = 30, 60, 120, 300 seconds
candidate selection = local maxima and within-session ranks
deduplication = binding-neutral candidate merge gap declared in config
```

The grid is a high-recall workload reducer. It is not the final oracle.

## Panel strata

The panel must balance cohort, RTH time bucket, price band, market-cap proxy
band, prior-activity state, source-quality state and candidate/control role.

Required roles:

```text
CANDIDATE_ACTIVITY_TRANSITION
CONTROL_DORMANT
CONTROL_ONE_CLUSTER
CONTROL_CONTEXT_NORMAL_ACTIVITY
CONTROL_QUALITY_OR_ARTIFACT
CONTROL_RANDOM_ELIGIBLE
```

## Calibration rule

WUL-D01…D08 are selected from a stable development region using blind-review
agreement, typed abstention, stratum robustness and parameter sensitivity.
No A/B feature, score or downstream outcome may be joined before the WUL freeze.

## Required audit

```text
two independent reviewers;
adjudication of disagreements;
all candidate and control sampling probabilities recorded;
all source and config hashes recorded;
no validation/final-test identity read;
independent terminal validation.
```

