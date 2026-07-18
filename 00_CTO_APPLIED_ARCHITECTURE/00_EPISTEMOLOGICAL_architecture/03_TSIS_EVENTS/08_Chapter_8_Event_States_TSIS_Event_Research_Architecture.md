# TSIS Event Research Architecture

## Chapter 8 --- Event States

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 8. Purpose

Event Candidates identify **where** research may begin.

Event Windows define **when** observations are collected.

Event States define **what was observable** inside those governed
windows.

An Event State is therefore the canonical observational object used by
scientific research.

------------------------------------------------------------------------

# 8.1 Fundamental Principle

An Event State is **not** an Event.

An Event State is **not** a Strategy.

An Event State is **not** an Outcome.

It is a Market State anchored to a governed Event Window.

``` text
Market State
      +
Event Window
      +
State Role
      ↓
Event State
```

------------------------------------------------------------------------

# 8.2 Definition

An Event State is a temporally legal market state associated with one
Event Window, one decision timestamp and one semantic role.

Its purpose is to provide a reproducible description of the observable
market surrounding an Event.

------------------------------------------------------------------------

# 8.3 Why Event States Exist

Market States answer:

> What was observable?

Event States answer:

> What was observable around this Event?

The Event State introduces research context without modifying the
underlying representation.

------------------------------------------------------------------------

# 8.4 Event State Roles

Typical roles include:

``` text
pre_event

anchor

confirmation

response

extended_response

control

replication
```

Roles define observational intent.

They do not imply profitability.

------------------------------------------------------------------------

# 8.5 Inputs

Every Event State consumes:

-   Market State
-   Event Window
-   Event metadata
-   State role

It never consumes:

-   outcomes
-   rewards
-   future labels
-   decisions

------------------------------------------------------------------------

# 8.6 Event State Metadata

Every Event State shall expose:

``` text
event_state_id
event_id
event_window_id
market_state_id
decision_timestamp
state_role
population_id
representation_versions
state_version
builder_version
quality_state
```

------------------------------------------------------------------------

# 8.7 Event State Independence

The same Market State may participate in multiple Event States if
different Event Windows reference it.

Likewise, changing Event Windows never modifies the underlying Market
State.

------------------------------------------------------------------------

# 8.8 Event State Lineage

Every Event State shall remain traceable to:

``` text
Event Family
Event Population
Event Window
Market State
Feature Registry
Representation Versions
```

Lineage is mandatory.

------------------------------------------------------------------------

# 8.9 Event State versus Outcome

Event States describe only observable information.

Outcomes evaluate what occurred afterwards.

``` text
Event State
      ↓
Research
      ↓
Outcome
```

The reverse dependency is forbidden.

------------------------------------------------------------------------

# 8.10 Constitutional Rule

Event States are the canonical observational unit of Event Research.

Every Phenomenon, Evidence Collection and Knowledge Object shall
reference governed Event States rather than raw Events, ensuring
reproducibility, temporal legality and scientific consistency.
