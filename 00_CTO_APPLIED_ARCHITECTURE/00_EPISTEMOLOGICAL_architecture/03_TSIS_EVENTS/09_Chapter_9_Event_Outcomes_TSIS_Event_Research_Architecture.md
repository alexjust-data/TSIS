# TSIS Event Research Architecture

## Chapter 9 --- Event Outcomes

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 9. Purpose

Events organize observation.

Event States describe what was observable.

Event Outcomes evaluate what happened after the Event.

Event Outcomes therefore close the scientific loop between observation
and empirical validation.

------------------------------------------------------------------------

# 9.1 Fundamental Principle

Event Outcomes never describe the Event itself.

They describe the consequences observed after a governed Event Window.

``` text
Event
      ↓
Event Window
      ↓
Event State
      ↓
Event Outcome
```

Outcomes belong to evaluation, not representation.

------------------------------------------------------------------------

# 9.2 Definition

An Event Outcome is a deterministic measurement computed after the Event
anchor according to an explicit outcome protocol.

Its purpose is to evaluate research hypotheses rather than generate
trading signals.

------------------------------------------------------------------------

# 9.3 Outcome Families

Typical Event Outcome families include:

``` text
Price Outcomes
Microstructure Outcomes
Execution Outcomes
Risk Outcomes
Phenomenon Outcomes
```

Examples:

``` text
Future Return
MFE
MAE
Time to Target
Time to Failure
Spread Evolution
Liquidity Recovery
Second Halt
```

------------------------------------------------------------------------

# 9.4 Outcome Horizons

Every Event Outcome shall define an explicit evaluation horizon.

Examples:

``` text
30 seconds
5 minutes
30 minutes
End of Session
Next Session
```

Changing the horizon creates a distinct canonical outcome.

------------------------------------------------------------------------

# 9.5 Inputs

Event Outcomes may consume only observations that occur strictly after
the Event anchor.

They never participate in:

-   Feature construction
-   Representation
-   Market State
-   Event State

------------------------------------------------------------------------

# 9.6 Outcome Metadata

Every Event Outcome shall expose:

``` text
event_outcome_id
event_id
event_window_id
anchor_timestamp
evaluation_start
evaluation_end
outcome_family
builder_version
quality_state
```

------------------------------------------------------------------------

# 9.7 Population Consistency

Outcome populations must exactly match the Event Population being
evaluated.

Missing or censored outcomes shall be explicitly documented.

------------------------------------------------------------------------

# 9.8 Outcome Lineage

Every Event Outcome shall remain traceable to:

``` text
Event
Event Window
Event State
Outcome Builder
Validation Protocol
```

------------------------------------------------------------------------

# 9.9 Event Outcome versus Knowledge

Outcomes provide evidence.

Knowledge interprets that evidence.

``` text
Event Outcomes
        ↓
Evidence
        ↓
Phenomenon
        ↓
Knowledge
```

No single outcome establishes a phenomenon.

------------------------------------------------------------------------

# 9.10 Constitutional Rule

Event Outcomes are evaluation objects.

They are temporally downstream from Event States and shall never
influence representations, features or states intended for decision
making.

Their exclusive purpose is to support reproducible scientific
validation.
