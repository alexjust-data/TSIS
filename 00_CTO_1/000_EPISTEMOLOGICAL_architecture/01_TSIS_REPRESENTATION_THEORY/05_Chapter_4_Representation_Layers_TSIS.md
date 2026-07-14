# TSIS Market Representation Architecture

## Chapter 4 --- Representation Layers

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 4. Representation Layers

## 4.1 Purpose

The TSIS architecture is organized as successive representation layers.

Each layer has one responsibility only.

No layer may assume responsibilities that belong to another.

The objective is to maximize semantic clarity, reproducibility and
long-term maintainability.

------------------------------------------------------------------------

# 4.2 Layer hierarchy

``` text
Reality
    ↓
Observation Layer
    ↓
Primitive Layer
    ↓
Feature Layer
    ↓
Representation Layer
    ↓
State Layer
    ↓
Decision Layer
    ↓
Outcome Layer
```

Each layer consumes only the immediately preceding semantic layer.

------------------------------------------------------------------------

# 4.3 Observation Layer

Purpose:

Capture reality without interpretation.

Examples:

``` text
Trade
Quote
News
SEC Filing
Halt
Corporate Action
```

Characteristics:

-   vendor dependent
-   immutable
-   timestamped
-   noisy
-   incomplete by nature

The Observation Layer preserves evidence.

It does not create knowledge.

------------------------------------------------------------------------

# 4.4 Primitive Layer

Purpose:

Transform heterogeneous observations into canonical objects.

Examples:

``` text
Canonical Trade Primitive
Canonical Quote Primitive
Canonical Daily Bar
Canonical 1m Bar
Canonical Halt
```

Responsibilities:

-   normalization
-   canonical timestamps
-   canonical identifiers
-   quality flags
-   lineage

Primitives are still descriptive.

They never perform inference.

------------------------------------------------------------------------

# 4.5 Feature Layer

Purpose:

Describe measurable properties of primitives.

Examples:

``` text
Spread
Trade Count Rate
Microprice
OFI
ATR
Gap
Distance to VWAP
```

Responsibilities:

-   mathematical transformations
-   multi-window aggregation
-   normalization
-   statistical descriptors
-   feature families

Features remain local properties.

They do not describe the market as a whole.

------------------------------------------------------------------------

# 4.6 Representation Layer

Purpose:

Organize related features into coherent semantic domains.

Examples:

``` text
Microstructure Representation

Intraday Representation

Daily Representation

Fundamental Representation

News Representation

Regime Representation
```

Representations are domain models.

Each representation owns one portion of market knowledge.

------------------------------------------------------------------------

# 4.7 State Layer

Purpose:

Merge multiple representations into a complete observable snapshot.

Examples:

``` text
Market State

Event State

Strategy State

Execution State

Position State
```

The State Layer answers:

``` text
What is observable now?
```

States must remain:

-   temporally legal
-   reproducible
-   consumer independent

------------------------------------------------------------------------

# 4.8 Decision Layer

Purpose:

Transform states into actions.

Examples:

``` text
Enter

Exit

Hold

Scale In

Scale Out
```

The Decision Layer belongs to strategies, policies and learning systems.

It is intentionally separated from market representation.

------------------------------------------------------------------------

# 4.9 Outcome Layer

Purpose:

Evaluate consequences.

Examples:

``` text
Future Return

MFE

MAE

Execution Cost

Breakout Success

Halt

Realized Spread
```

Outcomes answer:

``` text
What happened afterwards?
```

Outcomes never contribute to state construction.

------------------------------------------------------------------------

# 4.10 Layer independence

Each layer must be independently replaceable.

Changing:

-   a feature,
-   a model,
-   a strategy,
-   a broker,
-   a data vendor,

must not invalidate higher architectural principles.

------------------------------------------------------------------------

# 4.11 Information flow

Legal flow:

``` text
Observation
    ↓
Primitive
    ↓
Feature
    ↓
Representation
    ↓
State
    ↓
Decision
    ↓
Outcome
```

Illegal shortcuts:

``` text
Observation → Decision

Primitive → Outcome

Outcome → Feature

Outcome → State

Decision → Representation
```

------------------------------------------------------------------------

# 4.12 Architectural responsibilities

  Layer            Responsibility
  ---------------- -----------------------
  Observation      Capture evidence
  Primitive        Normalize evidence
  Feature          Measure properties
  Representation   Organize knowledge
  State            Describe the market
  Decision         Select actions
  Outcome          Evaluate consequences

------------------------------------------------------------------------

# 4.13 Constitutional rule

Every future TSIS component must declare explicitly:

-   which layer it belongs to,
-   which layer it consumes,
-   which layer it produces.

Components that violate this layering are architecturally invalid
regardless of implementation quality.

The representation hierarchy is mandatory throughout TSIS.
