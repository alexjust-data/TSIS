# TSIS Event Research Architecture

## Chapter 5 --- Event Windows

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 5. Purpose

An Event defines **what** occurred.

An Event Window defines **which observable states belong to the
scientific investigation of that Event**.

Without governed Event Windows, evidence collection becomes
inconsistent, outcomes become incomparable and research loses
reproducibility.

------------------------------------------------------------------------

# 5.1 Fundamental Principle

Events are instantaneous anchors.

Research is performed over windows.

``` text
Event
    ↓
Event Window
    ↓
States
    ↓
Evidence
```

Every canonical Event shall own one or more governed Event Windows.

------------------------------------------------------------------------

# 5.2 Definition

An Event Window is a deterministic temporal interval anchored to a
canonical Event and governed by explicit policies defining:

-   start
-   end
-   eligibility
-   state roles
-   outcome boundaries

The Event Window---not the Event---is the unit from which observable
States are collected.

------------------------------------------------------------------------

# 5.3 Why Event Windows Exist

The same Event may be investigated from multiple perspectives.

Examples:

``` text
30 minutes before
5 minutes before
Anchor instant
30 seconds after
30 minutes after
Next regular session
```

Each window answers a different scientific question.

------------------------------------------------------------------------

# 5.4 Canonical Window Types

## Pre-Event

Characterizes observable conditions before the anchor.

Examples:

``` text
Pre-30m
Pre-5m
Pre-30s
```

Purpose: describe the environment leading to the Event.

## Anchor Window

Captures the Event itself.

Purpose: describe the transition.

## Immediate Response

Examples:

``` text
0–30s
0–5m
```

Purpose: measure immediate market reaction.

## Extended Response

Examples:

``` text
30m
1 session
5 sessions
```

Purpose: study longer-term consequences.

## Control Window

Matched windows without the target Event.

Purpose: estimate baseline behaviour.

------------------------------------------------------------------------

# 5.5 Event Window Roles

Examples:

``` text
pre_event
anchor
response
extended_response
control
replication
```

Roles describe research intent rather than chronology alone.

------------------------------------------------------------------------

# 5.6 State Membership

``` text
Event
      ↓
Event Window
      ↓
Decision Timestamps
      ↓
Event States
```

The Event State Builder consumes Event Windows rather than raw Events.

------------------------------------------------------------------------

# 5.7 Window Metadata

``` text
event_window_id
event_id
window_role
anchor_timestamp
window_start
window_end
population_id
lookback_policy
coverage_policy
builder_version
```

------------------------------------------------------------------------

# 5.8 Window Independence

Changing one Event Window does not modify:

-   Event identity
-   Event Family
-   Event Population

It creates a new observational context only.

------------------------------------------------------------------------

# 5.9 Window Versioning

Changing duration, anchor definition, role, eligibility or quality
policy creates a new Event Window version.

Historical windows remain immutable.

------------------------------------------------------------------------

# 5.10 Constitutional Rule

Scientific observation inside TSIS is performed over governed Event
Windows rather than isolated Events.

Every Event State, Outcome and Phenomenon shall reference explicit Event
Windows whose construction is deterministic, reproducible and version
controlled.
