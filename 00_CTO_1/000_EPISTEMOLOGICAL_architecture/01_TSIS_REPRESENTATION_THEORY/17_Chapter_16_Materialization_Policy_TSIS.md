# TSIS Market Representation Architecture

## Chapter 16 --- Materialization Policy

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 16. Materialization Policy

## 16.1 Purpose

Not every feature should be materialized in the same way.

Some features are inexpensive and stable enough to exist across the full
historical archive.

Others are computationally expensive and should only be generated for
explicitly governed research populations.

Materialization policy separates **scientific definition** from
**physical persistence**.

------------------------------------------------------------------------

## 16.2 Fundamental principle

Semantic existence and physical materialization are different concepts.

A feature may exist in the Feature Registry without being permanently
materialized.

Likewise, a feature may be materialized for one research population but
not for another.

------------------------------------------------------------------------

## 16.3 Canonical materialization modes

``` text
FULL_SOURCE_HISTORY

FULL_CONTEXT_HISTORY

FULL_RESEARCH_POPULATION

SELECTIVE_EVENT_WINDOWS

ON_DEMAND_REPLAY

CACHE_ONLY

EXPERIMENTAL
```

------------------------------------------------------------------------

## 16.4 FULL_SOURCE_HISTORY

Applies to compact canonical datasets whose complete historical
persistence is justified.

Typical examples:

``` text
Instrument Master
Market Calendar
Master Daily
Canonical 1m Bars
Corporate Actions
```

Characteristics:

-   complete historical coverage
-   reproducible
-   low computational cost
-   stable semantics

------------------------------------------------------------------------

## 16.5 FULL_CONTEXT_HISTORY

Used for compact contextual information.

Examples:

``` text
Daily Context
Regime Context
Quality Summaries
Availability Summaries
```

These tables are intended to provide broad historical context rather
than exhaustive event-level detail.

------------------------------------------------------------------------

## 16.6 FULL_RESEARCH_POPULATION

The preferred mode for scientific research.

A population must be explicitly declared.

Examples:

``` text
All Halt Events

All Scanner Candidates

All Breakout Candidate Events

Matched Control Windows
```

Every eligible member of the declared population shall be materialized.

------------------------------------------------------------------------

## 16.7 SELECTIVE_EVENT_WINDOWS

Designed for computationally expensive event-level features.

Examples:

``` text
Microprice Dynamics

OFI Families

Trade-Quote Alignment

Burstiness

Apparent Replenishment
```

Materialization occurs only around governed windows.

------------------------------------------------------------------------

## 16.8 ON_DEMAND_REPLAY

Used during exploratory research.

Properties:

-   temporary
-   reproducible
-   deterministic
-   not automatically promoted

Outputs may later become FULL_RESEARCH_POPULATION after validation.

------------------------------------------------------------------------

## 16.9 CACHE_ONLY

Features computed lazily may be cached.

The cache must remain completely reproducible.

Cache keys should include:

``` text
instrument_id
anchor_timestamp
window_policy
feature_set_version
builder_version
alignment_policy
eligibility_policy
```

Cache invalidation requires explicit version changes.

------------------------------------------------------------------------

## 16.10 EXPERIMENTAL

Experimental materializations are isolated from official datasets.

Characteristics:

-   research only
-   no production dependency
-   explicit experimental namespace
-   no canonical authority

------------------------------------------------------------------------

## 16.11 Choosing a policy

Selection depends on:

-   computational cost,
-   storage requirements,
-   scientific importance,
-   reproducibility,
-   expected reuse,
-   research population.

Performance alone shall never determine policy.

------------------------------------------------------------------------

## 16.12 Coverage declarations

Every materialized dataset shall declare:

``` text
coverage_mode
population_id
coverage_policy_id
feature_set_version
lookback_policy_id
source_start
source_end
full_source_history_claim
full_population_claim
full_universe_claim
```

Coverage claims must be testable.

------------------------------------------------------------------------

## 16.13 Promotion

Materialization policies may evolve only through explicit promotion.

Typical path:

``` text
Experimental

↓

On-Demand Replay

↓

Full Research Population

↓

Canonical Production
```

Promotion never changes semantic definitions.

Only operational status changes.

------------------------------------------------------------------------

## 16.14 Constitutional rule

Materialization is an implementation concern.

Semantics belong to the Feature Registry.

No implementation may alter the scientific meaning of a feature by
changing its materialization policy.
