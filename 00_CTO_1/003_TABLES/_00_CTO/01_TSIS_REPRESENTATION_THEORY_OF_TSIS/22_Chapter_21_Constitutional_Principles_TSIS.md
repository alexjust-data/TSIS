# TSIS Market Representation Architecture

## Chapter 21 --- Constitutional Principles

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 21. Constitutional Principles

## 21.1 Purpose

This chapter defines the permanent architectural principles that govern
every present and future component of TSIS.

Unlike implementation documents, these principles are intended to remain
stable over the lifetime of the project.

Whenever a lower-level contract conflicts with one of these principles,
the constitutional principle prevails.

------------------------------------------------------------------------

# 21.2 Principle 1 --- Market before Strategy

TSIS exists to represent the market.

Strategies consume that representation.

The representation shall never be redesigned merely to improve one
strategy.

``` text
Market
    ↓
Representation
    ↓
Research
    ↓
Strategies
```

------------------------------------------------------------------------

# 21.3 Principle 2 --- Observation before Prediction

Prediction begins only after the observable market has been represented.

No predictive model may redefine the observable layer.

------------------------------------------------------------------------

# 21.4 Principle 3 --- Representation before Intelligence

Machine learning, reinforcement learning, optimisation and evolutionary
search are consumers of representations.

Representations remain independent of every intelligence system.

------------------------------------------------------------------------

# 21.5 Principle 4 --- Temporal Integrity

Every object intended for decision making shall be constructed
exclusively from information observable at or before the declared
decision timestamp.

Temporal legality is mandatory.

------------------------------------------------------------------------

# 21.6 Principle 5 --- Reproducibility

Every canonical result shall be reproducible from:

-   identical raw inputs,
-   identical contracts,
-   identical builders,
-   identical versions.

Scientific claims without reproducibility are not part of TSIS.

------------------------------------------------------------------------

# 21.7 Principle 6 --- Semantic Stability

Canonical meanings evolve through explicit versioning.

Implementations may change.

Semantics shall not drift silently.

------------------------------------------------------------------------

# 21.8 Principle 7 --- Layer Separation

The following layers remain independent:

``` text
Observation
Primitive
Feature
Representation
State
Decision
Outcome
```

No layer may assume the responsibility of another.

------------------------------------------------------------------------

# 21.9 Principle 8 --- Governance

Every canonical object must possess:

-   documented semantics,
-   lineage,
-   version,
-   ownership,
-   validation,
-   registry entry when applicable.

Undocumented objects cannot become constitutional components.

------------------------------------------------------------------------

# 21.10 Principle 9 --- Scientific Neutrality

The representation architecture stores measurements rather than beliefs.

TSIS records observable market properties.

Research evaluates hypotheses.

Strategies exploit validated knowledge.

The architecture itself remains neutral.

------------------------------------------------------------------------

# 21.11 Principle 10 --- Evolution through Extension

TSIS shall evolve by extending existing concepts rather than replacing
them.

New datasets, feature families, state surfaces and learning systems
should integrate into the established ontology whenever possible.

Architectural continuity has priority over short-term implementation
convenience.

------------------------------------------------------------------------

# 21.12 Constitutional statement

These principles constitute the highest architectural authority within
TSIS.

All future contracts, schemas, builders, datasets, registries, feature
families, state surfaces and learning systems shall remain compatible
with them.

Any future proposal that violates these principles must either:

1.  be rejected, or
2.  explicitly revise the constitutional architecture through a new
    major version.

No lower-level document may override this chapter.
