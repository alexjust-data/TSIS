# TSIS Event Research Architecture

## Chapter 7 --- Event Candidates

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 7. Purpose

Before a market phenomenon can be investigated, TSIS must identify
reproducible **candidate Events**.

An Event Candidate is not yet an accepted research object.

It is a deterministic proposal that an observable market configuration
has occurred and deserves scientific investigation.

------------------------------------------------------------------------

# 7.1 Fundamental Principle

Detection precedes validation.

``` text
Observations
      ↓
Representations
      ↓
Detection Rules
      ↓
Event Candidates
      ↓
Validation
      ↓
Research Events
```

An Event Candidate is therefore an intermediate object between
representation and research.

------------------------------------------------------------------------

# 7.2 Definition

An Event Candidate is a timestamped, reproducible occurrence generated
by deterministic eligibility rules applied to observable market states.

It never implies:

-   profitability,
-   correctness,
-   causal explanation,
-   strategy validity.

It only states:

> "This observable configuration satisfies the declared candidate
> rules."

------------------------------------------------------------------------

# 7.3 Why Candidates Exist

Separating candidates from validated Events prevents confirmation bias.

Instead of assuming:

``` text
Breakout
```

TSIS first records:

``` text
Breakout Candidate
```

Scientific investigation determines whether that candidate corresponds
to a meaningful market phenomenon.

------------------------------------------------------------------------

# 7.4 Candidate Families

Typical candidate families include:

``` text
Scanner Qualification
Breakout Candidate
VWAP Reclaim Candidate
Opening Range Candidate
Trade Burst Candidate
Liquidity Vacuum Candidate
Quote Burst Candidate
News Reaction Candidate
```

Families are defined by observable conditions only.

------------------------------------------------------------------------

# 7.5 Candidate Detection

Every candidate detector shall define:

-   observable inputs,
-   eligibility rules,
-   thresholds,
-   timestamp policy,
-   builder version,
-   quality gates.

Detection must be deterministic.

------------------------------------------------------------------------

# 7.6 Candidate Metadata

Every candidate shall expose:

``` text
candidate_id
candidate_family
anchor_timestamp
instrument_id
population_id
eligibility_policy
state_version
representation_versions
builder_version
quality_state
```

------------------------------------------------------------------------

# 7.7 Candidate Promotion

Promotion path:

``` text
Candidate
      ↓
Research Event
      ↓
Event Population
      ↓
Evidence Collection
```

Promotion requires governance.

Candidate detection alone never creates scientific knowledge.

------------------------------------------------------------------------

# 7.8 Candidate Independence

Changing a detector creates a new candidate version.

Historical candidate populations remain immutable and reproducible.

------------------------------------------------------------------------

# 7.9 Near Misses

Near misses are first-class research objects.

Examples:

``` text
Failed Breakout Candidate
Failed VWAP Reclaim Candidate
Scanner Threshold Miss
```

Near misses are essential for:

-   control populations,
-   boundary estimation,
-   phenomenon validation.

------------------------------------------------------------------------

# 7.10 Constitutional Rule

Event Candidates are governed research proposals generated from
observable representations.

They are intentionally separated from validated Events, Phenomena and
Strategies in order to preserve scientific neutrality and
reproducibility.
