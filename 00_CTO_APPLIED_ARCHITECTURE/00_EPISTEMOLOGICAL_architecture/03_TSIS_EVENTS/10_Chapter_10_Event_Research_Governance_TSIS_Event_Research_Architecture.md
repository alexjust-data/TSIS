# TSIS Event Research Architecture

## Chapter 10 --- Event Research Governance

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 10. Purpose

Event Research Governance defines the institutional rules governing how
Events become scientific research objects inside TSIS.

The objective is to guarantee that every Event Population, Event Window,
Event State and Event Outcome is created, promoted and consumed through
reproducible, auditable and version-controlled processes.

Events are the bridge between representation and scientific discovery.

Governance ensures that this bridge remains scientifically trustworthy.

------------------------------------------------------------------------

# 10.1 Fundamental Principle

No Event becomes a canonical research object merely because it appears
interesting.

Canonical Event Families, Event Populations and Event Windows are
promoted only after satisfying explicit governance requirements.

Scientific curiosity creates candidates.

Governance creates institutional knowledge.

------------------------------------------------------------------------

# 10.2 Governance Hierarchy

``` text
Ontology
    ↓
Event Taxonomy
    ↓
Event Families
    ↓
Detection Contracts
    ↓
Event Candidates
    ↓
Event Populations
    ↓
Event Windows
    ↓
Event States
    ↓
Evidence
    ↓
Phenomenon Discovery
```

Each layer constrains the next.

------------------------------------------------------------------------

# 10.3 Governance Responsibilities

Every governed Event object shall define:

-   semantic definition,
-   eligibility policy,
-   timestamp policy,
-   population policy,
-   window policy,
-   quality policy,
-   version,
-   lineage.

Undocumented Event objects shall never become canonical.

------------------------------------------------------------------------

# 10.4 Promotion Path

Typical lifecycle:

``` text
Experimental Detector
        ↓
Candidate Event
        ↓
Research Event
        ↓
Canonical Event Family
```

Promotion requires:

-   deterministic detection,
-   reproducibility,
-   documented semantics,
-   validator support,
-   governance approval.

------------------------------------------------------------------------

# 10.5 Event Registry

Every canonical Event shall be registered.

Minimum registry fields:

``` text
event_id
canonical_name
event_family
event_type
eligibility_policy
window_policy
population_policy
builder_version
taxonomy_version
status
```

The Event Registry is the authoritative catalogue of research anchors.

------------------------------------------------------------------------

# 10.6 Versioning

Changes to:

-   eligibility,
-   anchor definition,
-   population,
-   windows,
-   semantics,

shall create new Event versions.

Historical Event populations remain reproducible.

------------------------------------------------------------------------

# 10.7 Validation

Before promotion, every Event shall demonstrate:

-   deterministic construction,
-   temporal legality,
-   reproducibility,
-   quality compliance,
-   population integrity.

------------------------------------------------------------------------

# 10.8 Auditability

Every Event shall be traceable to:

``` text
Detection Builder
Source Data
Contracts
Registry
Population
Windows
States
Evidence
```

Scientific conclusions must always be explainable.

------------------------------------------------------------------------

# 10.9 Governance Independence

Governance is independent of:

-   trading profitability,
-   model performance,
-   execution quality,
-   reinforcement learning policies.

Governance protects scientific consistency rather than financial
outcomes.

------------------------------------------------------------------------

# 10.10 Constitutional Rule

Event Research Governance is the constitutional control layer connecting
market representation with scientific discovery.

No Event shall become a canonical research anchor without explicit
semantic definition, deterministic construction, reproducible validation
and documented governance.

Architectural integrity always takes precedence over convenience.

------------------------------------------------------------------------

# Closing Remarks

With this chapter, the **TSIS Event Research Architecture** becomes
complete.

It establishes:

1.  What an Event is.
2.  How Events are classified.
3.  How Event Families are defined.
4.  How Event Populations are constructed.
5.  How Event Windows govern observation.
6.  How Event Geometry organizes observable structure.
7.  How Event Candidates are detected.
8.  How Event States are built.
9.  How Event Outcomes evaluate evidence.
10. How the entire Event Research process is governed.

This architecture forms the missing bridge between:

``` text
Market Representation
        ↓
Event Research
        ↓
Phenomenon Discovery
        ↓
Knowledge
        ↓
Strategies
```

TSIS therefore progresses from describing the market, to organizing
scientific observation, to discovering validated knowledge, before any
strategy is ever designed.
