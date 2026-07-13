# TSIS Market Representation Architecture

## Chapter 19 --- Architectural Anti-Patterns

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 19. Architectural Anti-Patterns

## 19.1 Purpose

This chapter documents architectural mistakes that shall not become part
of TSIS.

Anti-patterns are explicitly documented because preventing invalid
designs is as important as defining valid ones.

------------------------------------------------------------------------

## 19.2 Principle

Every anti-pattern violates at least one constitutional property:

-   semantic clarity,
-   temporal legality,
-   reproducibility,
-   lineage,
-   observability,
-   governance.

------------------------------------------------------------------------

## 19.3 Mixing semantic layers

Illegal:

``` text
Feature + Outcome
State + Reward
Decision + Representation
```

Each object belongs to exactly one ontological layer.

------------------------------------------------------------------------

## 19.4 Feature-driven strategy contamination

Illegal:

``` text
Rename a feature because a strategy uses it.

Modify a feature to improve one model.
```

Features describe markets, not strategies.

------------------------------------------------------------------------

## 19.5 Hidden future information

Illegal examples:

``` text
Future close
Future spread
Future return
Future label
```

Any dependence on future observations invalidates the State.

------------------------------------------------------------------------

## 19.6 Vendor semantics

Raw vendor fields shall never be consumed directly by canonical
representations.

Every vendor-specific concept must first become a canonical primitive.

------------------------------------------------------------------------

## 19.7 Duplicate semantics

Different names shall not describe the same concept.

Likewise, the same canonical name shall never describe two different
concepts.

Semantic uniqueness is mandatory.

------------------------------------------------------------------------

## 19.8 Feature explosion without governance

Generating thousands of engineered variables without:

-   registry,
-   formula,
-   version,
-   lineage,

creates an unusable research system.

Feature quantity never replaces feature governance.

------------------------------------------------------------------------

## 19.9 States as data dumps

A State is not a container for every available variable.

Only observable, relevant and governed representations may enter a
State.

------------------------------------------------------------------------

## 19.10 Outcome contamination

Outcomes may evaluate States.

Outcomes may never define States.

This rule has no exceptions.

------------------------------------------------------------------------

## 19.11 Silent semantic drift

Changing:

-   mathematical definition,
-   units,
-   normalization,
-   interpretation,

without creating a new semantic version is forbidden.

------------------------------------------------------------------------

## 19.12 Hidden dependencies

Every dependency shall be explicit.

Implicit transformations, undocumented preprocessing and hidden
assumptions are architecturally invalid.

------------------------------------------------------------------------

## 19.13 Overfitting the architecture

The representation system shall never be redesigned merely because one
strategy, one model or one experiment performs better.

Architecture must remain strategy-independent.

------------------------------------------------------------------------

## 19.14 Constitutional rule

Whenever an implementation choice conflicts with the representation
principles of TSIS, the implementation shall change.

The architecture is authoritative.

Performance is never sufficient justification for violating
architectural correctness.
